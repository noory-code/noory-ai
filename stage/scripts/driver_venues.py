#!/usr/bin/env python3
"""Resolve and run the per-venue commands that surround an executor turn.

A venue can be asked three things besides doing the work: is it healthy before
we start, clean up your background jobs after, and who reviews this if you were
the one who ran it. Each is optional — a venue that declares none simply skips
that step with a warning rather than blocking the round.
"""

from __future__ import annotations

import json
import os
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

from driver_environment import project_environment  # noqa: E402
from driver_worklog import (  # noqa: E402
    append_reap_warning_to_work_log,
    print_preflight_blocker,
)
from close_work import ensure_work_log, run_check  # noqa: E402
from stage_paths import read_settings  # noqa: E402
from driver_subtree import ancestor_chain  # noqa: E402
from stage_work import WorkItem  # noqa: E402


def load_reapers_config(stage_root: Path) -> object:
    """Return the optional venue-to-command map used to reap external turns."""

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return None
    return data.get("reapers") if isinstance(data, dict) else None


def resolve_reap_command(
    reapers: object,
    venue: str,
) -> tuple[str | None, bool, str]:
    """Resolve one venue reaper and distinguish an explicit no-op from absence."""

    normalized_venue = venue.strip().lower()
    if not normalized_venue:
        return None, False, "turn venue must be a non-empty string"
    if reapers is None:
        return None, False, ""
    if not isinstance(reapers, dict):
        return None, False, "reapers must be an object mapping venue -> command"

    normalized: dict[str, str | None] = {}
    for raw_name, raw_command in reapers.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            return None, False, "reapers venue names must be non-empty strings"
        name = raw_name.strip().lower()
        if name in normalized:
            return None, False, f"reapers contains duplicate venue `{name}`"
        if raw_command is None:
            normalized[name] = None
            continue
        if not isinstance(raw_command, str) or not raw_command.strip():
            return (
                None,
                False,
                f"reapers.{name} must be a non-empty command string or null",
            )
        normalized[name] = raw_command
    if normalized_venue not in normalized:
        return None, False, ""
    return normalized[normalized_venue], True, ""


def load_preflights_config(stage_root: Path) -> object:
    """Return the optional venue-to-command map checked before executor turns."""

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return None
    return data.get("preflights") if isinstance(data, dict) else None


def resolve_preflight_command(
    preflights: object,
    venue: str,
) -> tuple[str | None, bool, str]:
    """Resolve one venue preflight and distinguish an explicit no-op from absence."""

    normalized_venue = venue.strip().lower()
    if not normalized_venue:
        return None, False, "executor venue must be a non-empty string"
    if preflights is None:
        return None, False, ""
    if not isinstance(preflights, dict):
        return None, False, "preflights must be an object mapping venue -> command"

    normalized: dict[str, str | None] = {}
    for raw_name, raw_command in preflights.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            return None, False, "preflights venue names must be non-empty strings"
        name = raw_name.strip().lower()
        if name in normalized:
            return None, False, f"preflights contains duplicate venue `{name}`"
        if raw_command is None:
            normalized[name] = None
            continue
        if not isinstance(raw_command, str) or not raw_command.strip():
            return (
                None,
                False,
                f"preflights.{name} must be a non-empty command string or null",
            )
        normalized[name] = raw_command
    if normalized_venue not in normalized:
        return None, False, ""
    return normalized[normalized_venue], True, ""


def preflight_environment(
    item: WorkItem,
    project_root: Path,
    *,
    items: list[WorkItem],
) -> dict[str, str]:
    """Return read-only work context for a venue preflight command."""

    env = project_environment(project_root)
    env.pop("GIT_INDEX_FILE", None)
    env.update(
        {
            "STAGE_WORK_ITEM": item.item_id,
            "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
            "STAGE_PROJECT_ROOT": str(project_root.resolve()),
            "STAGE_WORK_ITEM_ANCESTOR_PATHS": json.dumps(
                [
                    str(ancestor.path.resolve())
                    for ancestor in ancestor_chain(item, items)
                ]
            ),
        }
    )
    return env


