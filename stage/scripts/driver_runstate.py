#!/usr/bin/env python3
"""Remember what a run already did, so an interruption does not repeat it.

The state file is the only thing that survives a killed process. It records how
many attempts an item has spent and which role was mid-flight, which is what
lets a resumed run skip a stage that already finished instead of paying for it
twice.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import ensure_work_log  # noqa: E402
from stage_work import WorkItem  # noqa: E402


def new_run_state(target_id: str, now: float) -> dict[str, Any]:
    return {
        "target": target_id,
        "started_at_unix": now,
        "execution_seconds": 0.0,
        "iteration_count": 0,
        "items": {},
    }


def load_run_state(
    path: Path, target_id: str, now: float
) -> tuple[dict[str, Any] | None, str]:
    """Load runtime state or initialize it in memory without writing."""

    if not path.exists():
        return new_run_state(target_id, now), ""
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"cannot read driver run state: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"driver run state is not valid JSON: {exc}"
    if not isinstance(state, dict):
        return None, "driver run state must be a JSON object"
    if state.get("target") != target_id:
        return None, "driver run state target does not match the requested work item"
    started_at = state.get("started_at_unix")
    if not isinstance(started_at, (int, float)) or isinstance(started_at, bool):
        return None, "driver run state started_at_unix must be a number"
    execution_seconds = state.get("execution_seconds", 0.0)
    if (
        not isinstance(execution_seconds, (int, float))
        or isinstance(execution_seconds, bool)
        or execution_seconds < 0
    ):
        return None, "driver run state execution_seconds must be a non-negative number"
    state["execution_seconds"] = float(execution_seconds)
    iteration_count = state.get("iteration_count")
    if type(iteration_count) is not int or iteration_count < 0:
        return None, "driver run state iteration_count must be a non-negative integer"
    item_states = state.get("items")
    if not isinstance(item_states, dict):
        return None, "driver run state items must be an object"
    for item_id, item_state in item_states.items():
        if not isinstance(item_id, str) or not isinstance(item_state, dict):
            return None, "driver run state item entries must be objects"
        attempt_count = item_state.get("attempt_count")
        fingerprint = item_state.get("last_fingerprint")
        no_change_fingerprint = item_state.get(
            "last_no_change_fingerprint",
            "",
        )
        base_head = item_state.get("base_head", "")
        executor_changed_paths = item_state.get("executor_changed_paths", [])
        running_role = item_state.get("running_role")
        resume_repository_fingerprint = item_state.get(
            "resume_repository_fingerprint",
            "",
        )
        resume_review_changed_paths = item_state.get(
            "resume_review_changed_paths",
            [],
        )
        resume_acceptance_output = item_state.get(
            "resume_acceptance_output",
            [],
        )
        resume_previous_verdict = item_state.get(
            "resume_previous_verdict",
        )
        resume_reasoned_no_change = item_state.get(
            "resume_reasoned_no_change",
            False,
        )
        if type(attempt_count) is not int or attempt_count < 0:
            return None, (
                f"driver run state {item_id}.attempt_count must be a "
                "non-negative integer"
            )
        if not isinstance(fingerprint, str):
            return None, (
                f"driver run state {item_id}.last_fingerprint must be a string"
            )
        if not isinstance(no_change_fingerprint, str):
            return None, (
                f"driver run state {item_id}.last_no_change_fingerprint "
                "must be a string"
            )
        if not isinstance(base_head, str):
            return None, f"driver run state {item_id}.base_head must be a string"
        if (
            not isinstance(executor_changed_paths, list)
            or any(
                not isinstance(changed_path, str) or not changed_path
                for changed_path in executor_changed_paths
            )
            or len(set(executor_changed_paths)) != len(executor_changed_paths)
        ):
            return None, (
                f"driver run state {item_id}.executor_changed_paths must be "
                "an array of unique non-empty strings"
            )
        if running_role not in {None, "executor", "reviewer"}:
            return None, (
                f"driver run state {item_id}.running_role must be "
                "executor, reviewer, or null"
            )
        if not isinstance(resume_repository_fingerprint, str):
            return None, (
                f"driver run state {item_id}.resume_repository_fingerprint "
                "must be a string"
            )
        for field, value in (
            ("resume_review_changed_paths", resume_review_changed_paths),
            ("resume_acceptance_output", resume_acceptance_output),
        ):
            if (
                not isinstance(value, list)
                or any(not isinstance(entry, str) for entry in value)
            ):
                return None, (
                    f"driver run state {item_id}.{field} must be an array of strings"
                )
        if resume_previous_verdict is not None and not isinstance(
            resume_previous_verdict,
            dict,
        ):
            return None, (
                f"driver run state {item_id}.resume_previous_verdict must be "
                "an object or null"
            )
        if type(resume_reasoned_no_change) is not bool:
            return None, (
                f"driver run state {item_id}.resume_reasoned_no_change must be "
                "a boolean"
            )
    return state, ""


def write_run_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically replace one target's untracked runtime state."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    try:
        temporary.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def reset_attempts(
    *,
    state_path: Path,
    stage_root: Path,
    target_id: str,
    item_id: str,
    now: float,
    reason: str,
) -> tuple[bool, str]:
    """Reset one corrected item's attempt budget and record the operator reason."""

    if not state_path.exists():
        return False, f"no driver run state exists for {target_id}"
    state, state_error = load_run_state(state_path, target_id, now)
    if state_error or state is None:
        return False, state_error or "driver run state is unavailable"
    item_state = state["items"].get(item_id)
    if item_state is None:
        return False, f"no recorded attempts exist for {item_id}"
    for running_item_id, running_item_state in state["items"].items():
        if running_item_id == item_id:
            continue
        running_role = running_item_state.get("running_role")
        if running_role is not None:
            return (
                False,
                f"cannot reset attempts while {running_role} is running for "
                f"{running_item_id}",
            )
    if item_state["attempt_count"] == 0:
        return False, f"no recorded attempts exist for {item_id}"

    try:
        log_path = ensure_work_log(stage_root, item_id)
        log_stream = log_path.open("a", encoding="utf-8")
    except (OSError, RuntimeError) as exc:
        return False, str(exc)

    previous_started_at = state["started_at_unix"]
    previous_execution_seconds = state["execution_seconds"]
    previous_item_state = dict(item_state)
    state["started_at_unix"] = now
    state["execution_seconds"] = 0.0
    state["items"][item_id] = {
        **item_state,
        "attempt_count": 0,
        "last_fingerprint": "",
        "last_no_change_fingerprint": "",
        "running_role": None,
    }
    for field in (
        "resume_repository_fingerprint",
        "resume_review_changed_paths",
        "resume_acceptance_output",
        "resume_previous_verdict",
        "resume_reasoned_no_change",
    ):
        state["items"][item_id].pop(field, None)
    with log_stream:
        try:
            write_run_state(state_path, state)
            log_stream.write(
                "\n### Attempt limit reset\n"
                f"Reason: {reason}\n"
            )
            log_stream.flush()
        except OSError as exc:
            state["started_at_unix"] = previous_started_at
            state["execution_seconds"] = previous_execution_seconds
            state["items"][item_id] = previous_item_state
            try:
                write_run_state(state_path, state)
            except OSError as restore_exc:
                return (
                    False,
                    f"cannot record attempt reset: {exc}; cannot restore run state: "
                    f"{restore_exc}",
                )
            return False, f"cannot record attempt reset: {exc}"
    return True, ""


