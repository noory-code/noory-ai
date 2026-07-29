#!/usr/bin/env python3
"""Plan or execute one supervised Stage driver step.

The driver selects a READY leaf from the requested target: an eligible target
itself when it has no unfinished children, otherwise one of its eligible
children. Dry run is the default and has no side effects. ``--execute`` runs
exactly one executor -> acceptance -> independent-review sequence and records
runtime attempt state, but never commits, closes, escalates, promotes, creates
work, or advances a parent.
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

from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from stage_record_paths import record_path, record_paths  # noqa: E402
from close_work import (  # noqa: E402
    clip,
    ensure_work_log,
    executor_report_error,
    executor_review_dispositions,
    latest_review_failures,
    read_work_log,
    reviewer_report_error,
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
)


WORK_ID_RE = re.compile(r"^W-[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9_-]*)?$")
BLOCK_RE = re.compile(r"(?m)^BLOCK:")
STAGE_RUNTIME_PREFIX = ".stage/.runtime/"
RECOMMEND_PASS = (
    "verification+judge passed → ready to commit + close_work"
)
RECOMMEND_RETRY = "failed, retry (attempt {attempt}/{cap})"
RECOMMEND_ESCALATE = (
    "attempt cap reached / no progress / global limit exceeded → escalate_work"
)
UNCHANGED_REPOSITORY_FAILURE = (
    "executor left repository state unchanged; if the work is already complete, "
    "run close_work.py manually"
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
        help="Run the whole ready subtree unattended on an isolated branch (requires a limits config).",
    )
    parser.add_argument(
        "--timeout", type=int, default=900, help="Per-command timeout in seconds."
    )
    parser.add_argument("target", help="Existing parent or leaf work item id (W-*).")
    return parser.parse_args()


def select_next_ready_leaf(
    target_id: str, items: list[WorkItem]
) -> WorkItem | None:
    """Choose a READY leaf anywhere below the requested hierarchy root."""

    by_id = {item.item_id: item for item in items}
    candidates = (
        item
        for item in items
        if item.status in {"active", "review"}
        and item.acceptance
        and not non_terminal_children(item.item_id, items)
        and (
            item.item_id == target_id
            or is_in_subtree(item, target_id, by_id)
        )
        and ancestors_are_runnable(item, target_id, by_id)
    )
    return next(
        iter(sorted(candidates, key=lambda item: (item.item_id, item.path.as_posix()))),
        None,
    )


def new_run_state(target_id: str, now: float) -> dict[str, Any]:
    return {
        "target": target_id,
        "started_at_unix": now,
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
        base_head = item_state.get("base_head", "")
        base_repository_paths = item_state.get("base_repository_paths")
        executor_changed_paths = item_state.get("executor_changed_paths", [])
        if type(attempt_count) is not int or attempt_count < 0:
            return None, (
                f"driver run state {item_id}.attempt_count must be a "
                "non-negative integer"
            )
        if not isinstance(fingerprint, str):
            return None, (
                f"driver run state {item_id}.last_fingerprint must be a string"
            )
        if not isinstance(base_head, str):
            return None, f"driver run state {item_id}.base_head must be a string"
        if base_repository_paths is not None and (
            not isinstance(base_repository_paths, dict)
            or any(
                not isinstance(path, str) or not isinstance(value, str)
                for path, value in base_repository_paths.items()
            )
        ):
            return None, (
                f"driver run state {item_id}.base_repository_paths must be "
                "a string-to-string object"
            )
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


def git_untracked_paths(project_root: Path) -> tuple[set[str], str]:
    """Return untracked, non-ignored file paths without changing the index."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=str(project_root),
            capture_output=True,
        )
    except OSError as exc:
        return set(), str(exc)
    if result.returncode != 0:
        return set(), (
            result.stderr.decode(errors="replace").strip()
            or f"git ls-files failed with exit code {result.returncode}"
        )
    return {
        os.fsdecode(raw_path)
        for raw_path in result.stdout.split(b"\0")
        if raw_path
        and not os.fsdecode(raw_path).startswith(STAGE_RUNTIME_PREFIX)
    }, ""


