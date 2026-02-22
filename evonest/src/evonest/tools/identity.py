"""evonest_identity — View/update project identity."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_identity(project: str, content: str | None = None) -> str:
    """View or replace the project identity document (.evonest/identity.md)."""
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    if content is not None:
        state.write_identity(content)
        return "Identity updated."
    return state.read_identity()


@mcp.tool()
async def evonest_identity_refresh(project: str) -> str:
    """Re-draft identity.md by having Claude explore the project.

    Uses the same LLM-based approach as `evonest init` — Claude reads project
    files (README, pyproject.toml, CLAUDE.md, etc.) and produces a fresh draft.

    Returns a dict with 'current' and 'draft' keys so the caller can review
    the proposed changes and decide whether to apply them via evonest_identity().
    """
    import json
    from pathlib import Path

    from evonest.core.initializer import _draft_identity_via_claude
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    current = state.read_identity()

    draft = _draft_identity_via_claude(Path(project))
    if not draft:
        return json.dumps(
            {"error": "Could not generate draft — claude CLI unavailable or failed"},
            ensure_ascii=False,
        )

    return json.dumps(
        {"current": current, "draft": draft},
        indent=2,
        ensure_ascii=False,
    )
