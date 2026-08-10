#!/usr/bin/env python3
"""Run a whole ready subtree with nobody watching, on a branch of its own.

Nobody is there to answer a question, so every ambiguity has to end the run
rather than guess. The loop keeps going only while each round produces a clear
result: it commits what an executor changed, closes what passed, escalates what
ran out of attempts, and stops the moment a step it cannot judge appears.

Nothing here reaches the base branch. A person reviews the isolated branch and
merges it, which is the one judgement the run deliberately does not make.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import (  # noqa: E402
    clip,
    ensure_work_log,
    executor_report_error,
    executor_review_dispositions,
    read_work_log,
    review_verdict_path,
    run_check,
)
from driver_environment import executor_environment  # noqa: E402
from driver_git import (  # noqa: E402
    commit_item,
    commit_lifecycle,
    create_run_branch,
    current_head,
    restore_item_output,
)
from driver_lifecycle import (  # noqa: E402
    audit_check,
    close_via_close_work,
    current_card_path,
    escalate_via_escalate_work,
    mark_retrospective,
    write_driver_retrospective,
)
from driver_repository import (  # noqa: E402
    cumulative_executor_changed_paths,
    executor_changed_only_work_card,
    executor_widened_work_card_scope,
    fingerprint,
    git_index_path,
    repository_fingerprint,
    repository_path_snapshot,
)
from driver_review import (  # noqa: E402
    infrastructure_failure,
    retryable_review_infrastructure_failure,
    review_verdict_failures,
)
from driver_runstate import (  # noqa: E402
    load_run_state,
    write_run_state,
    write_running_role,
)
from driver_subtree import select_next_unattended_leaf, subtree_limits  # noqa: E402
from driver_venues import (  # noqa: E402
    reap_turn,
    resolve_independent_reviewer_venue,
    run_preflight,
)
from driver_worklog import (  # noqa: E402
    EXECUTOR_REJECTION_NEXT_ACTION,
    EXECUTOR_REJECTION_NOTICE,
    UNCHANGED_REPOSITORY_NEXT_ACTION,
    UNCHANGED_REPOSITORY_NOTICE,
    append_driver_commands_to_work_log,
    append_driver_notice_to_work_log,
    append_failure_to_work_log,
    print_escalation,
    reconcile_executor_work_log,
)
from driver_worktree import (  # noqa: E402
    create_unattended_worktree,
    current_branch,
    discard_worktree,
    preserve_unattended_runtime,
    remove_unattended_worktree,
    seed_unattended_runtime,
    worktree_clean,
)
from stage_paths import (  # noqa: E402
    load_executors_config,
    load_limits_config,
    load_review_config,
    resolve_executor_command,
    resolve_independent_review_command,
)
from stage_record_paths import record_path  # noqa: E402
from stage_work import (  # noqa: E402
    WORK_FINAL_STATUSES,
    load_all_work_items,
    non_terminal_children,
    parse_frontmatter,
    split_scope,
)


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
            raw_scope_after_executor = parse_frontmatter(item.path).get("scope", "")
            scope_after_executor = (
                split_scope(raw_scope_after_executor)
                if isinstance(raw_scope_after_executor, str)
                else ()
            )
            scope_widened = executor_widened_work_card_scope(
                item,
                scope_after_executor,
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
                    scope_after_executor,
                )
            except RuntimeError as exc:
                executor_ok = False
                executor_failure = str(exc)
        if scope_widened:
            before_scope = json.dumps(list(item.scope), ensure_ascii=False)
            after_scope = json.dumps(
                list(scope_after_executor), ensure_ascii=False
            )
            try:
                append_driver_notice_to_work_log(
                    log_path,
                    reason=(
                        "executor widened work item scope: "
                        f"{before_scope} -> {after_scope}"
                    ),
                    recommended_next_action=(
                        "have a human decide whether to keep the widened scope "
                        "before landing"
                    ),
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
                return 1
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

        commit_ok, commit_message, omitted_commit_paths = commit_item(
            project_root, item, base_head
        )
        if not commit_ok:
            discard_worktree(project_root)
            if not escalate_and_commit(
                project_root, item.item_id, f"commit failed: {commit_message}", cmd_timeout
            ):
                return 1
            continue
        if omitted_commit_paths:
            try:
                append_driver_notice_to_work_log(
                    log_path,
                    reason=(
                        "item commit omitted missing declared paths: "
                        + json.dumps(omitted_commit_paths, ensure_ascii=False)
                    ),
                    recommended_next_action=(
                        "continue with the remaining declared paths"
                    ),
                )
            except RuntimeError as exc:
                print_escalation(str(exc))
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
