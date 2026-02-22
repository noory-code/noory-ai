"""evonest_backlog — Manage improvement backlog."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_backlog(
    project: str,
    action: str = "list",
    item: dict[str, object] | None = None,
) -> str:
    """View, add, or remove backlog items. Actions: list, add, remove, prune."""
    from evonest.core.backlog import manage_backlog

    return manage_backlog(project, action, item)