def run_preflight(
    *,
    stage_root: Path,
    project_root: Path,
    item: WorkItem,
    items: list[WorkItem],
    timeout: int,
    skip: bool,
) -> bool:
    """Run an optional venue check without creating or spending an attempt."""

    normalized_venue = item.venue.strip().lower()
    if skip:
        warning = (
            "WARNING: preflight skipped by operator; "
            f"preflights.{normalized_venue} was not run"
        )
        log_warning = (
            "WARNING: preflight skipped by operator for recovery; "
            f"preflights.{normalized_venue} was not run"
        )
        try:
            append_reap_warning_to_work_log(
                ensure_work_log(stage_root, item.item_id),
                warning=log_warning,
            )
        except RuntimeError as exc:
            print_preflight_blocker(
                f"cannot record skipped preflight before attempt ({exc})"
            )
            return False
        print(warning)
        return True

    command, configured, config_error = resolve_preflight_command(
        load_preflights_config(stage_root),
        normalized_venue,
    )
    if config_error:
        print_preflight_blocker(
            f"preflights.{normalized_venue} is unusable before attempt "
            f"({config_error})"
        )
        return False
    if command is None:
        if configured:
            return True
        print(
            f"WARNING: preflights.{normalized_venue} is not configured; "
            "continuing without a venue health check"
        )
        return True

    passed, evidence, _raw = run_check(
        command,
        timeout,
        project_root,
        env=preflight_environment(item, project_root, items=items),
    )
    print(f"Preflight result:\n{evidence}")
    if passed:
        return True
    print_preflight_blocker(
        f"preflights.{normalized_venue} failed before attempt; "
        "executor was not started and attempt state was not written"
    )
    return False


def reap_turn(
    *,
    stage_root: Path,
    project_root: Path,
    log_path: Path,
    item_path: Path,
    venue: str,
    role: str,
    timeout: int,
) -> bool:
    """Run an optional venue-owned cleanup command after one external turn."""

    normalized_venue = venue.strip().lower()
    command, configured, config_error = resolve_reap_command(
        load_reapers_config(stage_root),
        normalized_venue,
    )
    if command is None:
        if config_error:
            warning = (
                f"WARNING: reapers.{normalized_venue} is unusable after {role} "
                f"turn ({config_error}); jobs may remain"
            )
        elif configured:
            return True
        else:
            warning = (
                f"WARNING: reapers.{normalized_venue} is not configured after "
                f"{role} turn; jobs may remain"
            )
        print(warning)
        try:
            append_reap_warning_to_work_log(log_path, warning=warning)
        except RuntimeError as exc:
            print(f"WARNING: {exc}")
        return True

    reap_environment = os.environ.copy()
    reap_environment.update(
        {
            "STAGE_WORK_ITEM_PATH": str(item_path.resolve()),
            "STAGE_PROJECT_ROOT": str(project_root.resolve()),
            "STAGE_WORK_LOG_PATH": str(log_path.resolve()),
            "STAGE_TURN_ROLE": role,
        }
    )
    reaped, evidence, _raw = run_check(
        command,
        timeout,
        project_root,
        env=reap_environment,
    )
    if reaped:
        return True

    warning = (
        f"WARNING: reapers.{normalized_venue} failed after {role} turn; "
        "jobs may remain"
    )
    print(warning)
    try:
        append_reap_warning_to_work_log(
            log_path,
            warning=warning,
            evidence=evidence,
        )
    except RuntimeError as exc:
        print(f"WARNING: {exc}")
    return False


def resolve_independent_reviewer_venue(
    review: dict[str, Any],
    item_venue: str,
) -> str | None:
    """Return the venue selected by the validated two-venue reviewer contract."""

    venue = item_venue.strip().lower()
    reviewers = review.get("reviewers")
    if not isinstance(reviewers, dict):
        return None
    differing = [
        raw_name.strip().lower()
        for raw_name in reviewers
        if isinstance(raw_name, str)
        and raw_name.strip()
        and raw_name.strip().lower() != venue
    ]
    return differing[0] if len(differing) == 1 else None
