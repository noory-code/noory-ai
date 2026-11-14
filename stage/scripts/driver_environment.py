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
from stage_model_tiers import load_tier_config  # noqa: E402
from stage_work import WorkItem  # noqa: E402

MODEL_ENV = "STAGE_MODEL"
EFFORT_ENV = "STAGE_EFFORT"


def model_tier_environment(project_root: Path, item: WorkItem, venue: str) -> dict[str, str]:
    """Return STAGE_MODEL / STAGE_EFFORT for the card's tier in `venue`.

    A card without a tier, a project without `model_tiers`, and a value the
    tier omits for that venue all export nothing.
    """

    if not item.tier:
        return {}
    values = load_tier_config(project_root / ".stage").values(item.tier, venue)
    if values is None:
        return {}
    env: dict[str, str] = {}
    if values.model:
        env[MODEL_ENV] = values.model
    if values.effort:
        env[EFFORT_ENV] = values.effort
    return env


def model_tier_record(
    project_root: Path,
    item: WorkItem,
    *,
    executor_venue: str,
    executor_command: str,
    reviewer_venue: str | None,
    reviewer_command: str,
) -> dict[str, object] | None:
    """Describe what one round hands each role, for the work log and the audit.

    `command_uses_*_env` records whether the command text reads the variable:
    a command that hardcodes its model never applies the card's tier.
    """

    if not item.tier or load_tier_config(project_root / ".stage").tiers is None:
        return None

    def role(venue: str | None, command: str) -> dict[str, object]:
        env = model_tier_environment(project_root, item, venue) if venue else {}
        return {
            "venue": venue or "",
            "model": env.get(MODEL_ENV, ""),
            "effort": env.get(EFFORT_ENV, ""),
            "command_uses_model_env": MODEL_ENV in command,
            "command_uses_effort_env": EFFORT_ENV in command,
        }

    return {
        "tier": item.tier,
        "executor": role(executor_venue, executor_command),
        "reviewer": role(reviewer_venue, reviewer_command),
    }


def project_environment(project_root: Path) -> dict[str, str]:
    """Return the inherited environment bound to the target project.

    Model-tier variables are never inherited: each role gets only the values
    its own card and venue select.
    """

    resolved_root = str(project_root.resolve())
    env = os.environ.copy()
    env.pop(MODEL_ENV, None)
    env.pop(EFFORT_ENV, None)
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
    env.update(model_tier_environment(project_root, item, item.venue))
    if executor_index_path is not None:
        env["GIT_INDEX_FILE"] = str(executor_index_path.resolve())
    return env
