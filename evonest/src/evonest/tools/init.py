"""evonest_init — Initialize a project for evolution."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_init(path: str, level: str = "standard") -> str:
    """Initialize .evonest/ in a project directory.

    Creates config, identity, progress, and backlog templates.

    Args:
        path: Absolute path to the target project directory.
        level: Analysis depth preset — "quick" (haiku, fast), "standard" (sonnet, balanced),
               or "deep" (opus, thorough). Sets active_level in config.json.
    """
    from evonest.core.initializer import init_project

    return init_project(path, level=level)
