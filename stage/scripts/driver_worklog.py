#!/usr/bin/env python3
"""Record what a round did, in the shared work log and on the screen.

The work log outlives the session; the screen does not. Anything a person will
need after the run ends — the commands that were tried, why a round stopped,
what an executor left behind — goes to the log. The screen carries the same
facts for whoever is watching now.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import clip, ensure_work_log, read_work_log  # noqa: E402
from stage_work import WorkItem  # noqa: E402

# What a person should do next, in the driver's own words. These are the only
# recommendations a round prints, so they live where the printing does.
RECOMMEND_PASS = (
    "verification+judge passed → ready to commit + close_work"
)
RECOMMEND_RETRY = "failed, retry (attempt {attempt}/{cap})"
RECOMMEND_ESCALATE = (
    "attempt cap reached / no progress / global limit exceeded → escalate_work"
)

# Two outcomes that look like failure and are not. An executor that changed
# nothing may have found the work already done, and one that changed only its
# own card is rejecting the card. Both are reported without spending an attempt.
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


def append_failure_to_work_log(
    log_path: Path,
    *,
    role: str,
    reason: str,
    evidence: str,
) -> None:
    """Append one driver-observed failure without replacing role-authored reports."""

    output = clip(evidence) or "(no output)"
    entry = (
        "\n### Driver failure\n"
        f"Role: {role}\n"
        f"Reason: {reason}\n"
        "Output:\n\n"
        "```text\n"
        f"{output}\n"
        "```\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(entry)
    except OSError as exc:
        raise RuntimeError(f"cannot append failure to work log {log_path}: {exc}") from exc


def append_driver_commands_to_work_log(
    log_path: Path,
    *,
    executor_command: str,
    reviewer_command: str,
) -> None:
    """Append the exact configured commands selected for one driver round."""

    entry = (
        "\n### Driver commands\n"
        f"Executor command: {json.dumps(executor_command)}\n"
        f"Reviewer command: {json.dumps(reviewer_command)}\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(entry)
    except OSError as exc:
        raise RuntimeError(
            f"cannot append driver commands to work log {log_path}: {exc}"
        ) from exc


def append_driver_notice_to_work_log(
    log_path: Path,
    *,
    reason: str,
    recommended_next_action: str,
) -> None:
    """Append a non-failure reason why an unattended driver stopped."""

    entry = (
        "\n### Driver notice\n"
        f"Reason: {reason}\n"
        f"Recommended next action: {recommended_next_action}\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(entry)
    except OSError as exc:
        raise RuntimeError(f"cannot append notice to work log {log_path}: {exc}") from exc


def reconcile_executor_work_log(
    log_path: Path,
    durable_log: str,
    attempt_log: str,
    current_log: str,
) -> tuple[str, str]:
    """Restore this attempt's driver commands after an intact stale-log rewrite."""

    if current_log.startswith(attempt_log):
        return current_log, ""
    if not current_log.startswith(durable_log):
        error = "executor rewrote existing work log content instead of appending"
        try:
            log_path.write_text(attempt_log, encoding="utf-8")
        except OSError as exc:
            return current_log, f"{error}; cannot restore prior work log: {exc}"
        return attempt_log, error
    reconciled = attempt_log + current_log[len(durable_log) :]
    try:
        log_path.write_text(reconciled, encoding="utf-8")
    except OSError as exc:
        return current_log, f"cannot restore driver commands in work log {log_path}: {exc}"
    return reconciled, ""


def append_reap_warning_to_work_log(
    log_path: Path,
    *,
    warning: str,
    evidence: str = "",
) -> None:
    """Append cleanup uncertainty without changing the turn's original verdict."""

    entry = f"\n### Driver warning\n{warning}\n"
    if evidence:
        entry += (
            "Output:\n\n"
            "```text\n"
            f"{clip(evidence)}\n"
            "```\n"
        )
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(entry)
    except OSError as exc:
        raise RuntimeError(
            f"cannot append reap warning to work log {log_path}: {exc}"
        ) from exc


def print_escalation(reason: str) -> None:
    print(f"Outcome: blocked — {reason}")
    print(f"Recommended next action: {RECOMMEND_ESCALATE}")


def print_preflight_blocker(reason: str) -> None:
    """Report venue infrastructure failure without blaming the selected card."""

    print(f"Outcome: blocked — {reason}")
    print(
        "Recommended next action: repair the venue preflight, or verify the "
        "venue manually and rerun with --skip-preflight"
    )


def cap_text(limits: dict[str, int] | None, key: str) -> str:
    return str(limits[key]) if limits is not None else "unlimited"
