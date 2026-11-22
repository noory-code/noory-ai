"""Audit checks for model and effort tiers (`docs/SCHEMA_V5.md` → Model and effort tiers).

Codes:
- TIER001 (error): `model_tiers` / `tier_routing` is invalid.
- TIER002 (error): a current card names a tier the settings do not declare.
- TIER003 (warning): the latest driver round for a current card ran on other values than the
  card's tier gives now, or its command did not read STAGE_MODEL / STAGE_EFFORT.
- TIER004 (warning): a subagent that ran for current cards used another model or effort than
  their tier gives; a stated over-tier reason is quoted.
- TIER005 (warning): a model-usage record line could not be read.
- TIER006 (error): `model_fallbacks` / `usage_limit_patterns` is invalid.

Only cards in the current work zone are compared: archived history is not re-judged. Without
`model_tiers` no card may carry a tier, and nothing else is checked.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Union

STAGE_ROOT = Path(__file__).resolve().parents[1]
if str(STAGE_ROOT / "hooks") not in sys.path:
    sys.path.insert(0, str(STAGE_ROOT / "hooks"))

from stage_model_tiers import (  # noqa: E402
    TierConfig,
    model_matches,
    parse_fallback_config,
    parse_tier_config,
)
from stage_record_paths import record_path  # noqa: E402

WORK_LOG_DIR = Path(".runtime") / "driver" / "logs"
USAGE_DIR = Path(".runtime") / "model-usage"
MODEL_TIER_LINE = re.compile(r"^Model tier \(JSON\): (.+)$", re.MULTILINE)
AGENT_VENUE = "claude"

# Evaluated at import time, so no `X | Y` syntax: Stage runs on Python 3.9.
Report = Callable[[str, str, Union[Path, str]], None]


def _expected(config: TierConfig, tier: str, venue: str) -> tuple[str, str]:
    values = config.values(tier, venue)
    return (values.model, values.effort) if values else ("", "")


def _audit_driver_round(
    config: TierConfig, card_id: str, tier: str, log: Path, warn: Report
) -> None:
    try:
        text = log.read_text(encoding="utf-8")
    except OSError:
        return
    lines = MODEL_TIER_LINE.findall(text)
    if not lines:
        return
    try:
        record = json.loads(lines[-1])
    except json.JSONDecodeError:
        warn("TIER005", f"{card_id}: the latest driver model-tier line is not JSON.", log)
        return
    if not isinstance(record, dict):
        return
    ran_tier = str(record.get("tier") or "")
    if ran_tier != tier:
        warn(
            "TIER003",
            f"{card_id}: the latest driver round ran on tier `{ran_tier}`, but the card now "
            f"says `{tier}`.",
            log,
        )
    for role in ("executor", "reviewer"):
        values = record.get(role)
        if not isinstance(values, dict):
            continue
        venue = str(values.get("venue") or "")
        model, effort = _expected(config, tier, venue)
        got_model = str(values.get("model") or "")
        got_effort = str(values.get("effort") or "")
        if (got_model, got_effort) != (model, effort):
            warn(
                "TIER003",
                f"{card_id}: the {role} ({venue}) received model `{got_model or '-'}` / effort "
                f"`{got_effort or '-'}`; tier `{tier}` gives `{model or '-'}` / `{effort or '-'}`.",
                log,
            )
        for key, variable, expected in (
            ("command_uses_model_env", "STAGE_MODEL", model),
            ("command_uses_effort_env", "STAGE_EFFORT", effort),
        ):
            if expected and values.get(key) is False:
                warn(
                    "TIER003",
                    f"{card_id}: the {role} ({venue}) command does not read ${variable}, so it "
                    f"ran on its own value instead of tier `{tier}`'s `{expected}`.",
                    log,
                )


def _usage_records(stage_root: Path, warn: Report) -> list[dict[str, Any]]:
    folder = stage_root / USAGE_DIR
    records: list[dict[str, Any]] = []
    if not folder.is_dir():
        return records
    for path in sorted(folder.glob("*.jsonl")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            warn("TIER005", "Model-usage records could not be read.", path)
            continue
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                warn("TIER005", f"Model-usage line {number} is not JSON; it was skipped.", path)
                continue
            if isinstance(record, dict):
                records.append({**record, "_path": path})
    return records


def _audit_subagents(
    config: TierConfig, card_tiers: dict[str, str], stage_root: Path, warn: Report
) -> None:
    records = _usage_records(stage_root, warn)
    reasons = {
        str(record.get("agent_id")): str(record.get("over_tier_reason") or "")
        for record in records
        if record.get("event") == "agent_requested" and record.get("agent_id")
    }
    for record in records:
        if record.get("event") != "agent_finished":
            continue
        cards = [card for card in record.get("cards") or [] if card in card_tiers]
        if not cards:
            continue
        tiers = {card_tiers[card] for card in cards}
        actual_model = str(record.get("model") or "")
        actual_effort = str(record.get("effort") or "")
        agent = str(record.get("agent_id") or "?")
        reason = reasons.get(agent, "")
        because = f" Stated reason: {reason}." if reason else ""
        names = ", ".join(cards)
        if len(tiers) != 1:
            ceiling = max(tiers, key=lambda tier: config.rank(tier) or 0)
            rank = config.model_rank(AGENT_VENUE, actual_model) if actual_model else None
            if actual_model and (rank is None or rank > (config.rank(ceiling) or 0)):
                warn(
                    "TIER004",
                    f"{names}: subagent {agent} ran on `{actual_model}`, costlier than the "
                    f"highest current tier `{ceiling}`.{because}",
                    record["_path"],
                )
            continue
        tier = next(iter(tiers))
        model, effort = _expected(config, tier, AGENT_VENUE)
        if model and actual_model and not model_matches(model, actual_model):
            warn(
                "TIER004",
                f"{names}: subagent {agent} ran on model `{actual_model}`; tier `{tier}` gives "
                f"`{model}`.{because}",
                record["_path"],
            )
        if effort and actual_effort and actual_effort != effort:
            warn(
                "TIER004",
                f"{names}: subagent {agent} ran on effort `{actual_effort}`; tier `{tier}` gives "
                f"`{effort}`.{because}",
                record["_path"],
            )


def audit_model_tiers(
    stage_root: Path,
    settings: Any,
    settings_path: Path | str,
    current_cards: list[tuple[str, str, Path]],
    error: Report,
    warning: Report,
) -> None:
    """Run every tier check; `current_cards` holds (id, tier, path) for current-zone cards."""

    for message in parse_fallback_config(settings).errors:
        error("TIER006", f"Model fallback settings are invalid: {message}.", settings_path)
    config = parse_tier_config(settings)
    for message in config.errors:
        error("TIER001", f"Model tier settings are invalid: {message}.", settings_path)
    if config.errors:
        return
    card_tiers: dict[str, str] = {}
    for card_id, tier, path in current_cards:
        if not tier:
            continue
        if config.tiers is None:
            error(
                "TIER002",
                f"{card_id} names tier `{tier}`, but settings declare no model_tiers.",
                path,
            )
        elif config.rank(tier) is None:
            error(
                "TIER002",
                f"{card_id} names tier `{tier}`, which model_tiers does not declare "
                f"(declared: {sorted(config.tiers)}).",
                path,
            )
        else:
            card_tiers[card_id] = tier
    if config.tiers is None:
        return
    for card_id, tier in card_tiers.items():
        _audit_driver_round(
            config, card_id, tier, record_path(stage_root / WORK_LOG_DIR, card_id), warning
        )
    _audit_subagents(config, card_tiers, stage_root, warning)
