"""Keep Claude Code Agent calls on the current card's model and effort tier.

Before an `Agent` call (PreToolUse), a missing `model` or `effort` is filled
from the current card's tier, and a model that costs more than that tier is
denied unless the call's `description` carries `[over-tier: <reason>]`.
After the call (PostToolUse) the requested values and reason are recorded
with the subagent's id, and when any subagent stops (SubagentStop, foreground
or background) the model and effort it actually ran with are recorded, both
in `.stage/.runtime/model-usage/<session>.jsonl`, for the audit to compare
with the card.

The current cards are the ones `stage_guard.active_work_chains` selects: the
driver's `STAGE_WORK_ITEM_PATH` card, or every open leaf. Only cards with a
`tier:` count. The cost ceiling is the costliest of their tiers; a value is
filled only when they share one tier, because otherwise there is no single
value to fill.

This module never breaks a tool call: without `model_tiers`, without a tiered
card, or on any error it returns no output. It does not apply to Codex, which
has no Agent tool.
"""

# The hook must run wherever `python3` points on a host machine (3.9+).
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_model_tiers import TierConfig, load_tier_config  # noqa: E402
from stage_runtime import runtime_slot_name  # noqa: E402
from stage_work import WorkItem  # noqa: E402

AGENT_TOOL = "Agent"
AGENT_VENUE = "claude"
OVER_TIER_RE = re.compile(r"\[over-tier:\s*([^\]]*?)\s*\]")
USAGE_DIR = Path(".runtime") / "model-usage"


def _tiered(leaves: list[WorkItem], config: TierConfig) -> list[WorkItem]:
    return [leaf for leaf in leaves if leaf.tier and config.rank(leaf.tier) is not None]


def _ceiling(cards: list[WorkItem], config: TierConfig) -> str:
    return max((card.tier for card in cards), key=lambda tier: config.rank(tier) or 0)


def _over_tier_reason(description: Any) -> str:
    if not isinstance(description, str):
        return ""
    match = OVER_TIER_RE.search(description)
    return match.group(1).strip() if match else ""


def _append_usage(stage_root: Path, session_id: str, record: dict[str, Any]) -> None:
    folder = stage_root / USAGE_DIR
    folder.mkdir(parents=True, exist_ok=True)
    record = {"recorded_at": datetime.now(timezone.utc).isoformat(), **record}
    path = folder / f"{runtime_slot_name(session_id)}.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _deny(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def _tier_table(cards: list[WorkItem], config: TierConfig) -> str:
    parts = []
    for name in sorted({card.tier for card in cards}, key=lambda tier: config.rank(tier) or 0):
        values = config.values(name, AGENT_VENUE)
        shown = f"{values.model or '-'}/{values.effort or '-'}" if values else "no claude values"
        parts.append(f"{name} ({shown})")
    return ", ".join(parts)


def _review_call(
    payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]
) -> dict[str, Any]:
    config = load_tier_config(stage_root)
    if config.tiers is None:
        return {}
    cards = _tiered(leaves, config)
    if not cards:
        return {}
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return {}
    card_ids = [card.item_id for card in cards]
    ceiling = _ceiling(cards, config)
    ceiling_rank = config.rank(ceiling) or 0

    requested = tool_input.get("model")
    over_tier_reason = ""
    if isinstance(requested, str) and requested.strip():
        model_rank = config.model_rank(AGENT_VENUE, requested)
        if model_rank is None or model_rank > ceiling_rank:
            over_tier_reason = _over_tier_reason(tool_input.get("description"))
            if not over_tier_reason:
                return _deny(
                    f"Stage model tier: Agent model `{requested}` costs more than the current "
                    f"card tier `{ceiling}` ({', '.join(card_ids)}; tiers: "
                    f"{_tier_table(cards, config)}). Use a model at or below `{ceiling}`, or, "
                    "when the task truly needs it, add `[over-tier: <reason>]` to the "
                    "description; the reason is recorded for the audit."
                )

    missing = [
        key
        for key in ("model", "effort")
        if not (isinstance(tool_input.get(key), str) and tool_input.get(key, "").strip())
    ]
    tiers = {card.tier for card in cards}
    if missing and len(tiers) != 1:
        return _deny(
            f"Stage model tier: the open cards have different tiers "
            f"({_tier_table(cards, config)}), so the missing {' and '.join(missing)} cannot "
            "be filled. Pass model and effort explicitly for this Agent call; the costliest "
            f"allowed tier is `{ceiling}`."
        )
    if over_tier_reason:
        session_id = str(payload.get("session_id") or "")
        _append_usage(
            stage_root,
            session_id,
            {
                "event": "over_tier_allowed",
                "session_id": session_id,
                "tool_use_id": str(payload.get("tool_use_id") or ""),
                "cards": card_ids,
                "tier": ceiling,
                "model": str(requested).strip(),
                "reason": over_tier_reason,
            },
        )
    if not missing:
        return {}
    tier = next(iter(tiers))
    values = config.values(tier, AGENT_VENUE)
    filled = {
        key: value
        for key, value in (
            ("model", values.model if values else ""),
            ("effort", values.effort if values else ""),
        )
        if key in missing and value
    }
    if not filled:
        return {}
    shown = ", ".join(f"{key}={value}" for key, value in filled.items())
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, **filled},
            "additionalContext": (
                f"Stage filled this Agent call from card tier `{tier}` "
                f"({', '.join(card_ids)}): {shown}."
            ),
        }
    }


