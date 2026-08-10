#!/usr/bin/env python3
"""Observe the repository the driver runs against, without changing it.

Every function here reads Git or the working tree and reports what it saw. None
of them writes, stages, or commits. That separation is what lets a round compare
the tree before and after an executor and attribute the difference to the
executor rather than to the driver's own bookkeeping.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from stage_work import WorkItem  # noqa: E402

# Runtime bookkeeping is the driver's own writing, never an executor's output,
# so it stays out of every snapshot the driver compares.
STAGE_RUNTIME_PREFIX = ".stage/.runtime/"


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


def work_card_relative_path(project_root: Path, item: WorkItem) -> str:
    """Return the work card path relative to its repository root."""

    try:
        return item.path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeError(
            f"work card is outside the project root: {item.path}"
        ) from exc


def executor_widened_work_card_scope(
    item: WorkItem,
    scope_after_executor: tuple[str, ...],
) -> bool:
    """Return whether an executor added any entry to its work card scope."""

    return bool(set(scope_after_executor) - set(item.scope))


def executor_changed_only_work_card(
    project_root: Path,
    item: WorkItem,
    changed_paths: list[str],
    scope_after_executor: tuple[str, ...] = (),
) -> bool:
    """Return whether an executor rejected a card by changing only that card."""

    return (
        not executor_widened_work_card_scope(item, scope_after_executor)
        and set(changed_paths) == {work_card_relative_path(project_root, item)}
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
