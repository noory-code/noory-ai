"""evonest_analyze — Observe-only pass, all improvements become proposals."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_analyze(
    project: str,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
    all_personas: bool = False,
    observe_mode: str | None = None,
    level: str | None = None,
) -> str:
    """Run Observe phase only, saving ALL identified improvements as proposals.

    No code is changed. All improvements regardless of category are saved to
    .evonest/proposals/ for human review.

    Args:
        project: Absolute path to target project.
        persona_id: Force a specific persona ID.
        adversarial_id: Force adversarial ID, or "none" to disable.
        group: Persona group filter ("biz", "tech", "quality").
        all_personas: Run every persona once. Each produces its own batch of proposals.
        observe_mode: "auto" (default), "quick", or "deep".
        level: Analysis depth preset — "quick" (haiku), "standard" (sonnet), "deep" (opus).
               Overrides active_level from config.
    """
    from evonest.core.orchestrator import run_analyze

    return await run_analyze(
        project=project,
        persona_id=persona_id,
        adversarial_id=adversarial_id,
        group=group,
        all_personas=all_personas,
        observe_mode=observe_mode,
        level=level,
    )
