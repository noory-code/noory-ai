"""evonest_improve — Execute a selected proposal."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from evonest.server import mcp


@mcp.tool()
async def evonest_improve(
    project: str,
    proposal_id: str | None = None,
) -> str:
    """Execute a proposal: select → Execute → Verify → commit/PR.

    No Observe or Plan phases run. The proposal content IS the plan.
    Runs in the background — returns immediately with PID and log path.

    Args:
        project: Absolute path to target project.
        proposal_id: Bare filename of the proposal to execute
                     (e.g. 'proposal-0000-shell-injection-risk.md').
                     If omitted, auto-selects by priority (high first) then age (oldest first).
    """
    cmd = [sys.executable, "-m", "evonest._runner", "improve", project]
    if proposal_id:
        cmd += ["--proposal-id", proposal_id]

    log_path = Path(project) / ".evonest" / "logs" / "current.log"
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return (
        f"Improve started (PID {proc.pid}).\n"
        f"Progress log: {log_path}\n"
        f"A macOS notification will fire when complete."
    )
