"""evonest_scout — On-demand scout execution."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_scout(project: str) -> str:
    """Run the scout phase immediately to search for external developments.

    Searches for recent changes in the project's ecosystem and injects
    qualifying findings as stimuli for the next evolution cycle.
    """
    from evonest.core import claude_runner
    from evonest.core.config import EvonestConfig
    from evonest.core.scout import apply_scout_results, build_scout_prompt
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    config = EvonestConfig.load(project)

    prompt = build_scout_prompt(state)
    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.scout,
        allowed_tools=claude_runner.SCOUT_TOOLS,
        cwd=str(state.project),
    )

    if not result.success:
        return "Scout produced no output"

    progress = state.read_progress()
    current_cycle = progress.get("total_cycles", 0)
    summary = apply_scout_results(state, result.output, config, current_cycle)

    lines = [
        "Scout complete:",
        f"  Found: {summary['findings_found']}",
        f"  Injected as stimuli: {summary['findings_injected']}",
        f"  Below threshold: {summary['findings_skipped_score']}",
        f"  Duplicates skipped: {summary['findings_skipped_duplicate']}",
    ]
    return "\n".join(lines)
