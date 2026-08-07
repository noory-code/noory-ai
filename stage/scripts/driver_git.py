#!/usr/bin/env python3
"""Write to Git on the driver's behalf — branch, stage, commit, restore.

Its counterpart, driver_repository, only reads. Everything that changes the
repository lives here, and nothing here decides *whether* to change it: a caller
that already judged a round passes in what to record. Keeping the judgement out
is what lets a failed write be reported rather than silently retried.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_repository import (  # noqa: E402
    git_head_exists,
    git_index_path,
    work_card_relative_path,
)
from stage_work import WorkItem  # noqa: E402

# The driver's own bookkeeping. It is never committed as a round's output.
STAGE_RUNTIME_PREFIX = ".stage/.runtime/"


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


def run_branch_name(target_id: str, now: float) -> str:
    """Return the branch owned by one unattended run."""

    return f"stage/driver/{target_id}-{int(now)}"


def create_run_branch(project_root: Path, target_id: str, now: float) -> tuple[str, str]:
    """Create and check out an isolated run branch; NEVER commit to the base branch.

    Returns (branch_name, error). An existing branch (idempotent re-run) is
    checked out rather than recreated.
    """

    branch = run_branch_name(target_id, now)
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
    try:
        card_path = work_card_relative_path(project_root, item)
    except RuntimeError as exc:
        return False, f"refusing item commit: {exc}"
    commit_paths = list(
        dict.fromkeys([path for path in item.scope if path] + [card_path])
    )
    ok, out = run_git(project_root, ["add", "--", *commit_paths])
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


def current_branch(project_root: Path) -> str:
    ok, out = run_git(project_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if ok else ""
