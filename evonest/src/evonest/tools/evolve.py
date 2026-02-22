"""evonest_evolve — Full evolution cycle (replaces evonest_run)."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_evolve(
    project: str,
    cycles: int | None = None,
    no_meta: bool = False,
    no_scout: bool = False,
    observe_mode: str | None = None,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
    all_personas: bool = False,
    cautious: bool = False,
    resume: bool | None = None,
    level: str | None = None,
) -> str:
    """Run full evolution: Observe → Plan → Execute → Verify → commit/PR.

    Args:
        project: Absolute path to target project.
        cycles: Number of cycles to run (default from config).
        no_meta: Skip meta-observe.
        no_scout: Skip scout phase.
        observe_mode: "auto", "quick", or "deep".
        persona_id: Force a specific persona.
        adversarial_id: Force adversarial, or "none" to disable.
        group: Persona group filter.
        all_personas: Run every persona once.
        cautious: If True, pause after Plan phase and return plan summary.
                  Call again with resume=True to execute, resume=False to cancel.
        resume: None = normal run; True = resume paused cautious session;
                False = cancel paused cautious session.
        level: Analysis depth preset — "quick" (haiku), "standard" (sonnet), "deep" (opus).
               Overrides active_level from config.
    """
    from evonest.core.orchestrator import run_cycles

    return await run_cycles(
        project=project,
        cycles=cycles,
        no_meta=no_meta,
        no_scout=no_scout,
        observe_mode=observe_mode,
        persona_id=persona_id,
        adversarial_id=adversarial_id,
        group=group,
        all_personas=all_personas,
        cautious=cautious,
        resume=resume,
        level=level,
    )