def write_running_role(
    path: Path,
    state: dict[str, Any],
    item_id: str,
    item_state: dict[str, Any],
    role: str | None,
) -> None:
    """Persist an active role or its latest completed-stage resume checkpoint."""

    updated = {
        "attempt_count": item_state["attempt_count"],
        "last_fingerprint": item_state["last_fingerprint"],
        "last_no_change_fingerprint": item_state.get(
            "last_no_change_fingerprint",
            "",
        ),
        "base_head": item_state.get("base_head", ""),
        "executor_changed_paths": item_state.get("executor_changed_paths", []),
        "running_role": role,
    }
    if role is not None:
        for field in (
            "resume_repository_fingerprint",
            "resume_review_changed_paths",
            "resume_acceptance_output",
            "resume_previous_verdict",
            "resume_reasoned_no_change",
        ):
            if field in item_state:
                updated[field] = item_state[field]
    state["items"][item_id] = updated
    write_run_state(path, state)


def interrupted_item(
    state: dict[str, Any],
    items: list[WorkItem],
) -> tuple[WorkItem | None, str]:
    """Resolve the one item whose persisted role marks an interrupted round."""

    interrupted_ids = sorted(
        item_id
        for item_id, item_state in state["items"].items()
        if item_state.get("running_role") is not None
    )
    if not interrupted_ids:
        return None, "no interrupted driver role is recorded"
    if len(interrupted_ids) != 1:
        return None, (
            "driver run state has multiple interrupted roles: "
            + ", ".join(interrupted_ids)
        )
    interrupted_id = interrupted_ids[0]
    matches = [item for item in items if item.item_id == interrupted_id]
    if len(matches) != 1:
        return None, (
            f"interrupted item {interrupted_id} must resolve to exactly one "
            f"current work item; found {len(matches)}"
        )
    item = matches[0]
    if item.status not in {"active", "review"} or not item.acceptance:
        return None, (
            f"interrupted item {interrupted_id} is not an active or review item "
            "with non-empty acceptance"
        )
    return item, ""
