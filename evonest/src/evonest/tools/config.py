"""evonest_config — View/update project configuration."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_config(project: str, settings: dict[str, object] | None = None) -> str:
    """View or update project configuration (cycles, model, verify commands, etc.)."""
    from evonest.core.config import EvonestConfig

    cfg = EvonestConfig.load(project)
    if settings:
        for key, value in settings.items():
            cfg.set(key, value)
        cfg.save()
        return f"Updated: {', '.join(settings.keys())}\n{cfg.to_json()}"
    return cfg.to_json()