def git_index_entries(project_root: Path) -> tuple[dict[str, str], str]:
    """Return real-index metadata by path without changing the index."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--stage", "-z"],
            cwd=str(project_root),
            capture_output=True,
        )
    except OSError as exc:
        return {}, str(exc)
    if result.returncode != 0:
        return {}, (
            result.stderr.decode(errors="replace").strip()
            or f"git ls-files --stage failed with exit code {result.returncode}"
        )

    entries: dict[str, str] = {}
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        metadata, separator, raw_path = raw_entry.partition(b"\t")
        if not separator:
            return {}, "git ls-files --stage returned an invalid entry"
        path = os.fsdecode(raw_path)
        rendered_metadata = metadata.decode(errors="replace")
        existing = entries.get(path)
        entries[path] = (
            rendered_metadata
            if existing is None
            else f"{existing}\n{rendered_metadata}"
        )
    return entries, ""


def worktree_path_fingerprint(path: Path) -> str:
    """Fingerprint one working-tree path, including deletion and executable state."""

    try:
        if path.is_symlink():
            return f"symlink\0{path.readlink()}"
        if not path.exists():
            return "missing"
        if path.is_file():
            executable_bits = path.stat().st_mode & 0o111
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return f"file\0{executable_bits:o}\0{digest}"
        if path.is_dir():
            return "directory"
        return "other"
    except OSError as exc:
        return f"unreadable:{type(exc).__name__}"


def repository_path_snapshot(project_root: Path) -> dict[str, str]:
    """Snapshot path-level repository state using the driver's real Git environment."""

    index_path, index_error = git_index_path(project_root)
    if index_error:
        raise RuntimeError(index_error)
    if index_path is None:
        return {}

    index_entries, entries_error = git_index_entries(project_root)
    if entries_error:
        raise RuntimeError(entries_error)
    untracked_paths, untracked_error = git_untracked_paths(project_root)
    if untracked_error:
        raise RuntimeError(untracked_error)

    snapshot: dict[str, str] = {}
    for relative in sorted(set(index_entries) | untracked_paths):
        snapshot[relative] = (
            index_entries.get(relative, "untracked")
            + "\0"
            + worktree_path_fingerprint(project_root / relative)
        )
    return snapshot


def changed_repository_paths(
    before: dict[str, str],
    after: dict[str, str],
) -> list[str]:
    """Return deterministic paths changed between two repository snapshots."""

    return sorted(
        relative
        for relative in set(before) | set(after)
        if before.get(relative) != after.get(relative)
    )


def cumulative_executor_changed_paths(
    previous: list[str],
    before_executor: dict[str, str],
    after_executor: dict[str, str],
) -> list[str]:
    """Accumulate only paths observed while an executor was running."""

    return sorted(
        set(previous)
        | set(changed_repository_paths(before_executor, after_executor))
    )


def git_diff(project_root: Path) -> str:
    """Return all changes for progress detection; fail if untracked paths are unknown."""

    index_path, index_error = git_index_path(project_root)
    if index_error:
        raise RuntimeError(index_error)
    if index_path is None:
        return "\0NO-GIT-WORKTREE\0"

    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--binary", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RuntimeError(str(exc)) from exc
    if result.returncode == 0:
        tracked_diff = result.stdout
    else:
        head_exists, head_error = git_head_exists(project_root)
        if head_error:
            raise RuntimeError(head_error)
        if head_exists:
            raise RuntimeError(
                result.stderr.strip()
                or f"git diff HEAD failed with exit code {result.returncode}"
            )
        unborn_diffs: list[str] = []
        for extra_args in (["--cached"], []):
            try:
                unborn_result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--no-ext-diff",
                        "--binary",
                        *extra_args,
                    ],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                )
            except OSError as exc:
                raise RuntimeError(str(exc)) from exc
            if unborn_result.returncode != 0:
                raise RuntimeError(
                    unborn_result.stderr.strip()
                    or (
                        "git diff "
                        f"{' '.join(extra_args) or 'worktree'} failed with exit code "
                        f"{unborn_result.returncode}"
                    )
                )
            unborn_diffs.append(unborn_result.stdout)
        tracked_diff = (
            "\0UNBORN-STAGED\0"
            + unborn_diffs[0]
            + "\0UNBORN-UNSTAGED\0"
            + unborn_diffs[1]
        )

    untracked_paths, untracked_error = git_untracked_paths(project_root)
    if untracked_error:
        raise RuntimeError(untracked_error)
    untracked: list[str] = []
    for relative in sorted(untracked_paths):
        path = project_root / relative
        try:
            content = path.read_bytes()
        except OSError as exc:
            digest = f"unreadable:{type(exc).__name__}"
        else:
            digest = hashlib.sha256(content).hexdigest()
        untracked.append(f"{relative}\0{digest}")
    return tracked_diff + "\0UNTRACKED\0" + "\0".join(untracked)