def review_agent_call(
    payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]
) -> dict[str, Any]:
    """PreToolUse output for an Agent call, or {} for no opinion."""

    try:
        return _review_call(payload, stage_root, leaves)
    except Exception:  # noqa: BLE001 - an advisory hook must never break the call
        return {}


def _transcript_values(agent_transcript: Path) -> tuple[str, str]:
    """(model, effort) of the subagent's last model request, or ("", "").

    SubagentStop can fire before the final assistant line is written, so the
    request line that precedes each reply (`api-request`: `params.model`,
    `params.output_config.effort`) is read as well; an assistant line
    (`message.model`, `effort`) overrides it when present.
    """

    if not agent_transcript.is_file():
        return "", ""
    model = effort = ""
    for line in agent_transcript.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "api-request":
            params = entry.get("params")
            if isinstance(params, dict):
                if isinstance(params.get("model"), str):
                    model = params["model"]
                output = params.get("output_config")
                if isinstance(output, dict) and isinstance(output.get("effort"), str):
                    effort = output["effort"]
        elif entry.get("type") == "assistant":
            message = entry.get("message")
            if isinstance(message, dict) and isinstance(message.get("model"), str):
                model = message["model"]
            if isinstance(entry.get("effort"), str):
                effort = entry["effort"]
    return model, effort


def _card_fields(cards: list[WorkItem], config: TierConfig) -> dict[str, Any]:
    tiers = {card.tier for card in cards}
    return {
        "cards": [card.item_id for card in cards],
        "tier": next(iter(tiers)) if len(tiers) == 1 else "",
        "ceiling": _ceiling(cards, config),
    }


def _tiered_cards(stage_root: Path, leaves: list[WorkItem]) -> tuple[TierConfig, list[WorkItem]]:
    config = load_tier_config(stage_root)
    if config.tiers is None:
        return config, []
    return config, _tiered(leaves, config)


def _record_request(payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]) -> None:
    config, cards = _tiered_cards(stage_root, leaves)
    if not cards:
        return
    response = payload.get("tool_response")
    if not isinstance(response, dict) or not response.get("agentId"):
        return
    tool_input = payload.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    session_id = str(payload.get("session_id") or "")
    _append_usage(
        stage_root,
        session_id,
        {
            "event": "agent_requested",
            "session_id": session_id,
            "tool_use_id": str(payload.get("tool_use_id") or ""),
            "agent_id": str(response["agentId"]),
            "status": str(response.get("status") or ""),
            **_card_fields(cards, config),
            "requested_model": str(tool_input.get("model") or ""),
            "requested_effort": str(tool_input.get("effort") or ""),
            "over_tier_reason": _over_tier_reason(tool_input.get("description")),
        },
    )


def _record_finish(payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]) -> None:
    config, cards = _tiered_cards(stage_root, leaves)
    if not cards:
        return
    agent_id = str(payload.get("agent_id") or "")
    if not agent_id:
        return
    transcript = payload.get("agent_transcript_path")
    model, transcript_effort = (
        _transcript_values(Path(transcript))
        if isinstance(transcript, str) and transcript
        else ("", "")
    )
    effort_field = payload.get("effort")
    effort = (
        effort_field.get("level")
        if isinstance(effort_field, dict) and isinstance(effort_field.get("level"), str)
        else transcript_effort
    )
    session_id = str(payload.get("session_id") or "")
    _append_usage(
        stage_root,
        session_id,
        {
            "event": "agent_finished",
            "session_id": session_id,
            "agent_id": agent_id,
            "agent_type": str(payload.get("agent_type") or ""),
            **_card_fields(cards, config),
            "model": model,
            "effort": effort,
        },
    )


def record_agent_request(
    payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]
) -> None:
    """PostToolUse: record what an Agent call asked for and why; never raises."""

    try:
        _record_request(payload, stage_root, leaves)
    except Exception:  # noqa: BLE001 - an advisory hook must never break the call
        return


def record_agent_finish(
    payload: dict[str, Any], stage_root: Path, leaves: list[WorkItem]
) -> None:
    """SubagentStop: record the model and effort the subagent ran with; never raises."""

    try:
        _record_finish(payload, stage_root, leaves)
    except Exception:  # noqa: BLE001 - an advisory hook must never break the call
        return
