"""evonest_evolve — Full evolution cycle (replaces evonest_run)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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

    Runs in the background — returns immediately with PID and log path.

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
    cmd = [sys.executable, "-m", "evonest._runner", "evolve", project]
    if cycles is not None:
        cmd += ["--cycles", str(cycles)]
    if no_meta:
        cmd += ["--no-meta"]
    if no_scout:
        cmd += ["--no-scout"]
    if observe_mode:
        cmd += ["--observe-mode", observe_mode]
    if persona_id:
        cmd += ["--persona-id", persona_id]
    if adversarial_id:
        cmd += ["--adversarial-id", adversarial_id]
    if group:
        cmd += ["--group", group]
    if all_personas:
        cmd += ["--all-personas"]
    if cautious:
        cmd += ["--cautious"]
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
        f"Evolve started (PID {proc.pid}).\n"
        f"Progress log: {log_path}\n"
        f"A macOS notification will fire on each phase and at completion."
    )
