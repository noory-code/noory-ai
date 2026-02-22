"""evonest_decide — Drop a human decision."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_decide(project: str, content: str) -> str:
    """Drop a human decision that will be consumed by the next evolution cycle."""
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    path = state.add_decision(content)
    return f"Decision saved: {path}"
