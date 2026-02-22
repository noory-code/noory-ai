"""evonest_improve — Execute a selected proposal."""

from __future__ import annotations

from evonest.server import mcp


@mcp.tool()
async def evonest_improve(
    project: str,
    proposal_id: str | None = None,
) -> str:
    """Execute a proposal: select → Execute → Verify → commit/PR.

    No Observe or Plan phases run. The proposal content IS the plan.

    Args:
        project: Absolute path to target project.
        proposal_id: Bare filename of the proposal to execute
                     (e.g. 'proposal-0004-20260222-103000-123456.md').
                     If omitted, auto-selects by priority (high first) then age (oldest first).
    """
    from evonest.core.improve import run_improve

    return await run_improve(project=project, proposal_id=proposal_id)