def git_index_path(project_root: Path) -> tuple[Path | None, str]:
    """Resolve the repository index, or return None when the root is not a Git worktree."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, ""
    raw_path = Path(result.stdout.strip())
    return (
        raw_path if raw_path.is_absolute() else project_root / raw_path,
        "",
    )


def git_head_exists(project_root: Path) -> tuple[bool, str]:
    """Report whether HEAD resolves, distinguishing an unborn branch from Git failure."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    if result.returncode == 1:
        return False, ""
    return False, (
        result.stderr.strip()
        or f"git rev-parse HEAD failed with exit code {result.returncode}"
    )


def fingerprint(project_root: Path, acceptance_output: list[str]) -> str:
    payload = git_diff(project_root) + "\0" + "\n".join(acceptance_output)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def repository_fingerprint(project_root: Path) -> str:
    """Fingerprint repository state without executor testimony or verification output."""

    return hashlib.sha256(git_diff(project_root).encode("utf-8")).hexdigest()


def executor_environment(
    item: WorkItem,
    project_root: Path,
    work_log_path: Path,
    executor_index_path: Path | None = None,
    *,
    items: list[WorkItem] | None = None,
) -> dict[str, str]:
    """Return the inherited environment plus the selected work item context."""

    env = os.environ.copy()
    env.update(
        {
            "STAGE_WORK_ITEM": item.item_id,
            "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
            "STAGE_PROJECT_ROOT": str(project_root.resolve()),
            "STAGE_WORK_LOG_PATH": str(work_log_path.resolve()),
            "STAGE_WORK_ITEM_ANCESTOR_PATHS": json.dumps(
                [
                    str(ancestor.path.resolve())
                    for ancestor in ancestor_chain(item, items or [])
                ]
            ),
        }
    )
    if executor_index_path is not None:
        env["GIT_INDEX_FILE"] = str(executor_index_path.resolve())
    return env


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


def cap_text(limits: dict[str, int] | None, key: str) -> str:
    return str(limits[key]) if limits is not None else "unlimited"


def print_escalation(reason: str) -> None:
    print(f"Outcome: blocked — {reason}")
    print(f"Recommended next action: {RECOMMEND_ESCALATE}")


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


