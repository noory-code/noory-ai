"""Cycle history and convergence detection.

History files are stored as cycle-NNNN.json in .evonest/history/.
Each file contains the full cycle result including persona, adversarial,
success status, changes, and timing.
"""

from __future__ import annotations

import json
from pathlib import Path

from evonest.core.state import ProjectState


def build_history_summary(state: ProjectState, count: int = 5) -> str:
    """Build recent history context for phase prompts."""
    files = state.list_history_files()
    if not files:
        return ""

    # Take the last N files (most recent)
    recent = files[-count:]

    lines = ["## Recent Cycle History", ""]
    for f in reversed(recent):  # newest first
        data = json.loads(f.read_text(encoding="utf-8"))
        ts = data.get("timestamp", "unknown")
        success = data.get("success", False)
        mutation = data.get("mutation", {})
        persona = mutation.get("persona", "unknown")
        adversarial = mutation.get("adversarial", "none")
        duration = data.get("duration_seconds", 0)
        title = data.get("improvement_title") or data.get("changes") or "N/A"
        status = "SUCCESS" if success else "FAIL"
        lines.append(
            f"- **{ts}**: {status} | persona={persona} | "
            f"adversarial={adversarial} | {duration}s | {title}"
        )

    return "\n".join(lines)


def get_recent_history(project: str | Path, count: int = 10) -> str:
    """MCP tool handler for viewing cycle history."""
    state = ProjectState(project)
    files = state.list_history_files()

    if not files:
        return "No cycle history yet."

    recent = files[-count:]
    lines = [f"Showing {len(recent)} of {len(files)} total cycles:", ""]

    for f in reversed(recent):
        data = json.loads(f.read_text(encoding="utf-8"))
        ts = data.get("timestamp", "unknown")
        success = data.get("success", False)
        mutation = data.get("mutation", {})
        persona = mutation.get("persona", "unknown")
        adversarial = mutation.get("adversarial", "none")
        duration = data.get("duration_seconds", 0)
        title = data.get("improvement_title", "N/A")
        status = "SUCCESS" if success else "FAIL"
        commit = data.get("commit_message", "")

        lines.append(f"[{ts}] {status}")
        lines.append(f"  Persona: {persona}")
        if adversarial != "none":
            lines.append(f"  Adversarial: {adversarial}")
        lines.append(f"  Change: {title}")
        if commit:
            lines.append(f"  Commit: {commit}")
        lines.append(f"  Duration: {duration}s")
        lines.append("")

    return "\n".join(lines)
