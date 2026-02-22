"""evonest_stimuli — Inject external stimuli."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_stimuli(project: str, content: str) -> str:
    """Inject an external stimulus that will influence the next evolution cycle."""
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    path = state.add_stimulus(content)
    return f"Stimulus saved: {path}"
