#!/usr/bin/env python3
"""Run one supervised round: executor, then acceptance, then an independent judge.

Supervised means a person is watching, so this stops and reports rather than
deciding anything a person would want to decide. It never commits, closes,
escalates, promotes, or advances a parent — the unattended loop is where those
belong, because there nobody is there to be asked.

Everything before this ran decided *whether* to run. This is the running, and
what it returns is the driver's exit code.
"""

from __future__ import annotations

import json
import shutil
import subprocess
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
    clear_review_verdict,
    ensure_work_log,
    executor_report_error,
    executor_review_dispositions,
    read_work_log,
    run_check,
    review_verdict_path,
)
from driver_environment import (  # noqa: E402
    check_environment,
    executor_environment,
    project_environment,
)
from driver_git import current_head_or_empty  # noqa: E402
from driver_repository import (  # noqa: E402
    changed_repository_paths,
    cumulative_executor_changed_paths,
    executor_changed_only_work_card,
    fingerprint,
    git_index_path,
    repository_fingerprint,
    repository_path_snapshot,
)
from driver_review import (  # noqa: E402
    infrastructure_failure,
    load_driver_review_verdict,
    merge_narrow_review_verdict,
    retryable_review_infrastructure_failure,
    review_verdict_error,
    review_verdict_failures,
)
from driver_runstate import write_run_state, write_running_role  # noqa: E402
from driver_venues import reap_turn, run_preflight  # noqa: E402
from driver_worklog import (  # noqa: E402
    EXECUTOR_REJECTION_NEXT_ACTION,
    EXECUTOR_REJECTION_NOTICE,
    RECOMMEND_PASS,
    RECOMMEND_RETRY,
    UNCHANGED_REPOSITORY_NEXT_ACTION,
    UNCHANGED_REPOSITORY_NOTICE,
    append_driver_commands_to_work_log,
    append_driver_notice_to_work_log,
    append_failure_to_work_log,
    cap_text,
    print_escalation,
    reconcile_executor_work_log,
)


def run_supervised_round(
    args,
    project_root,
    stage_root,
    item,
    items,
    state,
    state_path,
    item_state,
    attempt,
    iteration,
    execution_seconds,
    limits,
    executor_command,
    reviewer_command,
    reviewer_venue,
    resume_role,
) -> int:
    """Run one executor -> acceptance -> independent-review sequence.

    Everything before this point decided *whether* to run: the target
    resolved, the limits held, the plan printed. This is the running, and
    its return value is the driver's exit code.
    """

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
