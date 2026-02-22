"""Backlog management — CRUD, pruning, context building.

Backlog items track improvement ideas across cycles. Items are:
- Added by Observe phase (save_observations)
- Selected by Plan phase (mark in_progress)
- Completed or failed by Verify phase (mark completed/pending + increment attempts)
- Pruned: completed/stale items older than 20 cycles removed
- Stale: items with 3+ failed attempts are marked stale
"""

from __future__ import annotations

import time
from pathlib import Path
from random import randint
from typing import Any

from evonest.core.state import ProjectState

MAX_ATTEMPTS = 3
PRUNE_AGE_CYCLES = 20


def save_observations(
    state: ProjectState, improvements: list[dict[str, Any]], persona_id: str, current_cycle: int
) -> int:
    """Add new improvement items from observe output. Returns count added."""
    backlog = state.read_backlog()
    items = backlog.setdefault("items", [])
    existing_titles = {item["title"] for item in items}
    added = 0

    for imp in improvements:
        title = imp.get("title") or imp.get("description") or "untitled"
        if title in existing_titles:
            continue

        item_id = f"improve-{int(time.time())}-{randint(1000, 9999)}"
        files = imp.get("files", [])
        if isinstance(files, str):
            files = [f.strip() for f in files.split(",") if f.strip()]

        items.append(
            {
                "id": item_id,
                "title": title,
                "category": imp.get("category", "general"),
                "priority": imp.get("priority", "medium"),
                "files": files,
                "source_persona": persona_id,
                "source_cycle": current_cycle,
                "status": "pending",
                "attempts": 0,
            }
        )
        existing_titles.add(title)
        added += 1

    state.write_backlog(backlog)
    return added


def update_status(state: ProjectState, item_id: str, new_status: str) -> None:
    """Update a backlog item's status. Increments attempts on failure."""
    backlog = state.read_backlog()
    for item in backlog.get("items", []):
        if item["id"] == item_id:
            item["status"] = new_status
            if new_status == "pending":
                item["attempts"] = item.get("attempts", 0) + 1
                if item["attempts"] >= MAX_ATTEMPTS:
                    item["status"] = "stale"
            break
    state.write_backlog(backlog)


def prune(state: ProjectState, current_cycle: int) -> int:
    """Remove completed/stale items older than PRUNE_AGE_CYCLES. Returns count removed."""
    backlog = state.read_backlog()
    cutoff = max(0, current_cycle - PRUNE_AGE_CYCLES)

    original_count = len(backlog.get("items", []))
    backlog["items"] = [
        item
        for item in backlog.get("items", [])
        if item["status"] in ("pending", "in_progress") or item.get("source_cycle", 0) > cutoff
    ]
    removed = original_count - len(backlog["items"])

    if removed > 0:
        state.write_backlog(backlog)
    return removed


def build_context(state: ProjectState, limit: int = 10) -> str:
    """Build backlog context for plan phase prompts."""
    backlog = state.read_backlog()
    pending = [item for item in backlog.get("items", []) if item["status"] == "pending"]

    if not pending:
        return ""

    # Sort by priority (high first)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

    lines = [
        "## Accumulated Backlog",
        "",
        "The following improvements have been identified in previous cycles "
        "but not yet implemented.",
        "Consider selecting from this list if any align with your current observations.",
        "",
    ]
    for item in pending[:limit]:
        files = ", ".join(item.get("files", []))
        lines.append(
            f"- [{item.get('priority', 'medium')}] {item['title']} "
            f"(category: {item.get('category', 'general')}, files: {files})"
        )

    return "\n".join(lines)


def manage_backlog(
    project: str | Path,
    action: str = "list",
    item: dict[str, object] | None = None,
) -> str:
    """MCP tool handler for backlog management."""
    state = ProjectState(project)
    backlog = state.read_backlog()

    if action == "list":
        items = backlog.get("items", [])
        if not items:
            return "Backlog is empty."
        pending = [i for i in items if i["status"] == "pending"]
        stale = [i for i in items if i["status"] == "stale"]
        completed = [i for i in items if i["status"] == "completed"]
        lines = [
            f"Backlog: {len(items)} items (pending: {len(pending)}, "
            f"stale: {len(stale)}, completed: {len(completed)})"
        ]
        for i in items:
            lines.append(f"  [{i['status']}] {i['title']} ({i.get('category', '')})")
        return "\n".join(lines)

    elif action == "add" and item:
        title = str(item.get("title", "untitled"))
        progress = state.read_progress()
        added = save_observations(
            state,
            [
                {
                    "title": title,
                    "category": item.get("category", "general"),
                    "priority": item.get("priority", "medium"),
                    "files": item.get("files", []),
                }
            ],
            persona_id="human",
            current_cycle=progress.get("total_cycles", 0),
        )
        return f"Added {added} item(s) to backlog."

    elif action == "remove" and item:
        item_id = str(item.get("id", ""))
        backlog["items"] = [i for i in backlog.get("items", []) if i["id"] != item_id]
        state.write_backlog(backlog)
        return f"Removed item: {item_id}"

    elif action == "prune":
        progress = state.read_progress()
        removed = prune(state, progress.get("total_cycles", 0))
        return f"Pruned {removed} item(s)."

    return f"Unknown action: {action}"
