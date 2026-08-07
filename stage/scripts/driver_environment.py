#!/usr/bin/env python3
"""Build the environment a child process runs in.

Three audiences, three shapes: an acceptance check needs the project root, a
venue executor needs the card and its purpose too, and a health check needs
neither. Keeping them apart is what stops a variable meant for one from leaking
into another and quietly changing what that process sees.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_subtree import ancestor_chain  # noqa: E402
from stage_work import WorkItem  # noqa: E402


def project_environment(project_root: Path) -> dict[str, str]:
    """Return the inherited environment bound to the target project."""

    resolved_root = str(project_root.resolve())
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_PROJECT_DIR": resolved_root,
            "PROJECT_ROOT": resolved_root,
        }
    )
    return env


def check_environment() -> dict[str, str]:
    """Return the inherited environment without host project bindings."""

    env = os.environ.copy()
    env.pop("CLAUDE_PROJECT_DIR", None)
    env.pop("PROJECT_ROOT", None)
    return env


def executor_environment(
    item: WorkItem,
    project_root: Path,
    work_log_path: Path,
    review_verdict_file: Path,
    executor_index_path: Path | None = None,
    *,
    items: list[WorkItem] | None = None,
) -> dict[str, str]:
    """Return the inherited environment plus the selected work item context."""

    env = project_environment(project_root)
    env.update(
        {
            "STAGE_WORK_ITEM": item.item_id,
            "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
            "STAGE_PROJECT_ROOT": str(project_root.resolve()),
            "STAGE_WORK_LOG_PATH": str(work_log_path.resolve()),
            "STAGE_REVIEW_VERDICT_FILE": str(review_verdict_file.resolve()),
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
