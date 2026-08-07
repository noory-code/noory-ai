#!/usr/bin/env python3
"""Answer questions about a work item's place in the tree, and how big it is.

Two jobs that share the same walk. Which leaf is ready to run next, and how much
the requested subtree is asking for — the second is what sets a round's time
limit, because a card that declares more work needs longer than the floor a
single leaf gets.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from stage_work import (  # noqa: E402
    WORK_FINAL_STATUSES,
    WorkItem,
    non_terminal_children,
)

# The floor a single leaf gets. A subtree multiplies it by what the card
# declared, so the limit tracks the work rather than the number of rounds.
MIN_COMMAND_TIMEOUT_SECONDS = 900

SUCCESS_CRITERIA_HEADING_RE = re.compile(
    r"(?m)^##[ \t]+Success criteria[ \t]*\r?$"
)
TOP_LEVEL_LIST_ITEM_RE = re.compile(r"(?m)^[-*+][ \t]+\S")


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


def unfinished_subtree_leaf_count(
    target_id: str,
    items: list[WorkItem],
) -> int:
    """Count unfinished leaves at or below one hierarchy target."""

    by_id = {item.item_id: item for item in items}
    return max(
        1,
        sum(
            1
            for item in items
            if item.status not in WORK_FINAL_STATUSES
            and not non_terminal_children(item.item_id, items)
            and (
                item.item_id == target_id
                or is_in_subtree(item, target_id, by_id)
            )
        ),
    )


def declared_success_criteria_count(item: WorkItem) -> int:
    """Count top-level list items in the card's success-criteria section."""

    try:
        text = item.path.read_text(encoding="utf-8")
    except OSError:
        return 0
    heading = SUCCESS_CRITERIA_HEADING_RE.search(text)
    if heading is None:
        return 0
    next_heading = re.search(r"(?m)^##[ \t]+", text[heading.end() :])
    section_end = (
        heading.end() + next_heading.start()
        if next_heading is not None
        else len(text)
    )
    return len(TOP_LEVEL_LIST_ITEM_RE.findall(text[heading.end() : section_end]))


def declared_command_size(target_id: str, items: list[WorkItem]) -> int:
    """Return the largest declared or structural size signal for one target."""

    target = next(item for item in items if item.item_id == target_id)
    return max(
        unfinished_subtree_leaf_count(target_id, items),
        len(target.scope),
        declared_success_criteria_count(target),
    )


def subtree_command_timeout(
    target_id: str,
    items: list[WorkItem],
    *,
    requested: int | None,
) -> int:
    """Derive a command timeout from subtree size unless the operator overrides it."""

    if requested is not None:
        return requested
    return declared_command_size(target_id, items) * MIN_COMMAND_TIMEOUT_SECONDS


def subtree_limits(
    configured: dict[str, int],
    target_id: str,
    items: list[WorkItem],
    *,
    per_action_seconds: int,
) -> dict[str, int]:
    """Scale global ceilings to the number of unfinished leaves in the subtree."""

    action_count = unfinished_subtree_leaf_count(target_id, items)
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
