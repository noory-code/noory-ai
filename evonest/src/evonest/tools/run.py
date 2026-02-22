"""evonest_run — Run evolution cycles. [DEPRECATED: use evonest_evolve]"""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_run(
    project: str,
    cycles: int | None = None,
    dry_run: bool = False,
    no_meta: bool = False,
    no_scout: bool = False,
    observe_mode: str | None = None,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
    all_personas: bool = False,
) -> str:
    """[DEPRECATED] Use evonest_evolve instead. Kept for backward compatibility.

    Run N evolution cycles on a project. Observe → Plan → Execute → Verify.
    If dry_run=True, redirects to evonest_analyze behavior.

    observe_mode: "auto" (default), "quick" (sampled, faster), "deep" (comprehensive).
    persona_id: Force a specific persona (e.g. "product-strategist", "architect").
    adversarial_id: Force a specific adversarial (e.g. "corrupt-state"), or "none" to disable.
    group: Persona group to sample from ("biz", "tech", "quality"). Overrides active_groups config.
    no_scout: Skip the external scout phase.
    all_personas: Run every persona exactly once in order. Overrides cycles.
    """
    import warnings

    warnings.warn(
        "evonest_run is deprecated. Use evonest_evolve instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from evonest.core.orchestrator import run_cycles

    return await run_cycles(
        project=project,
        cycles=cycles,
        dry_run=dry_run,
        no_meta=no_meta,
        no_scout=no_scout,
        observe_mode=observe_mode,
        persona_id=persona_id,
        adversarial_id=adversarial_id,
        group=group,
        all_personas=all_personas,
    )
