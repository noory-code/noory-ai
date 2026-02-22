"""evonest_progress — View detailed evolution progress."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_progress(project: str) -> str:
    """Show detailed statistics: per-persona weights, area touch counts, convergence flags."""
    from evonest.core.progress import get_progress_report

    return get_progress_report(project)
