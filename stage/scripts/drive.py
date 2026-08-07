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
    EXECUTOR_REJECTION_NEXT_ACTION,
    EXECUTOR_REJECTION_NOTICE,
    UNCHANGED_REPOSITORY_NEXT_ACTION,
    UNCHANGED_REPOSITORY_NOTICE,
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
from driver_lifecycle import (  # noqa: E402
    AUDIT,
    CLOSE_WORK,
    ESCALATE_WORK,
    RETRO_SECTIONS,
    audit_check,
    close_via_close_work,
    current_card_path,
    escalate_via_escalate_work,
    mark_retrospective,
    retrospective_id_for_work_item,
    set_frontmatter_field,
    shell_command,
    write_driver_retrospective,
)
from driver_runstate import (  # noqa: E402
    interrupted_item,
    load_run_state,
    new_run_state,
    reset_attempts,
    write_run_state,
    write_running_role,
)
from driver_unattended import (  # noqa: E402
    close_ready_ancestors,
    escalate_and_commit,
    remaining_timeout,
    run_unattended,
    run_unattended_in_worktree,
)
from driver_supervised import run_supervised_round  # noqa: E402
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


AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"


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
    return run_supervised_round(
        args=args,
        project_root=project_root,
        stage_root=stage_root,
        item=item,
        items=items,
        state=state,
        state_path=state_path,
        item_state=item_state,
        attempt=attempt,
        iteration=iteration,
        execution_seconds=execution_seconds,
        limits=limits,
        executor_command=executor_command,
        reviewer_command=reviewer_command,
        reviewer_venue=reviewer_venue,
        resume_role=resume_role,
    )


if __name__ == "__main__":
    raise SystemExit(main())
