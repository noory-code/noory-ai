"""Shared guard against closing work that still authorizes dirty source paths."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from stage_paths import is_stage_internal_path  # noqa: E402
from stage_work import WorkItem, item_matches_path, split_scope  # noqa: E402

ORDER_CONTRACT = "commit source changes first, then close, then archive"


def _porcelain_paths(output: bytes) -> list[str]:
    """Return every changed entry named by NUL-delimited porcelain v1 output."""
    fields = output.split(b"\0")
    paths: list[str] = []
    index = 0
    while index < len(fields):
        entry = fields[index]
        index += 1
        if not entry:
            continue
        if len(entry) < 4 or entry[2:3] != b" ":
            raise RuntimeError("git status --porcelain returned an unrecognized record")
        status = entry[:2]
        paths.append(os.fsdecode(entry[3:]))
        if b"R" in status or b"C" in status:
            if index >= len(fields) or not fields[index]:
                raise RuntimeError("git status --porcelain returned an incomplete rename record")
            paths.append(os.fsdecode(fields[index]))
            index += 1
    return paths


def dirty_paths_in_scope(project_root: Path, scope_value: str) -> list[str]:
    """List dirty non-Stage paths covered by a work item's scope.

    A directory outside a git work tree has no ordering guard. Once git confirms
    the project is a work tree, status failures are errors rather than silent
    passes because closing without knowing the worktree state would be unsafe.
    """
    try:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return []

    status = subprocess.run(
        [
            "git",
            "-c",
            "status.relativePaths=true",
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            ".",
        ],
        cwd=str(project_root),
        capture_output=True,
    )
    if status.returncode != 0:
        detail = os.fsdecode(status.stderr).strip() or f"exit {status.returncode}"
        raise RuntimeError(f"git status --porcelain failed: {detail}")

    item = WorkItem(
        path=Path(),
        item_id="",
        title="",
        status="active",
        verification="pending",
        retrospective="pending",
        promotion="pending",
        scope=split_scope(scope_value),
        promotes=(),
    )
    return [
        path
        for path in _porcelain_paths(status.stdout)
        if not is_stage_internal_path(path, project_root)
        and item_matches_path(item, path, project_root)
    ]
