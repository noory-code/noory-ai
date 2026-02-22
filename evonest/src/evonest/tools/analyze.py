"""evonest_analyze — Observe-only pass, all improvements become proposals."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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
    .evonest/proposals/ for human review. Runs in the background — returns immediately.

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
    cmd = [sys.executable, "-m", "evonest._runner", "analyze", project]
    if persona_id:
        cmd += ["--persona-id", persona_id]
    if adversarial_id:
        cmd += ["--adversarial-id", adversarial_id]
    if group:
        cmd += ["--group", group]
    if all_personas:
        cmd += ["--all-personas"]
    if observe_mode:
        cmd += ["--observe-mode", observe_mode]
    if level:
        cmd += ["--level", level]

    log_path = Path(project) / ".evonest" / "logs" / "current.log"
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return (
        f"Analyze started (PID {proc.pid}).\n"
        f"Progress log: {log_path}\n"
        f"A macOS notification will fire when complete."
    )
