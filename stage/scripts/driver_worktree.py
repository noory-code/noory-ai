#!/usr/bin/env python3
"""Give an unattended run its own checkout, and take it away afterwards.

An unattended run must not touch the branch a person is working on, so it gets a
worktree and a branch of its own. Two things travel between them by hand: the
runtime state the run needs to start, and the logs it leaves behind. Everything
else stays on the isolated branch until a person merges it.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_git import current_branch, run_branch_name, run_git  # noqa: E402
from driver_subtree import is_in_subtree  # noqa: E402
from stage_work import WorkItem  # noqa: E402

# The driver's own bookkeeping. A run needs it seeded in, and its logs carried
# back out, because nothing else travels between the two checkouts.
STAGE_RUNTIME_PREFIX = ".stage/.runtime/"


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


def unattended_worktree_path(
    project_root: Path,
    target_id: str,
    now: float,
    *,
    worktree_root: Path | None = None,
) -> Path:
    """Return the separate checkout path for one unattended run."""

    root = (
        worktree_root.resolve()
        if worktree_root is not None
        else project_root.parent / f"{project_root.name}-stage-unattended"
    )
    return (root / f"{target_id}-{int(now)}").resolve()


def create_unattended_worktree(
    project_root: Path,
    target_id: str,
    now: float,
    *,
    worktree_root: Path | None = None,
) -> tuple[Path | None, str, str]:
    """Create an unattended worktree without switching the human checkout."""

    path = unattended_worktree_path(
        project_root,
        target_id,
        now,
        worktree_root=worktree_root,
    )
    branch = run_branch_name(target_id, now)
    if path.exists() or path.is_symlink():
        return None, "", f"unattended worktree path already exists: {path}"
    exists, out = run_git(
        project_root,
        ["rev-parse", "--verify", "--quiet", branch],
    )
    if exists:
        return None, "", f"unattended run branch already exists: {branch}"
    if out.strip():
        return None, "", f"cannot inspect unattended run branch {branch}: {out.strip()}"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return None, "", f"cannot create unattended worktree root {path.parent}: {exc}"
    ok, out = run_git(
        project_root,
        ["worktree", "add", "-b", branch, str(path), "HEAD"],
    )
    if not ok:
        return None, "", (
            f"cannot create unattended worktree {path} on {branch}: {out.strip()}"
        )
    return path, branch, ""


def remove_unattended_worktree(project_root: Path, path: Path) -> str:
    """Remove a clean unattended worktree while retaining its handoff branch."""

    ok, out = run_git(project_root, ["worktree", "remove", str(path)])
    if not ok:
        detail = out.strip() or "git worktree remove failed"
        return f"cannot remove unattended worktree {path}: {detail}"
    try:
        path.parent.rmdir()
    except OSError:
        pass
    return ""


def seed_unattended_runtime(
    stage_root: Path,
    run_stage_root: Path,
    target_id: str,
    items: list[WorkItem],
) -> str:
    """Copy only the selected subtree's prior driver state into its worktree."""

    by_id = {item.item_id: item for item in items}
    item_ids = {
        item.item_id
        for item in items
        if item.item_id == target_id or is_in_subtree(item, target_id, by_id)
    }
    relative_paths = [Path(f"driver/{target_id}.json")]
    for item_id in sorted(item_ids):
        relative_paths.extend(
            (
                Path(f"driver/logs/{item_id}.md"),
                Path(f"driver/verdicts/{item_id}.json"),
            )
        )
    source_root = stage_root / ".runtime"
    destination_root = run_stage_root / ".runtime"
    try:
        for relative_path in relative_paths:
            source = source_root / relative_path
            if not source.is_file():
                continue
            destination = destination_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    except OSError as exc:
        return f"cannot seed unattended runtime evidence: {exc}"
    return ""


def preserve_unattended_runtime(run_stage_root: Path, stage_root: Path) -> str:
    """Move ignored runtime evidence back to the human checkout before cleanup."""

    source = run_stage_root / ".runtime"
    if not source.exists():
        return ""
    destination = stage_root / ".runtime"
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        shutil.rmtree(source)
    except OSError as exc:
        return f"cannot preserve unattended runtime evidence from {source}: {exc}"
    return ""
