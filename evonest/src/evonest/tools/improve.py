"""evonest_improve — Execute a selected proposal."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from evonest.server import mcp


def _pending_count(project: str) -> int:
    proposals_dir = Path(project) / ".evonest" / "proposals"
    if not proposals_dir.is_dir():
        return 0
    return sum(1 for f in proposals_dir.iterdir() if f.suffix == ".md" and f.is_file())


def _extract_result(log_path: Path) -> str:
    """Extract the last improve result from the log file."""
    try:
        lines = log_path.read_text(errors="replace").splitlines()
    except OSError:
        return "Improve complete."

    # Find the last "evonest improve completed:" marker and collect lines after it
    for i in range(len(lines) - 1, -1, -1):
        if "evonest improve completed:" in lines[i]:
            result_lines = lines[i + 1 :]
            return "\n".join(result_lines).strip() or "Improve complete."
    return "Improve complete."


async def _run_one(project: str, proposal_id: str | None) -> str:
    """Run a single improve cycle synchronously. Returns the result string."""
    cmd = [sys.executable, "-m", "evonest._runner", "improve", project]
    if proposal_id:
        cmd += ["--proposal-id", proposal_id]

    log_path = Path(project) / ".evonest" / "logs" / "current.log"

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return _extract_result(log_path)


@mcp.tool()
async def evonest_improve(
    project: str,
    proposal_id: str | None = None,
    all: bool = False,
) -> str:
    """Execute a proposal: select → Execute → Verify → commit/PR.

    No Observe or Plan phases run. The proposal content IS the plan.
    Blocks until the proposal is fully processed (build + tests + commit).

    Args:
        project: Absolute path to target project.
        proposal_id: Bare filename of the proposal to execute
                     (e.g. 'proposal-0000-shell-injection-risk.md').
                     If omitted, auto-selects by priority (high first) then age (oldest first).
        all: If True, process all pending proposals sequentially until none remain.
    """
    if all:
        results: list[str] = []
        while True:
            pending = _pending_count(project)
            if pending == 0:
                break
            result = await _run_one(project, proposal_id=None)
            results.append(result)
            if "no proposals" in result.lower() or "no pending" in result.lower():
                break
        if not results:
            return "No pending proposals found."
        return f"Batch complete: {len(results)} proposal(s) processed.\n\n" + "\n\n---\n\n".join(
            results
        )

    return await _run_one(project, proposal_id)
