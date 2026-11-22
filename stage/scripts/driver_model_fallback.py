#!/usr/bin/env python3
"""Run one role's turn again on the venue's next model when a usage limit stops it.

A venue that offers several models can stop one of them on a usage limit while
the others still run. Reading that as a failed attempt, or as the whole venue
being down, sends the card to the wrong place. This module runs the turn, asks
`stage_model_tiers` whether the output is a usage limit, and if so runs the
same turn again with `STAGE_MODEL` set to the next unspent model group's first
model. The reruns stay inside the one turn, so they never count as attempts.
When every group is spent, the result carries `USAGE_LIMITS_EXHAUSTED_MARKER`
so each driver can stop and say so.

This module never imports `close_work.py`: `close_work.py` imports it for the
close review (`docs/BLUEPRINT.md`).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_environment import MODEL_ENV  # noqa: E402
from stage_model_tiers import load_fallback_config  # noqa: E402

# Lowercase so `driver_review.infrastructure_failure` finds it as written.
USAGE_LIMITS_EXHAUSTED_MARKER = "stage: every model group hit its usage limit"
COMMAND_DEFAULT_MODEL = "(command default)"

RunTurn = Callable[[Dict[str, str]], Tuple[bool, str, str]]


@dataclass
class FallbackRun:
    """One turn's final result plus what the fallback did."""

    ok: bool
    evidence: str
    raw: str
    exhausted: bool = False
    models: list[str] = field(default_factory=list)


def usage_limits_exhausted(output: str) -> bool:
    """Whether a turn's output says every model group hit its usage limit."""

    return USAGE_LIMITS_EXHAUSTED_MARKER in output.lower()


def _shown(model: str) -> str:
    return json.dumps(model or COMMAND_DEFAULT_MODEL, ensure_ascii=False)


def _log_line(log_path: Optional[Path], line: str) -> None:
    if log_path is None:
        return
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n### Driver model\n{line}\n")
    except OSError as exc:
        print(f"WARNING: cannot record model line in work log {log_path}: {exc}")


def run_with_model_fallbacks(
    run: RunTurn,
    *,
    stage_root: Path,
    venue: str,
    role: str,
    command: str,
    env: dict[str, str],
    log_path: Optional[Path],
    before_retry: Optional[Callable[[], None]] = None,
) -> FallbackRun:
    """Run `run(env)` and rerun it on the next model while a usage limit stops it.

    Without `model_fallbacks` or `usage_limit_patterns` for `venue` this is one
    plain call. Otherwise each run adds one `### Driver model` line to the work
    log naming the model, and each usage limit adds one line naming the matched
    pattern and the next model. A usage limit is a non-zero exit whose raw
    output matches a venue pattern. A command that does not name
    `$STAGE_MODEL` cannot change model, so its first usage limit ends the turn
    as exhausted. `before_retry` runs before each rerun, for example to remove
    a partial review verdict.
    """

    config = load_fallback_config(stage_root)
    venue_key = venue.strip().lower()
    if not config.declares(venue_key):
        ok, evidence, raw = run(env)
        return FallbackRun(ok, evidence, raw, models=[env.get(MODEL_ENV, "")])

    current_env = dict(env)
    limited: list[str] = []
    evidences: list[str] = []
    while True:
        model = current_env.get(MODEL_ENV, "")
        _log_line(log_path, f"Model run: {role} on {venue_key} with model {_shown(model)}")
        ok, evidence, raw = run(current_env)
        evidences.append(evidence)
        pattern = "" if ok else config.usage_limit_match(venue_key, raw)
        if not pattern:
            return FallbackRun(ok, "\n".join(evidences), raw, models=[*limited, model])
        limited.append(model)
        next_model = config.next_model(venue_key, limited) if MODEL_ENV in command else ""
        hit = (
            f"Model fallback: {role} model {_shown(model)} on {venue_key} hit a usage limit "
            f"(matched {json.dumps(pattern, ensure_ascii=False)})"
        )
        if next_model:
            _log_line(
                log_path,
                f"{hit}; rerunning with {_shown(next_model)}; the rerun is not an attempt",
            )
            print(f"{hit}; rerunning with {_shown(next_model)}")
            if before_retry is not None:
                before_retry()
            current_env = {**current_env, MODEL_ENV: next_model}
            continue
        why = (
            "every model group in model_fallbacks is spent"
            if MODEL_ENV in command
            else f"the command does not read ${MODEL_ENV}, so it cannot change model"
        )
        tried = ", ".join(_shown(entry) for entry in limited)
        note = f"[{USAGE_LIMITS_EXHAUSTED_MARKER}] {role} on {venue_key}: {why}; tried {tried}"
        _log_line(log_path, f"{hit}; {note}")
        print(note)
        return FallbackRun(
            False,
            "\n".join([*evidences, note]),
            f"{raw}\n{note}",
            exhausted=True,
            models=limited,
        )