def print_plan(
    *,
    execute: bool,
    target_id: str,
    item: WorkItem,
    executor_command: str,
    reviewer_command: str,
    attempt: int,
    iteration: int,
    elapsed: float,
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
    wall_cap = (
        f"{limits['max_wall_clock_seconds']}s"
        if limits is not None
        else "unlimited"
    )
    print(f"Wall clock: {int(elapsed)}s/{wall_cap}")


def limit_blocker(
    limits: dict[str, int] | None,
    *,
    attempt: int,
    iteration: int,
    elapsed: float,
) -> str:
    if limits is None:
        return ""
    if attempt > limits["max_attempts_per_item"]:
        return "per-item attempt cap reached before execution"
    if iteration > limits["max_iterations"]:
        return "global iteration limit exceeded before execution"
    if elapsed >= limits["max_wall_clock_seconds"]:
        return "global wall-clock limit exceeded before execution"
    return ""


CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ESCALATE_WORK = STAGE_ROOT / "scripts" / "escalate_work.py"
RETRO_ID_RE = re.compile(r"^R-(\d+)(?:-.*)?\.md$")
RETRO_SECTIONS = (
    "Work",
    "Decision points",
    "Principles applied",
    "Context that helped",
    "Context that was missing",
    "Next changes",
    "Promotion decision",
)


def run_git(project_root: Path, args: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run one git command; return (ok, combined output). Never raises."""

    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"git {' '.join(args[:2])} timed out after {timeout}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def create_run_branch(project_root: Path, target_id: str, now: float) -> tuple[str, str]:
    """Create and check out an isolated run branch; NEVER commit to the base branch.

    Returns (branch_name, error). An existing branch (idempotent re-run) is
    checked out rather than recreated.
    """

    branch = f"stage/driver/{target_id}-{int(now)}"
    exists, _ = run_git(project_root, ["rev-parse", "--verify", "--quiet", branch])
    verb = ["checkout", branch] if exists else ["checkout", "-b", branch]
    ok, out = run_git(project_root, verb)
    if not ok:
        return "", f"cannot create/checkout run branch {branch}: {out.strip()}"
    return branch, ""


def commit_item(
    project_root: Path,
    item: WorkItem,
    base_head: str = "",
) -> tuple[bool, str]:
    """Replace prior round checkpoints with one cumulative item commit."""

    if not current_branch(project_root).startswith("stage/driver/"):
        return False, "refusing item commit: HEAD is not on a stage/driver run branch"
    if base_head:
        ok, current = run_git(project_root, ["rev-parse", "HEAD"])
        if not ok:
            return False, f"cannot resolve item checkpoint HEAD: {current.strip()}"
        if current.strip() != base_head:
            ok, out = run_git(project_root, ["reset", "--soft", base_head])
            if not ok:
                return False, f"cannot squash prior item checkpoints: {out.strip()}"
    scope_paths = [path for path in item.scope if path]
    if scope_paths:
        ok, out = run_git(project_root, ["add", "--", *scope_paths])
        if not ok:
            return False, f"git add failed: {out.strip()}"
    ok, out = run_git(
        project_root,
        ["commit", "-m", f"driver: {item.item_id} executor output"],
    )
    if not ok and "nothing to commit" in out:
        return True, "nothing to commit"
    return (True, "") if ok else (False, f"git commit failed: {out.strip()}")


def restore_item_output(project_root: Path, base_head: str) -> tuple[bool, str]:
    """Remove item checkpoint commits while retaining their files for human handoff."""

    ok, out = run_git(project_root, ["reset", "--mixed", base_head])
    return (True, "") if ok else (
        False,
        f"cannot restore uncommitted item output at attempt cap: {out.strip()}",
    )


def current_head(project_root: Path) -> tuple[str, str]:
    ok, out = run_git(project_root, ["rev-parse", "HEAD"])
    return (out.strip(), "") if ok else ("", f"cannot resolve HEAD: {out.strip()}")


def current_head_or_empty(project_root: Path) -> tuple[str, str]:
    """Return HEAD, or an empty basis for an unborn/non-Git repository."""

    index_path, index_error = git_index_path(project_root)
    if index_error:
        return "", index_error
    if index_path is None:
        return "", ""
    head_exists, head_error = git_head_exists(project_root)
    if head_error:
        return "", head_error
    if not head_exists:
        return "", ""
    return current_head(project_root)


def infrastructure_failure(output: str) -> bool:
    """Recognize a command transport/tool failure that must not spend a work round."""

    lowered = output.lower()
    return any(
        marker in lowered
        for marker in (
            "timed out",
            "command not found",
            "[exit 126]",
            "[exit 127]",
            "terminated by signal",
            "killed by signal",
        )
    )


def next_retro_id(stage_root: Path) -> str:
    highest = 0
    for relative in ("work/retrospectives", "official/work/archive/retrospectives"):
        root = stage_root / relative
        for path in record_paths(root, pattern="R-*.md") if root.exists() else ():
            match = RETRO_ID_RE.fullmatch(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"R-{highest + 1:08d}"


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

    retro_id = next_retro_id(stage_root)
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
        "Promotion decision": (
            f"{note}: 항목 Verification의 결과를 따른다(close_work가 acceptance·독립 판정 통과 시에만 completed로 스탬프)."
        ),
    }
    body = f"---\nid: {retro_id}\nwork_item: {item.item_id}\n---\n\n# {retro_id} {item.item_id} 무인 드라이버 회고\n"
    for heading in RETRO_SECTIONS:
        body += f"\n## {heading}\n\n{sections[heading]}\n"
    path = record_path(stage_root / "work" / "retrospectives", retro_id)
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
    project_root: Path, item_id: str, extra_checks: list[str], timeout: int
) -> tuple[bool, str]:
    """Reuse the reviewed close_work.py: acceptance + (autonomous) independent review + close."""

    command = [
        sys.executable,
        str(CLOSE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--promotion",
        "approved",
        "--timeout",
        str(timeout),
    ]
    for check in extra_checks:
        command += ["--check", check]
    try:
        proc = subprocess.run(
            command, cwd=str(project_root), capture_output=True, text=True, timeout=timeout + 60
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


def is_in_subtree(item: WorkItem, target_id: str, by_id: dict[str, WorkItem]) -> bool:
    """Whether `item` is a descendant of `target_id` (following the parent chain).

    Bounded by the number of items so a malformed cycle cannot spin forever.
    """

    seen: set[str] = set()
    parent = item.parent
    for _ in range(len(by_id) + 1):
        if not parent or parent in seen:
            return False
        if parent == target_id:
            return True
        seen.add(parent)
        ancestor = by_id.get(parent)
        if ancestor is None:
            return False
        parent = ancestor.parent
    return False


def ancestor_chain(item: WorkItem, items: list[WorkItem]) -> list[WorkItem]:
    """Return known ancestors in root-first order."""

    by_id = {candidate.item_id: candidate for candidate in items}
    ancestors: list[WorkItem] = []
    seen: set[str] = set()
    parent_id = item.parent
    while parent_id and parent_id not in seen:
        seen.add(parent_id)
        parent = by_id.get(parent_id)
        if parent is None:
            break
        ancestors.append(parent)
        parent_id = parent.parent
    ancestors.reverse()
    return ancestors


def ancestors_are_runnable(
    item: WorkItem,
    target_id: str,
    by_id: dict[str, WorkItem],
) -> bool:
    """Blocked/final ancestors suppress only their own descendant branch."""

    current = item
    seen: set[str] = set()
    while current.item_id != target_id:
        parent_id = current.parent
        if not parent_id or parent_id in seen:
            return False
        seen.add(parent_id)
        parent = by_id.get(parent_id)
        if parent is None or parent.status not in {"active", "review"}:
            return False
        current = parent
    return current.status in {"active", "review"}


def subtree_limits(
    configured: dict[str, int],
    target_id: str,
    items: list[WorkItem],
    *,
    per_action_seconds: int,
) -> dict[str, int]:
    """Scale global ceilings to the number of unfinished leaves in the subtree."""

    by_id = {item.item_id: item for item in items}
    action_count = sum(
        1
        for item in items
        if item.status not in WORK_FINAL_STATUSES
        and not non_terminal_children(item.item_id, items)
        and (
            item.item_id == target_id
            or is_in_subtree(item, target_id, by_id)
        )
    )
    action_count = max(1, action_count)
    return {
        "max_attempts_per_item": configured["max_attempts_per_item"],
        "max_iterations": max(
            configured["max_iterations"],
            action_count * configured["max_attempts_per_item"],
        ),
        "max_wall_clock_seconds": max(
            configured["max_wall_clock_seconds"],
            action_count * per_action_seconds,
        ),
    }


def select_next_unattended_leaf(target_id: str, items: list[WorkItem]) -> WorkItem | None:
    """Choose the target leaf or an eligible leaf in its subtree.

    Eligibility remains AUTONOMOUS (so close_work runs the mandatory independent
    review), `active` (not terminal, not blocked — escalated items are not
    retried), non-empty acceptance, and leaf readiness.
    """

    by_id = {item.item_id: item for item in items}
    if non_terminal_children(target_id, items):
        candidates = (
            item
            for item in items
            if item.status == "active"
            and item.autonomous
            and item.acceptance
            and not non_terminal_children(item.item_id, items)
            and is_in_subtree(item, target_id, by_id)
            and ancestors_are_runnable(item, target_id, by_id)
        )
    else:
        candidates = (
            item
            for item in items
            if item.item_id == target_id
            and item.status == "active"
            and item.autonomous
            and item.acceptance
        )
    return next(
        iter(sorted(candidates, key=lambda item: (item.item_id, item.path.as_posix()))),
        None,
    )


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
        ok, out = close_via_close_work(project_root, current, checks, timeout)
        if not ok:
            return closed, f"{current}: parent close failed: {out.strip()[:200]}"
        closed.append(current)
        current = "" if current == target_id else parent.parent
    return closed, ""


def current_branch(project_root: Path) -> str:
    ok, out = run_git(project_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if ok else ""


def worktree_clean(project_root: Path) -> bool:
    ok, out = run_git(project_root, ["status", "--porcelain"])
    return ok and out.strip() == ""


def discard_worktree(project_root: Path) -> None:
    """Drop a failed attempt's uncommitted changes so the next iteration starts clean."""

    run_git(project_root, ["checkout", "--", "."])
    run_git(
        project_root,
        ["clean", "-fdq", "-e", f"/{STAGE_RUNTIME_PREFIX}"],
    )


def commit_lifecycle(project_root: Path, message: str) -> tuple[bool, str]:
    """Commit the Stage lifecycle records (.stage/) to the run branch — never the base branch."""

    if not current_branch(project_root).startswith("stage/driver/"):
        return False, "refusing lifecycle commit: HEAD is not on a stage/driver run branch"
    ok, out = run_git(
        project_root,
        ["add", "--update", "--", ".stage"],
    )
    if not ok:
        return False, f"git add tracked .stage paths failed: {out.strip()}"
    ok, out = run_git(
        project_root,
        ["ls-files", "--others", "--exclude-standard", "-z", "--", ".stage"],
    )
    if not ok:
        return False, f"cannot list untracked lifecycle paths: {out.strip()}"
    untracked_paths = [
        path
        for path in out.split("\0")
        if path and not path.startswith(STAGE_RUNTIME_PREFIX)
    ]
    if untracked_paths:
        ok, out = run_git(project_root, ["add", "--", *untracked_paths])
        if not ok:
            return False, f"git add untracked lifecycle paths failed: {out.strip()}"
    ok, staged_paths = run_git(
        project_root,
        ["diff", "--cached", "--name-only"],
    )
    if not ok:
        return False, f"cannot inspect staged lifecycle paths: {staged_paths.strip()}"
    if not staged_paths.strip():
        return True, "nothing to commit"
    ok, out = run_git(project_root, ["commit", "-m", message])
    return (True, "") if ok else (False, f"git commit failed: {out.strip()}")


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


def run_unattended(args: argparse.Namespace, project_root: Path, stage_root: Path, now: float) -> int:
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
        per_action_seconds=args.timeout,
    )
    # A dirty index/worktree would leak unrelated changes into item commits.
    if not worktree_clean(project_root):
        print_escalation("working tree/index is not clean; commit or stash before an unattended run")
        return 1

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
        iteration += 1

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
            log_before = read_work_log(log_path)
            pending_findings = latest_review_failures(log_before)
            repository_before = repository_fingerprint(project_root)
            repository_paths_before = repository_path_snapshot(project_root)
            executor_changed_paths = item_state.get(
                "executor_changed_paths",
                [],
            )
        except RuntimeError as exc:
            print_escalation(f"cannot prepare executor observation: {exc}")
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
                    executor_index if index_path is not None else None,
                    items=items,
                ),
            )
        try:
            log_after_executor = read_work_log(log_path)
            executor_log_error = ""
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
        elif (
            executor_ok
            and repository_after == repository_before
            and not reasoned_no_change
        ):
            executor_ok = False
            executor_failure = UNCHANGED_REPOSITORY_FAILURE
        elif executor_ok and report_error:
            executor_ok = False
            executor_failure = report_error
        no_progress = (
            bool(item_state["last_fingerprint"]) and current_fingerprint == item_state["last_fingerprint"]
        )
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        counted_attempt = item_state["attempt_count"] if infrastructure_failed else attempt
        state["items"][item.item_id] = {
            "attempt_count": counted_attempt,
            "last_fingerprint": current_fingerprint,
            "base_head": base_head,
            "executor_changed_paths": (
                changed_paths if executor_ok else executor_changed_paths
            ),
        }
        write_run_state(state_path, state)

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
            load_review_config(stage_root),
            item.venue,
        )
        while True:
            close_ok, close_out = close_via_close_work(
                project_root,
                item.item_id,
                [],
                cmd_timeout,
            )
            try:
                log_after_close = read_work_log(log_path)
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
            close_infrastructure_failure = (
                not close_ok
                and infrastructure_failure(close_out)
                and not latest_review_failures(log_after_close)
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


def main() -> int:
    args = parse_args()
    if args.timeout <= 0:
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

    if args.unattended:
        return run_unattended(args, project_root, stage_root, time.time())

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
            per_action_seconds=args.timeout,
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

    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    now = time.time()
    state, state_error = load_run_state(state_path, args.target, now)
    if state_error or state is None:
        print_escalation(state_error or "driver run state is unavailable")
        return 1

    item_state = state["items"].get(
        item.item_id,
        {"attempt_count": 0, "last_fingerprint": "", "base_head": ""},
    )
    attempt = item_state["attempt_count"] + 1
    iteration = state["iteration_count"] + 1
    elapsed = max(0.0, now - state["started_at_unix"])
    print_plan(
        execute=args.execute,
        target_id=args.target,
        item=item,
        executor_command=executor_command,
        reviewer_command=reviewer_command,
        attempt=attempt,
        iteration=iteration,
        elapsed=elapsed,
        limits=limits,
    )

    blocker = limit_blocker(
        limits, attempt=attempt, iteration=iteration, elapsed=elapsed
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
    if not args.execute:
        print("Outcome: plan only — no commands ran and no run state was written")
        return 0

    if not item_state.get("base_head"):
        base_head, head_error = current_head_or_empty(project_root)
        if head_error:
            print_escalation(head_error)
            return 1
        item_state["base_head"] = base_head
    base_head = item_state["base_head"]

    step_ok = True
    failure = ""
    reviewer_blocked = False
    acceptance_output: list[str] = []
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
        log_before = read_work_log(log_path)
        repository_before = repository_fingerprint(project_root)
        repository_paths_before = repository_path_snapshot(project_root)
    except RuntimeError as exc:
        print_escalation(f"cannot prepare executor observation: {exc}")
        return 1

    with tempfile.TemporaryDirectory(prefix="stage-drive-index-") as temporary:
        temporary_root = Path(temporary)
        executor_index = temporary_root / "executor-index"
        changed_paths_file = temporary_root / "review-changed-paths.json"
        if index_existed and index_path is not None:
            try:
                shutil.copyfile(index_path, executor_index)
            except OSError as exc:
                print_escalation(
                    f"cannot prepare disposable Git index for executor: {exc}"
                )
                return 1

        executor_ok, executor_evidence, _executor_raw = run_check(
            executor_command,
            args.timeout,
            project_root,
            env=executor_environment(
                item,
                project_root,
                log_path,
                executor_index if index_path is not None else None,
                items=items,
            ),
        )
        print(f"Executor result:\n{executor_evidence}")
        try:
            log_after_executor = read_work_log(log_path)
            executor_log_error = ""
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
            timeout=args.timeout,
        )

        try:
            repository_after = repository_fingerprint(project_root)
            repository_paths_after = repository_path_snapshot(project_root)
            changed_paths = cumulative_executor_changed_paths(
                changed_paths,
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
            elif not executor_reaped:
                step_ok = False
                failure = (
                    "executor reap command failed"
                    if executor_ok
                    else "executor command and reap command failed"
                )
            elif not executor_ok:
                step_ok = False
                failure = "executor command failed"
            elif repository_after == repository_before:
                step_ok = False
                failure = UNCHANGED_REPOSITORY_FAILURE
            else:
                try:
                    changed_paths_file.write_text(
                        json.dumps(changed_paths, indent=2) + "\n",
                        encoding="utf-8",
                    )
                except OSError as exc:
                    step_ok = False
                    failure = (
                        "cannot write driver-observed paths for review: "
                        f"{exc}"
                    )
                if step_ok:
                    report_error = executor_report_error(
                        log_before,
                        log_after_executor,
                        changed_paths,
                        ignored_paths=[
                            log_path.relative_to(project_root).as_posix()
                        ],
                    )
                    if report_error:
                        step_ok = False
                        failure = report_error

        if step_ok and not changed_paths:
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

        if step_ok:
            for command in item.acceptance:
                accepted, evidence, raw = run_check(
                    command, args.timeout, project_root
                )
                acceptance_output.append(raw)
                print(f"Acceptance result:\n{evidence}")
                if not accepted:
                    step_ok = False
                    failure = "acceptance check failed"
                    break

        if step_ok:
            reviewer_env = os.environ.copy()
            reviewer_env.pop("GIT_INDEX_FILE", None)
            reviewer_env.update(
                {
                    "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
                    "STAGE_CHANGED_PATHS_FILE": str(changed_paths_file.resolve()),
                    "STAGE_WORK_LOG_PATH": str(log_path.resolve()),
                }
            )
            log_before_review = read_work_log(log_path)
            reviewed, review_evidence, review_raw = run_check(
                reviewer_command,
                args.timeout,
                project_root,
                env=reviewer_env,
            )
            print(f"Independent reviewer result:\n{review_evidence}")
            try:
                log_after_review = read_work_log(log_path)
            except RuntimeError as exc:
                step_ok = False
                failure = str(exc)
                log_after_review = log_before_review
            reviewer_reaped = reap_turn(
                stage_root=stage_root,
                project_root=project_root,
                log_path=log_path,
                item_path=item.path,
                venue=reviewer_venue,
                role="reviewer",
                timeout=args.timeout,
            )
            verdict_error = reviewer_report_error(
                log_before_review,
                log_after_review,
            )
            reviewer_blocked = bool(BLOCK_RE.search(review_raw))
            if reviewer_blocked or not reviewed or verdict_error:
                review_failure = (
                    "independent reviewer BLOCK verdict"
                    if reviewer_blocked
                    else verdict_error or "independent reviewer command failed"
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
        print_escalation(f"cannot inspect changes for progress: {exc}")
        return 1
    previous_fingerprint = item_state["last_fingerprint"]
    no_progress = (
        bool(previous_fingerprint)
        and current_fingerprint == previous_fingerprint
    )
    state["iteration_count"] = iteration
    state["items"][item.item_id] = {
        "attempt_count": attempt,
        "last_fingerprint": current_fingerprint,
        "base_head": base_head,
        "executor_changed_paths": changed_paths,
    }
    try:
        write_run_state(state_path, state)
    except OSError as exc:
        print_escalation(f"cannot persist driver run state after execution: {exc}")
        return 1

    elapsed_after = max(0.0, time.time() - state["started_at_unix"])
    escalation_reasons: list[str] = []
    if no_progress:
        escalation_reasons.append("NO-PROGRESS fingerprint matched the previous attempt")
    if reviewer_blocked:
        escalation_reasons.append(failure)
    if limits is not None:
        if not step_ok and attempt >= limits["max_attempts_per_item"]:
            escalation_reasons.append("per-item attempt cap reached")
        if not step_ok and iteration >= limits["max_iterations"]:
            escalation_reasons.append("global iteration limit reached")
        if elapsed_after >= limits["max_wall_clock_seconds"]:
            escalation_reasons.append("global wall-clock limit exceeded")

    if escalation_reasons:
        print_escalation("; ".join(escalation_reasons))
        return 1
    if step_ok:
        print("Outcome: executor, acceptance, and independent reviewer passed")
        print(f"Recommended next action: {RECOMMEND_PASS}")
        return 0

    print(f"Outcome: {failure}")
    print(
        "Recommended next action: "
        + RECOMMEND_RETRY.format(
            attempt=attempt,
            cap=cap_text(limits, "max_attempts_per_item"),
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
