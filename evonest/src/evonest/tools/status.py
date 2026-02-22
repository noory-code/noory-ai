"""evonest_status — Show project evolution status."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_status(project: str) -> str:
    """Show evolution status: cycle count, success rate, running state, convergence areas."""
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    return state.summary()
