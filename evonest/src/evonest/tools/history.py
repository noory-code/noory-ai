"""evonest_history — View cycle history."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_history(project: str, count: int = 10) -> str:
    """Show recent evolution cycle history."""
    from evonest.core.history import get_recent_history

    return get_recent_history(project, count)
