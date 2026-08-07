#!/usr/bin/env python3
"""Plan, execute, or resume one supervised Stage driver step.

The driver selects a READY leaf from the requested target: an eligible target
itself when it has no unfinished children, otherwise one of its eligible
children. Dry run is the default and has no side effects. ``--execute`` runs
exactly one executor -> acceptance -> independent-review sequence and records
runtime attempt state. ``--resume`` continues one checkpointed interrupted
sequence without rerunning completed stages. Neither mode commits, closes,
escalates, promotes, creates work, or advances a parent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


# Dry-run CLI use must not create import caches alongside the shipped plugin.
if __name__ == "__main__":
    sys.dont_write_bytecode = True

STAGE_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = STAGE_ROOT / "hooks"
SCRIPTS_DIR = STAGE_ROOT / "scripts"
RETROSPECTIVE_DIR = STAGE_ROOT / "skills" / "stage-retrospective"
for import_dir in (HOOKS_DIR, SCRIPTS_DIR, RETROSPECTIVE_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_repository import (  # noqa: E402
    changed_repository_paths,
    cumulative_executor_changed_paths,
    executor_changed_only_work_card,
    fingerprint,
    git_diff,
    git_head_exists,
    git_index_entries,
    git_index_path,
    git_untracked_paths,
    repository_fingerprint,
    repository_path_snapshot,
    work_card_relative_path,
    worktree_path_fingerprint,
)
from driver_environment import (  # noqa: E402
    check_environment,
    executor_environment,
    project_environment,
)
from driver_venues import (  # noqa: E402
    load_preflights_config,
    load_reapers_config,
    preflight_environment,
    reap_turn,
    resolve_independent_reviewer_venue,
    resolve_preflight_command,
    resolve_reap_command,
    run_preflight,
)
from driver_worklog import (  # noqa: E402
    RECOMMEND_ESCALATE,
    RECOMMEND_PASS,
    RECOMMEND_RETRY,
    append_driver_commands_to_work_log,
    append_driver_notice_to_work_log,
    append_failure_to_work_log,
    append_reap_warning_to_work_log,
    cap_text,
    print_escalation,
    print_preflight_blocker,
    reconcile_executor_work_log,
)
from driver_git import (  # noqa: E402
    commit_item,
    commit_lifecycle,
    create_run_branch,
    current_head,
    current_head_or_empty,
    restore_item_output,
    run_branch_name,
    run_git,
)
from driver_worktree import (  # noqa: E402
    create_unattended_worktree,
    current_branch,
    discard_worktree,
    preserve_unattended_runtime,
    remove_unattended_worktree,
    seed_unattended_runtime,
    unattended_worktree_path,
    worktree_clean,
)
from driver_subtree import (  # noqa: E402
    MIN_COMMAND_TIMEOUT_SECONDS,
    SUCCESS_CRITERIA_HEADING_RE,
    TOP_LEVEL_LIST_ITEM_RE,
    ancestor_chain,
    ancestors_are_runnable,
    declared_command_size,
    declared_success_criteria_count,
    is_in_subtree,
    select_next_ready_leaf,
    select_next_unattended_leaf,
    subtree_command_timeout,
    subtree_limits,
    unfinished_subtree_leaf_count,
)
from driver_review import (  # noqa: E402
    infrastructure_failure,
    load_driver_review_verdict,
    merge_narrow_review_verdict,
    retryable_review_infrastructure_failure,
    review_verdict_error,
    review_verdict_failures,
)
from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from stage_record_paths import record_path  # noqa: E402
from close_work import (  # noqa: E402
    clear_review_verdict,
    clip,
    ensure_work_log,
    executor_report_error,
    executor_review_dispositions,
    load_review_verdict,
    read_work_log,
    review_verdict_path,
    run_check,
    work_log_reference,
)
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_executors_config,
    load_limits_config,
    load_review_config,
    read_settings,
    resolve_executor_command,
    resolve_independent_review_command,
    schema_migration_banner,
)
from stage_work import (  # noqa: E402
    WORK_FINAL_STATUSES,
    WorkItem,
    load_all_work_items,
    non_terminal_children,
    parse_frontmatter,
    split_scope,
)


WORK_ID_RE = re.compile(r"^W-[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9_-]*)?$")
STAGE_RUNTIME_PREFIX = ".stage/.runtime/"
UNCHANGED_REPOSITORY_NOTICE = (
    "executor left repository state unchanged; work appears complete; "
    "attempt was not spent"
)
UNCHANGED_REPOSITORY_NEXT_ACTION = (
    "run close_work.py manually to verify and review the apparent completion"
)
EXECUTOR_REJECTION_NOTICE = (
    "executor rejected the work item after changing only its work card"
)
EXECUTOR_REJECTION_NEXT_ACTION = (
    "review the executor's reason, then withdraw or redesign the work item"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or execute one supervised Stage driver step."
    )
    parser.add_argument(
        "--project-root", default=".", help="Project root (default: cwd)."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run exactly one executor/acceptance/reviewer step.",
    )
    parser.add_argument(
        "--unattended",
        action="store_true",
        help=(
            "Run the whole ready subtree unattended in a separate Git worktree and branch "
            "(requires a limits config)."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=(
            "Override the per-command timeout derived from the target card's "
            f"declared size, in seconds (derived minimum: {MIN_COMMAND_TIMEOUT_SECONDS})."
        ),
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip the venue preflight command for operator recovery.",
    )
    parser.add_argument(
        "--reset-attempts",
        action="store_true",
        help="Reset the selected item's attempt limit state after human correction.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume one interrupted supervised round from its recorded role.",
    )
    parser.add_argument(
        "--reason",
        help="Required one-line reason for --reset-attempts.",
    )
    parser.add_argument("target", help="Existing parent or leaf work item id (W-*).")
    return parser.parse_args()


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


def print_plan(
    *,
    execute: bool,
    target_id: str,
    item: WorkItem,
    executor_command: str,
    reviewer_command: str,
    attempt: int,
    iteration: int,
    execution_seconds: float,
    limits: dict[str, int] | None,
) -> None:
    print(f"Mode: {'execute' if execute else 'dry-run'}")
    print(f"Target parent: {target_id}")
    print(f"Selected item: {item.item_id}")
    print(f"Executor: {executor_command}")
    for command in item.acceptance:
        print(f"Acceptance: {command}")
    print(f"Independent reviewer: {reviewer_command}")
    print(
        "Attempt: "
        f"{attempt}/{cap_text(limits, 'max_attempts_per_item')}"
    )
    print(f"Iteration: {iteration}/{cap_text(limits, 'max_iterations')}")
    time_cap = (
        f"{limits['max_wall_clock_seconds']}s"
        if limits is not None
        else "unlimited"
    )
    print(f"Execution time: {int(execution_seconds)}s/{time_cap}")


def limit_blocker(
    limits: dict[str, int] | None,
    *,
    attempt: int,
    iteration: int,
    execution_seconds: float,
) -> str:
    if limits is None:
        return ""
    if attempt > limits["max_attempts_per_item"]:
        return "per-item attempt cap reached before execution"
    if iteration > limits["max_iterations"]:
        return "global iteration limit exceeded before execution"
    if execution_seconds >= limits["max_wall_clock_seconds"]:
        return "global execution-time limit exceeded before execution"
    return ""


def timed_run_check(
    command: str,
    timeout: int,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> tuple[bool, str, str, float]:
    """Run one supervised work command and return its actual elapsed time."""

    started = time.monotonic()
    passed, evidence, raw = run_check(command, timeout, cwd, env=env)
    elapsed = max(0.0, time.monotonic() - started)
    return passed, evidence, raw, elapsed


CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ESCALATE_WORK = STAGE_ROOT / "scripts" / "escalate_work.py"
RETRO_SECTIONS = (
    "Work",
    "Decision points",
    "Principles applied",
    "Context that helped",
    "Context that was missing",
    "Next changes",
    "Rule candidate",
    "Promotion decision",
)


def retrospective_id_for_work_item(item_id: str) -> str:
    """Derive the one retrospective ID reserved for a work item."""

    if not WORK_ID_RE.fullmatch(item_id):
        raise ValueError(f"invalid work item ID for retrospective: {item_id}")
    return f"R-{item_id[2:]}"


def set_frontmatter_field(text: str, name: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def write_driver_retrospective(
    stage_root: Path, item: WorkItem
) -> tuple[str, str]:
    """Write a machine-generated retrospective, flagged driver-generated.

    Returns (retro_id, error). The reflective retrospective is deliberately
    thin — a human reviews it when merging the run branch (DE-24, mode A).
    """

    try:
        retro_id = retrospective_id_for_work_item(item.item_id)
    except ValueError as exc:
        return "", str(exc)
    path = record_path(stage_root / "work" / "retrospectives", retro_id)
    if path.exists():
        existing_owner = parse_frontmatter(path).get("work_item", "")
        if existing_owner != item.item_id:
            owner = existing_owner or "an unknown work item"
            return (
                "",
                f"cannot write retrospective {retro_id}: already belongs to {owner}, "
                f"not {item.item_id}",
            )
    note = "driver-generated (사람 머지 검토 대상)"
    # Neutral wording: this is written BEFORE close_work verifies. It must not
    # claim success — the item's Verification (stamped by close_work) is the
    # source of truth for whether acceptance and the independent review passed.
    sections = {
        "Work": (
            f"{note}: 무인 드라이버가 {item.item_id}의 executor를 실행하고 결과를 커밋했다. "
            "acceptance·독립 판정의 실제 통과 여부와 최종 완료는 항목의 Verification"
            "(close_work가 기록)이 정본이다. 실행자의 작업 내용·이유·변경 경로 주장은 "
            f"`{work_log_reference(item.item_id)}`가 소유한다."
        ),
        "Decision points": f"{note}: 기계 실행, 별도 결정 없음.",
        "Principles applied": f"{note}: Honesty, Fail Fast, No partial completion.",
        "Context that helped": f"{note}: 항목 acceptance가 종료를 결정적으로 판정.",
        "Context that was missing": f"{note}: 반성적 회고는 사람이 브랜치 머지 시 보완.",
        "Next changes": f"{note}: 사람이 격리 브랜치를 검토·머지.",
        # A run cannot judge from inside whether its own behavior should bind
        # future cards, so it leaves the rule candidate to whoever merges it.
        "Rule candidate": f"{note}: 머지하는 사람이 채운다 — 이 실행이 남긴 규칙 후보가 있으면.",
        "Promotion decision": (
            f"{note}: 항목 Verification의 결과를 따른다(close_work가 acceptance·독립 판정 통과 시에만 completed로 스탬프)."
        ),
    }
    body = f"---\nid: {retro_id}\nwork_item: {item.item_id}\n---\n\n# {retro_id} {item.item_id} 무인 드라이버 회고\n"
    for heading in RETRO_SECTIONS:
        body += f"\n## {heading}\n\n{sections[heading]}\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
    except OSError as exc:
        return "", f"cannot write retrospective {retro_id}: {exc}"
    return retro_id, ""


AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"


def current_card_path(stage_root: Path, item_id: str) -> Path:
    return record_path(stage_root / v4_lifecycle_paths().current_cards, item_id)


def mark_retrospective(stage_root: Path, item_id: str, retro_id: str) -> None:
    path = current_card_path(stage_root, item_id)
    text = path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "retrospective", "completed")
    text = set_frontmatter_field(text, "retrospective_ref", retro_id)
    path.write_text(text, encoding="utf-8")


def close_via_close_work(
    project_root: Path,
    item_id: str,
    extra_checks: list[str],
    timeout: int,
    promotion_default: str | None = None,
) -> tuple[bool, str]:
    """Reuse the reviewed close_work.py: acceptance + (autonomous) independent review + close."""

    raw_promotion = parse_frontmatter(
        current_card_path(project_root / ".stage", item_id)
    ).get("promotion", "")
    promotion = raw_promotion.strip() if isinstance(raw_promotion, str) else ""
    if promotion == "pending" and promotion_default is not None:
        promotion = promotion_default
    command = [
        sys.executable,
        str(CLOSE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--promotion",
        promotion,
        "--timeout",
        str(timeout),
    ]
    for check in extra_checks:
        command += ["--check", check]
    try:
        proc = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout + 60,
            env=project_environment(project_root),
        )
    except subprocess.TimeoutExpired:
        return False, f"close_work timed out after {timeout + 60}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def escalate_via_escalate_work(
    project_root: Path, item_id: str, reason: str, timeout: int = 120
) -> tuple[bool, str]:
    """Reuse the reviewed escalate_work.py: item -> blocked + a pending decision."""

    command = [
        sys.executable,
        str(ESCALATE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--reason",
        reason,
    ]
    try:
        proc = subprocess.run(
            command, cwd=str(project_root), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, f"escalate_work timed out after {timeout}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def shell_command(args: list[str], os_name: str | None = None) -> str:
    """Join arguments the way the named platform's shell parses them.

    The result is handed to a shell, and the two shells disagree: POSIX shells
    strip single quotes, `cmd.exe` does not. Quoting for one breaks the other,
    so each gets its own joiner. Windows arguments containing shell
    metacharacters must be quoted even when they contain no whitespace.

    ``os_name`` defaults to the running platform. It is a parameter so a test can
    exercise the other branch without reaching into the process-wide ``os``
    module — there is no Windows runner here, so both branches have to be
    reachable from any host.
    """

    if (os_name or os.name) == "nt":
        rendered_args: list[str] = []
        for arg in args:
            rendered = subprocess.list2cmdline([arg])
            if any(character in arg for character in "&^|<>") and not (
                rendered.startswith('"') and rendered.endswith('"')
            ):
                trailing_backslashes = len(rendered) - len(rendered.rstrip("\\"))
                rendered += "\\" * trailing_backslashes
                rendered = f'"{rendered}"'
            rendered_args.append(rendered)
        return " ".join(rendered_args)
    return shlex.join(args)


def audit_check(project_root: Path, os_name: str | None = None) -> str:
    return shell_command(
        [sys.executable, str(AUDIT), "--project-root", str(project_root)], os_name
    )


def close_ready_ancestors(
    project_root: Path, stage_root: Path, target_id: str, parent_id: str, timeout: int
) -> tuple[list[str], str]:
    """Close each ancestor up to and including the target whose children are all terminal.

    Returns (closed_ids, error). A non-empty error means a parent that SHOULD have
    closed did not (retrospective or close failed) — the caller must fail closed;
    stopping because a parent still has non-terminal children is normal, not an error.

    Parent verification always includes the audit (whole-.stage consistency) plus
    close_work's own aggregation gate (children terminal). close_work also loads and
    runs any parent-declared acceptance once; the children were each independently
    reviewed (DE-00000027). No silent pass.
    """

    closed: list[str] = []
    current = parent_id
    while current:
        items = load_all_work_items(stage_root)
        match = [item for item in items if item.item_id == current]
        if not match:
            break
        parent = match[0]
        if parent.status in WORK_FINAL_STATUSES:
            current = "" if current == target_id else parent.parent
            continue
        if non_terminal_children(current, items):
            break  # normal: this parent waits for its other children
        if not (parent.retrospective == "completed" and parent.retrospective_ref):
            retro_id, err = write_driver_retrospective(
                stage_root, parent
            )
            if err:
                return closed, f"{current}: {err}"
            mark_retrospective(stage_root, current, retro_id)
        checks = [audit_check(project_root)]
        raw_decision_refs = parse_frontmatter(parent.path).get("decision_refs", "")
        decision_refs = (
            split_scope(raw_decision_refs)
            if isinstance(raw_decision_refs, str)
            else ()
        )
        promotion_default = "not_applicable" if not decision_refs and not parent.promotes else None
        ok, out = close_via_close_work(
            project_root,
            current,
            checks,
            timeout,
            promotion_default=promotion_default,
        )
        if not ok:
            return closed, f"{current}: parent close failed: {out.strip()[:200]}"
        closed.append(current)
        current = "" if current == target_id else parent.parent
    return closed, ""


def remaining_timeout(now: float, wall_clock: int, per_command: int) -> int:
    return max(1, min(per_command, int(wall_clock - (time.time() - now))))


def escalate_and_commit(project_root: Path, item_id: str, reason: str, timeout: int) -> bool:
    """Escalate an item to blocked and commit the resulting lifecycle to the run branch.

    Returns False when escalation or its lifecycle commit failed — the run must stop,
    because the item would otherwise stay `active` or its blocked state would be lost.
    """

    ok, out = escalate_via_escalate_work(project_root, item_id, reason, timeout)
    if not ok:
        print_escalation(
            f"escalation of {item_id} FAILED ({out.strip()[:200]}); stopping run to avoid a stuck loop"
        )
        return False
    lifecycle_ok, lifecycle_out = commit_lifecycle(
        project_root, f"driver: {item_id} escalated (lifecycle)"
    )
    if not lifecycle_ok:
        print_escalation(
            f"cannot commit escalation lifecycle for {item_id}: {lifecycle_out.strip()[:200]}"
        )
        return False
    return True


def run_unattended(
    args: argparse.Namespace,
    project_root: Path,
    stage_root: Path,
    now: float,
    *,
    branch: str = "",
    base_branch: str = "",
) -> int:
    limits, limits_error = load_limits_config(stage_root)
    if limits_error:
        print_escalation(f"limits config unusable: {limits_error}")
        return 1
    if limits is None:
        print_escalation(
            "unattended mode requires a `limits` config (absent is not unlimited here); refusing to run"
        )
        return 1
    limits = subtree_limits(
        limits,
        args.target,
        load_all_work_items(stage_root),
        per_action_seconds=getattr(
            args,
            "limit_action_seconds",
            args.timeout,
        ),
    )
    # A dirty index/worktree would leak unrelated changes into item commits.
    if not worktree_clean(project_root):
        print_escalation("working tree/index is not clean; commit or stash before an unattended run")
        return 1

    if branch:
        if current_branch(project_root) != branch:
            print_escalation(
                f"unattended worktree is not on its run branch {branch}"
            )
            return 1
    else:
        base_branch = current_branch(project_root)
        branch, branch_error = create_run_branch(project_root, args.target, now)
        if branch_error:
            print_escalation(branch_error)
            return 1
    print(f"Unattended run on isolated branch: {branch} (base: {base_branch or 'unknown'})")

    wall = limits["max_wall_clock_seconds"]
    cap = limits["max_attempts_per_item"]
    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    processed: list[str] = []
    iteration = 0
    while True:
        if time.time() - now >= wall:
            print(f"STOP: wall-clock limit {wall}s reached; {len(processed)} closed; handoff on {branch}")
            return 1
        if iteration >= limits["max_iterations"]:
            print(
                f"STOP: iteration limit {limits['max_iterations']} reached; "
                f"{len(processed)} closed; handoff on {branch}"
            )
            return 1

        items = load_all_work_items(stage_root)
        item = select_next_unattended_leaf(args.target, items)
        if item is None:
            break

        # Safety: never leave the isolated branch (an executor could switch it).
        if current_branch(project_root) != branch:
            print_escalation(f"HEAD left the run branch {branch}; aborting to protect the base branch")
            return 1

        cmd_timeout = remaining_timeout(now, wall, args.timeout)

        executor_command, executor_error = resolve_executor_command(
            load_executors_config(stage_root), item.venue
        )
        if executor_error or not executor_command:
            if not escalate_and_commit(
                project_root, item.item_id, executor_error or "executor command missing", cmd_timeout
            ):
                return 1
            continue
        review_config = load_review_config(stage_root)
        reviewer_command, reviewer_error = resolve_independent_review_command(
            review_config,
            item.venue,
        )
        if reviewer_error or not reviewer_command:
            if not escalate_and_commit(
                project_root,
                item.item_id,
                reviewer_error or "independent reviewer command missing",
                cmd_timeout,
            ):
                return 1
            continue
        if not run_preflight(
            stage_root=stage_root,
            project_root=project_root,
            item=item,
            items=items,
            timeout=cmd_timeout,
            skip=getattr(args, "skip_preflight", False),
        ):
            return 1
        iteration += 1

        state, state_error = load_run_state(state_path, args.target, now)
        if state_error or state is None:
            print_escalation(state_error or "driver run state unavailable")
            return 1
        item_state = state["items"].get(
            item.item_id,
            {"attempt_count": 0, "last_fingerprint": "", "base_head": ""},
        )
        if not item_state.get("base_head"):
            base_head, head_error = current_head(project_root)
            if head_error:
                print_escalation(head_error)
                return 1
            item_state["base_head"] = base_head
        base_head = item_state["base_head"]
        attempt = item_state["attempt_count"] + 1
        if attempt > cap:
            try:
                cap_log_path = ensure_work_log(stage_root, item.item_id)
                reap_turn(
                    stage_root=stage_root,
                    project_root=project_root,
                    log_path=cap_log_path,
                    item_path=item.path,
                    venue=item.venue,
                    role="executor",
                    timeout=cmd_timeout,
                )
            except RuntimeError as exc:
                print(f"WARNING: cannot record attempt-cap reaping: {exc}")
            restored, restore_error = restore_item_output(project_root, base_head)
            if not restored:
                print_escalation(restore_error)
                return 1
            if not escalate_and_commit(
                project_root, item.item_id, f"per-item attempt cap ({cap}) reached", cmd_timeout
            ):
                return 1
            continue

        index_path, index_error = git_index_path(project_root)
        if index_error:
            print_escalation(
                f"cannot resolve Git index before executor: {index_error}"
            )
            return 1
        try:
            log_path = ensure_work_log(stage_root, item.item_id)
            verdict_file = review_verdict_path(stage_root, item.item_id)
            durable_log = read_work_log(log_path)
            append_driver_commands_to_work_log(
                log_path,
                executor_command=executor_command,
                reviewer_command=reviewer_command,
            )
            log_before = read_work_log(log_path)
            pending_findings = review_verdict_failures(verdict_file)
            repository_before = repository_fingerprint(project_root)
            repository_paths_before = repository_path_snapshot(project_root)
            executor_changed_paths = item_state.get(
                "executor_changed_paths",
                [],
            )
        except RuntimeError as exc:
            print_escalation(f"cannot prepare executor observation: {exc}")
            return 1
        try:
            write_running_role(
                state_path,
                state,
                item.item_id,
                item_state,
                "executor",
            )
        except OSError as exc:
            print_escalation(f"cannot persist executor running role: {exc}")
            return 1
        with tempfile.TemporaryDirectory(
            prefix="stage-drive-executor-index-"
        ) as temporary:
            executor_index = Path(temporary) / "executor-index"
            if index_path is not None and index_path.is_file():
                try:
                    shutil.copyfile(index_path, executor_index)
                except OSError as exc:
                    print_escalation(
                        f"cannot prepare disposable Git index for executor: {exc}"
                    )
                    return 1
            executor_ok, executor_evidence, _raw = run_check(
                executor_command,
                cmd_timeout,
                project_root,
                env=executor_environment(
                    item,
                    project_root,
                    log_path,
                    verdict_file,
                    executor_index if index_path is not None else None,
                    items=items,
                ),
            )
        try:
            log_after_executor = read_work_log(log_path)
            log_after_executor, executor_log_error = reconcile_executor_work_log(
                log_path,
                durable_log,
                log_before,
                log_after_executor,
            )
        except RuntimeError as exc:
            log_after_executor = log_before
            executor_log_error = str(exc)
        executor_reaped = reap_turn(
            stage_root=stage_root,
            project_root=project_root,
            log_path=log_path,
            item_path=item.path,
            venue=item.venue,
            role="executor",
            timeout=cmd_timeout,
        )
        try:
            write_running_role(
                state_path,
                state,
                item.item_id,
                item_state,
                None,
            )
        except OSError as exc:
            print_escalation(f"cannot clear executor running role: {exc}")
            return 1
        try:
            repository_after = repository_fingerprint(project_root)
            repository_paths_after = repository_path_snapshot(project_root)
            current_fingerprint = fingerprint(project_root, [executor_evidence])
            changed_paths = cumulative_executor_changed_paths(
                executor_changed_paths,
                repository_paths_before,
                repository_paths_after,
            )
        except RuntimeError as exc:
            print_escalation(f"cannot inspect changes for progress: {exc}")
            return 1
        executor_failure = "executor failed"
        executor_rejected = False
        unchanged_repository = False
        dispositions, disposition_error = executor_review_dispositions(
            log_before,
            log_after_executor,
            pending_findings,
        )
        report_error = executor_report_error(
            log_before,
            log_after_executor,
            changed_paths,
            pending_findings,
            ignored_paths=[log_path.relative_to(project_root).as_posix()],
        )
        reasoned_no_change = (
            bool(pending_findings)
            and not disposition_error
            and bool(dispositions)
            and all(
                entry["disposition"] in {"decline", "defer"}
                for entry in dispositions
            )
        )
        infrastructure_failed = infrastructure_failure(executor_evidence)
        if executor_log_error:
            executor_ok = False
            executor_failure = executor_log_error
        elif not executor_reaped:
            executor_failure = (
                "executor reap command failed"
                if executor_ok
                else "executor failed; executor reap command failed"
            )
            executor_ok = False
        elif executor_ok and report_error:
            executor_ok = False
            executor_failure = report_error
        elif (
            executor_ok
            and repository_after == repository_before
            and not reasoned_no_change
        ):
            unchanged_repository = True
        elif executor_ok:
            try:
                executor_rejected = executor_changed_only_work_card(
                    project_root,
                    item,
                    changed_paths,
                )
            except RuntimeError as exc:
                executor_ok = False
                executor_failure = str(exc)
        no_progress = (
            bool(item_state["last_fingerprint"]) and current_fingerprint == item_state["last_fingerprint"]
        )
        repeated_unchanged_repository = (
            unchanged_repository
            and bool(item_state.get("last_no_change_fingerprint"))
            and repository_after == item_state["last_no_change_fingerprint"]
        )
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        counted_attempt = (
            item_state["attempt_count"]
            if infrastructure_failed or unchanged_repository or executor_rejected
            else attempt
        )
        state["items"][item.item_id] = {
            "attempt_count": counted_attempt,
            "last_fingerprint": current_fingerprint,
            "last_no_change_fingerprint": (
                repository_after if unchanged_repository else ""
            ),
            "base_head": base_head,
            "executor_changed_paths": (
                changed_paths if executor_ok else executor_changed_paths
            ),
            "running_role": None,
        }
        write_run_state(state_path, state)

        if unchanged_repository:
            if no_progress or repeated_unchanged_repository:
                if not escalate_and_commit(
                    project_root,
                    item.item_id,
                    "NO-PROGRESS repository state matched the previous round",
                    cmd_timeout,
                ):
                    return 1
                continue
            try:
                append_driver_notice_to_work_log(
                    log_path,
                    reason=UNCHANGED_REPOSITORY_NOTICE,
                    recommended_next_action=UNCHANGED_REPOSITORY_NEXT_ACTION,
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
            print(f"[{item.item_id}] {UNCHANGED_REPOSITORY_NOTICE}")
            print(f"Recommended next action: {UNCHANGED_REPOSITORY_NEXT_ACTION}")
            return 0

        # A FAILED executor must never proceed to commit/close. Discard the failed
        # attempt's partial output, then retry or escalate.
        if not executor_ok:
            try:
                append_failure_to_work_log(
                    log_path,
                    role="executor",
                    reason=executor_failure,
                    evidence=executor_evidence,
                )
            except RuntimeError as exc:
                discard_worktree(project_root)
                print_escalation(str(exc))
                return 1
            discard_worktree(project_root)
            if not executor_reaped:
                print_escalation(
                    f"executor reap command failed for {item.item_id}; "
                    "stopping before another turn"
                )
                return 1
            if infrastructure_failed:
                print(
                    f"[{item.item_id}] executor infrastructure failure; "
                    f"retry without spending attempt {item_state['attempt_count']}/{cap}"
                )
            elif no_progress or attempt >= cap:
                restored, restore_error = restore_item_output(
                    project_root,
                    base_head,
                )
                if not restored:
                    print_escalation(restore_error)
                    return 1
                if not escalate_and_commit(
                    project_root,
                    item.item_id,
                    f"{executor_failure}; no progress or attempt cap",
                    cmd_timeout,
                ):
                    return 1
            else:
                print(f"[{item.item_id}] {executor_failure}; retry {attempt}/{cap}")
            continue

        executor_changed_paths = changed_paths
        if current_branch(project_root) != branch:
            print_escalation(f"HEAD left the run branch {branch}; aborting")
            return 1

        commit_ok, commit_message = commit_item(project_root, item, base_head)
        if not commit_ok:
            discard_worktree(project_root)
            if not escalate_and_commit(
                project_root, item.item_id, f"commit failed: {commit_message}", cmd_timeout
            ):
                return 1
            continue

        if executor_rejected:
            try:
                append_driver_notice_to_work_log(
                    log_path,
                    reason=EXECUTOR_REJECTION_NOTICE,
                    recommended_next_action=EXECUTOR_REJECTION_NEXT_ACTION,
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
            print(f"[{item.item_id}] {EXECUTOR_REJECTION_NOTICE}")
            print(f"Recommended next action: {EXECUTOR_REJECTION_NEXT_ACTION}")
            return 0

        card_path = current_card_path(stage_root, item.item_id)
        try:
            card_before_retrospective = card_path.read_text(encoding="utf-8")
        except OSError as exc:
            print_escalation(f"cannot snapshot work card before close: {exc}")
            return 1
        created_retro_path: Path | None = None
        if not (item.retrospective == "completed" and item.retrospective_ref):
            retro_id, retro_error = write_driver_retrospective(stage_root, item)
            if retro_error:
                if not escalate_and_commit(project_root, item.item_id, retro_error, cmd_timeout):
                    return 1
                continue
            mark_retrospective(stage_root, item.item_id, retro_id)
            created_retro_path = (
                record_path(stage_root / "work" / "retrospectives", retro_id)
            )

        reviewer_venue = resolve_independent_reviewer_venue(
            review_config,
            item.venue,
        )
        while True:
            try:
                write_running_role(
                    state_path,
                    state,
                    item.item_id,
                    state["items"][item.item_id],
                    "reviewer",
                )
            except OSError as exc:
                print_escalation(f"cannot persist reviewer running role: {exc}")
                return 1
            close_ok, close_out = close_via_close_work(
                project_root,
                item.item_id,
                [],
                cmd_timeout,
            )
            try:
                read_work_log(log_path)
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
            reviewer_reaped = True
            if reviewer_venue is not None:
                reviewer_reaped = reap_turn(
                    stage_root=stage_root,
                    project_root=project_root,
                    log_path=log_path,
                    item_path=item.path,
                    venue=reviewer_venue,
                    role="reviewer",
                    timeout=cmd_timeout,
                )
            try:
                write_running_role(
                    state_path,
                    state,
                    item.item_id,
                    state["items"][item.item_id],
                    None,
                )
            except OSError as exc:
                print_escalation(f"cannot clear reviewer running role: {exc}")
                return 1
            close_infrastructure_failure = retryable_review_infrastructure_failure(
                close_ok=close_ok,
                close_output=close_out,
                verdict_file=verdict_file,
            )
            if not close_infrastructure_failure:
                break
            try:
                append_failure_to_work_log(
                    log_path,
                    role="close",
                    reason="review infrastructure failed; retrying without spending an attempt",
                    evidence=close_out,
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
            if not reviewer_reaped:
                print_escalation(
                    f"reviewer reap command failed for {item.item_id}; "
                    "stopping before another turn"
                )
                return 1
            iteration += 1
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            state["items"][item.item_id] = {
                "attempt_count": item_state["attempt_count"],
                "last_fingerprint": item_state["last_fingerprint"],
                "base_head": base_head,
                "executor_changed_paths": executor_changed_paths,
                "running_role": None,
            }
            write_run_state(state_path, state)
            if (
                iteration >= limits["max_iterations"]
                or time.time() - now >= wall
            ):
                try:
                    card_path.write_text(
                        card_before_retrospective,
                        encoding="utf-8",
                    )
                    if created_retro_path is not None:
                        created_retro_path.unlink(missing_ok=True)
                except OSError as exc:
                    print_escalation(
                        f"cannot restore lifecycle after review infrastructure failure: {exc}"
                    )
                    return 1
                restored, restore_error = restore_item_output(
                    project_root,
                    base_head,
                )
                if not restored:
                    print_escalation(restore_error)
                    return 1
                print_escalation(
                    "global limit reached while retrying review infrastructure; "
                    "item output left uncommitted for human handoff"
                )
                return 1
            print(
                f"[{item.item_id}] review infrastructure failure; "
                f"retry without spending attempt {item_state['attempt_count']}/{cap}"
            )

        state["items"][item.item_id] = {
            "attempt_count": attempt,
            "last_fingerprint": current_fingerprint,
            "base_head": base_head,
            "executor_changed_paths": executor_changed_paths,
            "running_role": None,
        }
        write_run_state(state_path, state)

        if not reviewer_reaped:
            if not close_ok:
                try:
                    append_failure_to_work_log(
                        log_path,
                        role="close",
                        reason="close failed (acceptance or independent review)",
                        evidence=close_out,
                    )
                except RuntimeError as exc:
                    print(f"WARNING: {exc}")
            print_escalation(
                f"reviewer reap command failed for {item.item_id}; stopping before another turn"
            )
            return 1
        if not close_ok:
            close_failure = "close failed (acceptance or independent review)"
            try:
                append_failure_to_work_log(
                    log_path,
                    role="close",
                    reason=close_failure,
                    evidence=close_out,
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
            reason = close_failure
            clipped_close_out = clip(close_out)
            if clipped_close_out:
                reason += f"; close_work output:\n{clipped_close_out}"
            try:
                card_path.write_text(
                    card_before_retrospective,
                    encoding="utf-8",
                )
                if created_retro_path is not None:
                    created_retro_path.unlink(missing_ok=True)
            except OSError as exc:
                print_escalation(
                    f"cannot restore pre-review lifecycle for retry: {exc}"
                )
                return 1
            state["items"][item.item_id] = {
                "attempt_count": attempt,
                "last_fingerprint": current_fingerprint,
                "base_head": base_head,
                "executor_changed_paths": executor_changed_paths,
                "running_role": None,
            }
            write_run_state(state_path, state)
            if no_progress or attempt >= cap:
                restored, restore_error = restore_item_output(
                    project_root,
                    base_head,
                )
                if not restored:
                    print_escalation(restore_error)
                    return 1
                if not escalate_and_commit(
                    project_root, item.item_id, f"{reason}; no progress or attempt cap reached", cmd_timeout
                ):
                    return 1
            else:
                print(f"[{item.item_id}] {reason}; retry {attempt}/{cap}")
            continue

        # Commit the lifecycle records (card completed, retrospective, indexes) to the run
        # branch, so a merge carries the Stage bookkeeping — not only the executor output.
        lc_ok, lc_msg = commit_lifecycle(project_root, f"driver: {item.item_id} closed (lifecycle)")
        if not lc_ok:
            print_escalation(f"cannot commit lifecycle for {item.item_id}: {lc_msg}")
            return 1
        processed.append(item.item_id)
        print(f"[{item.item_id}] completed on {branch}")

        _closed, anc_error = close_ready_ancestors(
            project_root, stage_root, args.target, item.parent, cmd_timeout
        )
        lc_ok, lc_msg = commit_lifecycle(
            project_root, f"driver: {item.item_id} ancestor aggregation (lifecycle)"
        )
        if not lc_ok:
            failures = []
            if anc_error:
                failures.append(f"parent aggregation-close failed: {anc_error}")
            failures.append(
                f"cannot commit ancestor lifecycle for {item.item_id}: "
                f"{lc_msg.strip()[:200]}"
            )
            print_escalation(
                f"{'; '.join(failures)}; handoff on {branch}"
            )
            return 1
        if anc_error:
            print_escalation(f"parent aggregation-close failed: {anc_error}; handoff on {branch}")
            return 1

    print(
        f"Unattended run finished: {len(processed)} item(s) closed on isolated branch {branch}. "
        "Human review + merge required; the base branch was not modified."
    )
    return 0


def run_unattended_in_worktree(
    args: argparse.Namespace,
    project_root: Path,
    stage_root: Path,
    now: float,
    *,
    worktree_root: Path | None = None,
) -> int:
    """Run unattended work away from the human checkout and clean up when safe."""

    limits, limits_error = load_limits_config(stage_root)
    if limits_error:
        print_escalation(f"limits config unusable: {limits_error}")
        return 1
    if limits is None:
        print_escalation(
            "unattended mode requires a `limits` config (absent is not unlimited here); "
            "refusing to run"
        )
        return 1
    if not worktree_clean(project_root):
        print_escalation(
            "working tree/index is not clean; commit or stash before an unattended run"
        )
        return 1

    base_branch = current_branch(project_root)
    run_root, branch, creation_error = create_unattended_worktree(
        project_root,
        args.target,
        now,
        worktree_root=worktree_root,
    )
    if creation_error or run_root is None:
        print_escalation(creation_error or "unattended worktree unavailable")
        return 1
    print(f"Unattended worktree: {run_root}")
    print(f"Unattended branch: {branch}")

    seed_error = seed_unattended_runtime(
        stage_root,
        run_root / ".stage",
        args.target,
        load_all_work_items(stage_root),
    )
    if seed_error:
        print_escalation(
            f"{seed_error}. The unattended executor did not start; worktree retained at "
            f"{run_root}."
        )
        return 1
    result = run_unattended(
        args,
        run_root,
        run_root / ".stage",
        now,
        branch=branch,
        base_branch=base_branch,
    )
    runtime_error = preserve_unattended_runtime(run_root / ".stage", stage_root)
    if runtime_error:
        print_escalation(
            f"{runtime_error}. Recovery retained on branch {branch} at {run_root}."
        )
        return 1
    cleanup_error = remove_unattended_worktree(project_root, run_root)
    if cleanup_error:
        print_escalation(
            f"{cleanup_error}. Recovery retained on branch {branch} at {run_root}. "
            f"After preserving any changes, run `git worktree remove {run_root}`."
        )
        return 1
    print(f"Removed unattended worktree: {run_root}")
    return result


def main() -> int:
    args = parse_args()
    if args.reset_attempts:
        if args.reason is None or not args.reason.strip():
            print_escalation("--reason is required with --reset-attempts")
            return 2
        if "\n" in args.reason or "\r" in args.reason:
            print_escalation("--reason must be one line")
            return 2
        if (
            args.execute
            or args.unattended
            or args.resume
            or args.skip_preflight
            or args.timeout is not None
        ):
            print_escalation(
                "--reset-attempts cannot be combined with execution options"
            )
            return 2
        args.reason = args.reason.strip()
    elif args.reason is not None:
        print_escalation("--reason requires --reset-attempts")
        return 2
    if args.resume and (args.execute or args.unattended or args.skip_preflight):
        print_escalation("--resume cannot be combined with other execution modes")
        return 2
    if args.timeout is not None and args.timeout <= 0:
        print_escalation("--timeout must be a positive integer")
        return 2
    if not WORK_ID_RE.fullmatch(args.target):
        print_escalation("target must be a safe W-* work item id")
        return 2

    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print_escalation(schema_blocker)
        return 2
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        print_escalation("drive requires a schema-v4 Stage project")
        return 2

    items = load_all_work_items(stage_root)
    targets = [item for item in items if item.item_id == args.target]
    if len(targets) != 1:
        print_escalation(
            f"target must resolve to exactly one existing work item; found {len(targets)}"
        )
        return 1
    if args.reset_attempts:
        state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
        state, state_error = load_run_state(state_path, args.target, time.time())
        if state_error or state is None:
            print_escalation(state_error or "driver run state is unavailable")
            return 1
        item, interrupted_error = interrupted_item(state, items)
        if item is None and interrupted_error == "no interrupted driver role is recorded":
            item = select_next_ready_leaf(args.target, items)
        elif interrupted_error:
            print_escalation(interrupted_error)
            return 1
        if item is None:
            print_escalation(
                "target has no active or review leaf with non-empty acceptance"
            )
            return 1
        reset_ok, reset_error = reset_attempts(
            state_path=state_path,
            stage_root=stage_root,
            target_id=args.target,
            item_id=item.item_id,
            now=time.time(),
            reason=args.reason,
        )
        if not reset_ok:
            print_escalation(reset_error)
            return 1
        print(f"Reset attempts for {item.item_id}. Reason: {args.reason}")
        return 0
    requested_timeout = args.timeout
    args.timeout = subtree_command_timeout(
        args.target,
        items,
        requested=requested_timeout,
    )
    args.limit_action_seconds = (
        requested_timeout
        if requested_timeout is not None
        else MIN_COMMAND_TIMEOUT_SECONDS
    )

    if args.unattended:
        return run_unattended_in_worktree(
            args,
            project_root,
            stage_root,
            time.time(),
        )

    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    now = time.time()
    state, state_error = load_run_state(state_path, args.target, now)
    if state_error or state is None:
        print_escalation(state_error or "driver run state is unavailable")
        return 1

    resume_role: str | None = None
    if args.resume:
        item, interrupted_error = interrupted_item(state, items)
        if interrupted_error or item is None:
            print_escalation(interrupted_error or "interrupted item is unavailable")
            return 1
        resume_role = state["items"][item.item_id]["running_role"]
    else:
        interrupted, interrupted_error = interrupted_item(state, items)
        if interrupted is not None:
            print_escalation(
                f"interrupted driver role is recorded for {interrupted.item_id}; "
                "use --resume or --reset-attempts"
            )
            return 1
        if interrupted_error != "no interrupted driver role is recorded":
            print_escalation(interrupted_error)
            return 1
        item = select_next_ready_leaf(args.target, items)
    if item is None:
        unfinished_children = non_terminal_children(args.target, items)
        reason = (
            "no non-terminal direct child has non-empty acceptance and leaf readiness"
            if unfinished_children
            else "target is terminal or has empty acceptance"
        )
        print_escalation(reason)
        return 1

    limits, limits_error = load_limits_config(stage_root)
    if limits_error:
        print_escalation(f"limits config unusable: {limits_error}")
        return 1
    if limits is not None:
        limits = subtree_limits(
            limits,
            args.target,
            items,
            per_action_seconds=args.limit_action_seconds,
        )

    executor_command, executor_error = resolve_executor_command(
        load_executors_config(stage_root), item.venue
    )
    if executor_error or not executor_command:
        print_escalation(executor_error or "executor command is missing")
        return 1

    review_config = load_review_config(stage_root)
    reviewer_command, reviewer_error = resolve_independent_review_command(
        review_config, item.venue
    )
    if reviewer_error or not reviewer_command:
        print_escalation(
            reviewer_error or "independent reviewer command is missing"
        )
        return 1
    reviewer_venue = resolve_independent_reviewer_venue(
        review_config,
        item.venue,
    )
    if reviewer_venue is None:
        print_escalation("cannot resolve independent reviewer venue")
        return 1

    item_state = state["items"].get(
        item.item_id,
        {"attempt_count": 0, "last_fingerprint": "", "base_head": ""},
    )
    attempt = item_state["attempt_count"] + (0 if args.resume else 1)
    iteration = state["iteration_count"] + (0 if args.resume else 1)
    execution_seconds = state["execution_seconds"]
    print_plan(
        execute=args.execute or args.resume,
        target_id=args.target,
        item=item,
        executor_command=executor_command,
        reviewer_command=reviewer_command,
        attempt=attempt,
        iteration=iteration,
        execution_seconds=execution_seconds,
        limits=limits,
    )

    blocker = limit_blocker(
        limits,
        attempt=attempt,
        iteration=iteration,
        execution_seconds=execution_seconds,
    )
    if blocker:
        if args.execute and blocker == "per-item attempt cap reached before execution":
            try:
                cap_log_path = ensure_work_log(stage_root, item.item_id)
                reap_turn(
                    stage_root=stage_root,
                    project_root=project_root,
                    log_path=cap_log_path,
                    item_path=item.path,
                    venue=item.venue,
                    role="executor",
                    timeout=args.timeout,
                )
            except RuntimeError as exc:
                print(f"WARNING: cannot record attempt-cap reaping: {exc}")
        print_escalation(blocker)
        return 1
    if not args.execute and not args.resume:
        print("Outcome: plan only — no commands ran and no run state was written")
        return 0
    if not args.resume and not run_preflight(
        stage_root=stage_root,
        project_root=project_root,
        item=item,
        items=items,
        timeout=args.timeout,
        skip=args.skip_preflight,
    ):
        return 1

    if not item_state.get("base_head"):
        base_head, head_error = current_head_or_empty(project_root)
        if head_error:
            print_escalation(head_error)
            return 1
        item_state["base_head"] = base_head
    base_head = item_state["base_head"]
    in_progress_item_state = {
        **item_state,
        "attempt_count": attempt,
    }
    if args.resume:
        saved_repository_fingerprint = item_state.get(
            "resume_repository_fingerprint",
            "",
        )
        if not saved_repository_fingerprint:
            print_escalation(
                "interrupted driver state has no completed-stage checkpoint; "
                "use --reset-attempts before another executor turn"
            )
            return 1
        try:
            current_repository_fingerprint = repository_fingerprint(project_root)
        except RuntimeError as exc:
            print_escalation(f"cannot inspect repository before resume: {exc}")
            return 1
        if current_repository_fingerprint != saved_repository_fingerprint:
            print_escalation(
                "repository changed after the interrupted driver checkpoint; "
                "refusing to skip completed stages"
            )
            return 1
        print(f"Resuming after completed {resume_role}")

    step_ok = True
    failure = ""
    reviewer_blocked = False
    infrastructure_failed = False
    acceptance_output: list[str] = list(
        item_state.get("resume_acceptance_output", [])
        if resume_role == "reviewer"
        else []
    )
    changed_paths: list[str] = list(
        item_state.get("executor_changed_paths", [])
    )

    index_path, index_error = git_index_path(project_root)
    if index_error:
        print_escalation(f"cannot resolve Git index before execution: {index_error}")
        return 1
    index_existed = bool(index_path is not None and index_path.is_file())

    try:
        log_path = ensure_work_log(stage_root, item.item_id)
        verdict_file = review_verdict_path(stage_root, item.item_id)
        durable_log = read_work_log(log_path)
        if not args.resume:
            append_driver_commands_to_work_log(
                log_path,
                executor_command=executor_command,
                reviewer_command=reviewer_command,
            )
        log_before = read_work_log(log_path)
        previous_verdict = (
            item_state.get("resume_previous_verdict")
            if args.resume
            else load_driver_review_verdict(verdict_file)[0]
        )
        pending_findings = (
            [
                str(entry["criterion"])
                for entry in previous_verdict["criteria"]
                if entry["verdict"] == "FAIL"
            ]
            if previous_verdict is not None
            else []
        )
        if not args.resume:
            repository_before = repository_fingerprint(project_root)
            repository_paths_before = repository_path_snapshot(project_root)
        else:
            repository_before = item_state["resume_repository_fingerprint"]
            repository_paths_before = {}
    except RuntimeError as exc:
        print_escalation(f"cannot prepare executor observation: {exc}")
        return 1
    with tempfile.TemporaryDirectory(prefix="stage-drive-index-") as temporary:
        temporary_root = Path(temporary)
        executor_index = temporary_root / "executor-index"
        changed_paths_file = temporary_root / "review-changed-paths.json"
        previous_verdict_file = temporary_root / "previous-review-verdict.json"
        failed_criteria_file = temporary_root / "failed-review-criteria.json"
        current_verdict_file = temporary_root / "current-review-verdict.json"
        unchanged_repository = False
        executor_rejected = False
        if args.resume:
            executor_ok = True
            executor_evidence = "resumed from a completed executor checkpoint"
            executor_log_error = ""
            reasoned_no_change = bool(
                item_state.get("resume_reasoned_no_change", False)
            )
            executor_reaped = True
            repository_after = item_state["resume_repository_fingerprint"]
            review_changed_paths = list(
                item_state.get("resume_review_changed_paths", [])
            )
        else:
            if index_existed and index_path is not None:
                try:
                    shutil.copyfile(index_path, executor_index)
                except OSError as exc:
                    print_escalation(
                        f"cannot prepare disposable Git index for executor: {exc}"
                    )
                    return 1
            state["iteration_count"] = iteration
            try:
                write_running_role(
                    state_path,
                    state,
                    item.item_id,
                    in_progress_item_state,
                    "executor",
                )
            except OSError as exc:
                print_escalation(f"cannot persist executor running role: {exc}")
                return 1

            (
                executor_ok,
                executor_evidence,
                _executor_raw,
                executor_seconds,
            ) = timed_run_check(
                executor_command,
                args.timeout,
                project_root,
                env=executor_environment(
                    item,
                    project_root,
                    log_path,
                    verdict_file,
                    executor_index if index_path is not None else None,
                    items=items,
                ),
            )
            execution_seconds += executor_seconds
            state["execution_seconds"] = execution_seconds
            try:
                write_run_state(state_path, state)
            except OSError as exc:
                print_escalation(f"cannot persist executor execution time: {exc}")
                return 1
            infrastructure_failed = (
                not executor_ok and infrastructure_failure(executor_evidence)
            )
            print(f"Executor result:\n{executor_evidence}")
            try:
                log_after_executor = read_work_log(log_path)
                log_after_executor, executor_log_error = reconcile_executor_work_log(
                    log_path,
                    durable_log,
                    log_before,
                    log_after_executor,
                )
            except RuntimeError as exc:
                log_after_executor = log_before
                executor_log_error = str(exc)
            dispositions, disposition_error = executor_review_dispositions(
                log_before,
                log_after_executor,
                pending_findings,
            )
            reasoned_no_change = (
                bool(pending_findings)
                and not disposition_error
                and bool(dispositions)
                and all(
                    entry["disposition"] in {"decline", "defer"}
                    for entry in dispositions
                )
            )
            try:
                repository_after = repository_fingerprint(project_root)
                repository_paths_after = repository_path_snapshot(project_root)
                changed_paths = cumulative_executor_changed_paths(
                    changed_paths,
                    repository_paths_before,
                    repository_paths_after,
                )
                review_changed_paths = changed_repository_paths(
                    repository_paths_before,
                    repository_paths_after,
                )
            except RuntimeError as exc:
                step_ok = False
                failure = f"cannot inspect repository after executor: {exc}"

            if step_ok:
                if executor_log_error:
                    step_ok = False
                    failure = executor_log_error
                elif not executor_ok:
                    step_ok = False
                    failure = "executor command failed"
                else:
                    report_error = executor_report_error(
                        log_before,
                        log_after_executor,
                        changed_paths,
                        pending_findings,
                        ignored_paths=[
                            log_path.relative_to(project_root).as_posix()
                        ],
                    )
                    if report_error:
                        step_ok = False
                        failure = report_error
                    elif (
                        repository_after == repository_before
                        and not reasoned_no_change
                    ):
                        unchanged_repository = True

            if step_ok:
                executor_checkpoint = {
                    **in_progress_item_state,
                    "executor_changed_paths": changed_paths,
                    "resume_repository_fingerprint": repository_after,
                    "resume_review_changed_paths": review_changed_paths,
                    "resume_acceptance_output": [],
                    "resume_previous_verdict": previous_verdict,
                    "resume_reasoned_no_change": reasoned_no_change,
                }
                try:
                    write_running_role(
                        state_path,
                        state,
                        item.item_id,
                        executor_checkpoint,
                        "executor",
                    )
                except OSError as exc:
                    print_escalation(f"cannot persist executor checkpoint: {exc}")
                    return 1

            executor_reaped = reap_turn(
                stage_root=stage_root,
                project_root=project_root,
                log_path=log_path,
                item_path=item.path,
                venue=item.venue,
                role="executor",
                timeout=args.timeout,
            )
            if step_ok and not executor_reaped:
                step_ok = False
                failure = "executor reap command failed"

        if step_ok:
            try:
                executor_rejected = executor_changed_only_work_card(
                    project_root,
                    item,
                    changed_paths,
                )
            except RuntimeError as exc:
                step_ok = False
                failure = str(exc)
        if step_ok:
            try:
                changed_paths_file.write_text(
                    json.dumps(
                        (
                            review_changed_paths
                            if previous_verdict is not None
                            else changed_paths
                        ),
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            except OSError as exc:
                step_ok = False
                failure = (
                    "cannot write driver-observed paths for review: "
                    f"{exc}"
                )
        if (
            step_ok
            and not changed_paths
            and not reasoned_no_change
        ):
            step_ok = False
            failure = (
                "repository changed but no changed paths were observed for review"
            )

        if not step_ok:
            try:
                append_failure_to_work_log(
                    log_path,
                    role="executor",
                    reason=failure,
                    evidence=executor_evidence,
                )
            except RuntimeError as exc:
                failure = f"{failure}; {exc}"

        if step_ok and not executor_rejected and resume_role != "reviewer":
            for command in item.acceptance:
                accepted, evidence, raw, acceptance_seconds = timed_run_check(
                    command,
                    args.timeout,
                    project_root,
                    env=check_environment(),
                )
                execution_seconds += acceptance_seconds
                state["execution_seconds"] = execution_seconds
                try:
                    write_run_state(state_path, state)
                except OSError as exc:
                    print_escalation(
                        f"cannot persist execution time after acceptance: {exc}"
                    )
                    return 1
                acceptance_output.append(raw)
                print(f"Acceptance result:\n{evidence}")
                if not accepted:
                    step_ok = False
                    failure = "acceptance check failed"
                    infrastructure_failed = infrastructure_failure(evidence)
                    break

        # Passing acceptance turns an unchanged executor round into progress.
        # Failing acceptance remains an ordinary failed attempt.
        unchanged_repository = False

        if step_ok and not executor_rejected:
            try:
                reviewer_checkpoint_fingerprint = repository_fingerprint(project_root)
                reviewer_checkpoint = {
                    **in_progress_item_state,
                    "executor_changed_paths": changed_paths,
                    "resume_repository_fingerprint": reviewer_checkpoint_fingerprint,
                    "resume_review_changed_paths": review_changed_paths,
                    "resume_acceptance_output": acceptance_output,
                    "resume_previous_verdict": previous_verdict,
                    "resume_reasoned_no_change": reasoned_no_change,
                }
                write_running_role(
                    state_path,
                    state,
                    item.item_id,
                    reviewer_checkpoint,
                    "reviewer",
                )
            except RuntimeError as exc:
                step_ok = False
                failure = f"cannot inspect repository before reviewer: {exc}"
            except OSError as exc:
                print_escalation(f"cannot persist reviewer checkpoint: {exc}")
                return 1

        if step_ok and not executor_rejected:
            try:
                clear_review_verdict(verdict_file)
                if previous_verdict is not None:
                    previous_verdict_file.write_text(
                        json.dumps(previous_verdict, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    failed_criteria_file.write_text(
                        json.dumps(pending_findings, indent=2) + "\n",
                        encoding="utf-8",
                    )
            except RuntimeError as exc:
                step_ok = False
                failure = str(exc)
            except OSError as exc:
                step_ok = False
                failure = f"cannot prepare narrow review inputs: {exc}"

        if step_ok and not executor_rejected:
            reviewer_env = project_environment(project_root)
            reviewer_env.pop("GIT_INDEX_FILE", None)
            reviewer_verdict_file = (
                current_verdict_file
                if previous_verdict is not None
                else verdict_file
            )
            reviewer_env.update(
                {
                    "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
                    "STAGE_CHANGED_PATHS_FILE": str(changed_paths_file.resolve()),
                    "STAGE_REVIEW_MODE": (
                        "narrow"
                        if previous_verdict is not None
                        else "full"
                    ),
                    "STAGE_REVIEW_VERDICT_FILE": str(
                        reviewer_verdict_file.resolve()
                    ),
                    "STAGE_WORK_LOG_PATH": str(log_path.resolve()),
                }
            )
            if previous_verdict is not None:
                reviewer_env.update(
                    {
                        "STAGE_PREVIOUS_REVIEW_VERDICT_FILE": str(
                            previous_verdict_file.resolve()
                        ),
                        "STAGE_REVIEW_FAILED_CRITERIA_FILE": str(
                            failed_criteria_file.resolve()
                        ),
                    }
                )
            (
                reviewed,
                review_evidence,
                _review_raw,
                reviewer_seconds,
            ) = timed_run_check(
                reviewer_command,
                args.timeout,
                project_root,
                env=reviewer_env,
            )
            execution_seconds += reviewer_seconds
            state["execution_seconds"] = execution_seconds
            try:
                write_run_state(state_path, state)
            except OSError as exc:
                print_escalation(f"cannot persist reviewer execution time: {exc}")
                return 1
            print(f"Independent reviewer result:\n{review_evidence}")
            try:
                read_work_log(log_path)
            except RuntimeError as exc:
                step_ok = False
                failure = str(exc)
            reviewer_reaped = reap_turn(
                stage_root=stage_root,
                project_root=project_root,
                log_path=log_path,
                item_path=item.path,
                venue=reviewer_venue,
                role="reviewer",
                timeout=args.timeout,
            )
            try:
                write_running_role(
                    state_path,
                    state,
                    item.item_id,
                    in_progress_item_state,
                    None,
                )
            except OSError as exc:
                print_escalation(f"cannot clear reviewer running role: {exc}")
                return 1
            narrow_merge_error = ""
            current_verdict_error = ""
            if previous_verdict is not None:
                current_verdict, current_verdict_error = (
                    load_driver_review_verdict(current_verdict_file)
                )
                if current_verdict_error or current_verdict is None:
                    narrow_merge_error = (
                        current_verdict_error
                        or "narrow review verdict is unavailable"
                    )
                else:
                    narrow_merge_error = merge_narrow_review_verdict(
                        previous_verdict,
                        current_verdict,
                        verdict_file,
                    )
            verdict_error = (
                narrow_merge_error or review_verdict_error(verdict_file)
            )
            reviewer_blocked = bool(
                review_verdict_failures(verdict_file)
            )
            if not reviewed or verdict_error:
                if (
                    previous_verdict is not None
                    and current_verdict_error
                    == "review verdict file is missing"
                ):
                    infrastructure_failed = (
                        retryable_review_infrastructure_failure(
                            close_ok=reviewed,
                            close_output=review_evidence,
                            verdict_file=current_verdict_file,
                        )
                    )
                elif not narrow_merge_error:
                    infrastructure_failed = retryable_review_infrastructure_failure(
                        close_ok=reviewed,
                        close_output=review_evidence,
                        verdict_file=verdict_file,
                    )
                else:
                    infrastructure_failed = False
                review_failure = (
                    verdict_error or "independent reviewer command failed"
                )
                if step_ok:
                    step_ok = False
                    failure = review_failure
                try:
                    append_failure_to_work_log(
                        log_path,
                        role="reviewer",
                        reason=review_failure,
                        evidence=review_evidence,
                    )
                except RuntimeError as exc:
                    failure = f"{failure}; {exc}"
            elif not reviewer_reaped:
                step_ok = False
                failure = "reviewer reap command failed"

    try:
        current_fingerprint = fingerprint(project_root, acceptance_output)
    except RuntimeError as exc:
        try:
            write_running_role(
                state_path,
                state,
                item.item_id,
                state["items"][item.item_id],
                None,
            )
        except OSError as clear_exc:
            print_escalation(
                f"cannot inspect changes for progress: {exc}; "
                f"cannot clear interrupted role: {clear_exc}"
            )
            return 1
        print_escalation(f"cannot inspect changes for progress: {exc}")
        return 1
    previous_fingerprint = item_state["last_fingerprint"]
    no_progress = (
        bool(previous_fingerprint)
        and current_fingerprint == previous_fingerprint
        and not reasoned_no_change
    )
    repeated_unchanged_repository = (
        unchanged_repository
        and bool(item_state.get("last_no_change_fingerprint"))
        and repository_after == item_state["last_no_change_fingerprint"]
    )
    counted_attempt = (
        item_state["attempt_count"]
        if (
            unchanged_repository
            or executor_rejected
            or (not step_ok and infrastructure_failed)
        )
        else attempt
    )
    state["iteration_count"] = iteration
    state["execution_seconds"] = execution_seconds
    state["items"][item.item_id] = {
        "attempt_count": counted_attempt,
        "last_fingerprint": current_fingerprint,
        "last_no_change_fingerprint": (
            repository_after if unchanged_repository else ""
        ),
        "base_head": base_head,
        "executor_changed_paths": changed_paths,
        "running_role": None,
    }
    try:
        write_run_state(state_path, state)
    except OSError as exc:
        print_escalation(f"cannot persist driver run state after execution: {exc}")
        return 1

    if executor_rejected:
        try:
            append_driver_notice_to_work_log(
                log_path,
                reason=EXECUTOR_REJECTION_NOTICE,
                recommended_next_action=EXECUTOR_REJECTION_NEXT_ACTION,
            )
        except RuntimeError as exc:
            print_escalation(str(exc))
            return 1
        print(f"Outcome: {EXECUTOR_REJECTION_NOTICE}")
        print(f"Recommended next action: {EXECUTOR_REJECTION_NEXT_ACTION}")
        return 0

    if unchanged_repository:
        if no_progress or repeated_unchanged_repository:
            print_escalation(
                "NO-PROGRESS repository state matched the previous round"
            )
            return 1
        print(f"Outcome: {UNCHANGED_REPOSITORY_NOTICE}")
        print(f"Recommended next action: {UNCHANGED_REPOSITORY_NEXT_ACTION}")
        return 0

    escalation_reasons: list[str] = []
    if no_progress and not infrastructure_failed:
        escalation_reasons.append("NO-PROGRESS fingerprint matched the previous attempt")
    if reviewer_blocked:
        escalation_reasons.append(failure)
    if limits is not None:
        if (
            not step_ok
            and counted_attempt >= limits["max_attempts_per_item"]
        ):
            escalation_reasons.append("per-item attempt cap reached")
        if not step_ok and iteration >= limits["max_iterations"]:
            escalation_reasons.append("global iteration limit reached")
        if execution_seconds >= limits["max_wall_clock_seconds"]:
            escalation_reasons.append("global execution-time limit exceeded")

    if escalation_reasons:
        print_escalation("; ".join(escalation_reasons))
        return 1
    if step_ok:
        print("Outcome: executor, acceptance, and independent reviewer passed")
        print(f"Recommended next action: {RECOMMEND_PASS}")
        return 0

    if infrastructure_failed:
        print(f"Outcome: {failure}; infrastructure failure did not spend an attempt")
    else:
        print(f"Outcome: {failure}")
    print(
        "Recommended next action: "
        + RECOMMEND_RETRY.format(
            attempt=counted_attempt,
            cap=cap_text(limits, "max_attempts_per_item"),
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
