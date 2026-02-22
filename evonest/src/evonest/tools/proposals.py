"""evonest_proposals — List and manage proposals."""

from __future__ import annotations

from pathlib import Path

from evonest.server import mcp


@mcp.tool()
async def evonest_proposals(
    project: str,
    action: str = "list",
    filename: str = "",
) -> str:
    """List pending proposals or mark one as done (moves to proposals/done/).

    Args:
        project: Absolute path to the target project.
        action:  "list" (default) — show pending proposals.
                 "done" — mark a proposal as completed and move it to done/.
        filename: Required when action="done". Bare filename of the proposal
                  (e.g. 'proposal-0004-20260218-195413-167247.md').
    """
    from evonest.core.state import ProjectState

    state = ProjectState(project)

    if action == "done":
        if not filename:
            return "Error: filename is required for action='done'."
        try:
            dest = state.mark_proposal_done(filename)
            return f"Proposal marked as done: {dest}"
        except FileNotFoundError as e:
            return f"Error: {e}"

    # action == "list"
    proposals = state.list_proposals()
    if not proposals:
        return "No pending proposals."

    def _parse_meta(path: Path) -> tuple[str, str, str]:
        """Return (title, priority, persona) from a proposal file."""
        import re

        title = priority = persona = ""
        try:
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines()[:15]:
                if not title and line.startswith("# "):
                    title = re.sub(r"^#\s*(제안|Proposal):\s*", "", line[2:]).strip()
                elif not priority:
                    m = re.search(r"\*\*(?:우선순위|[Pp]riority)\*\*[:\s]+(\w+)", line)
                    if m:
                        priority = m.group(1).lower()
                elif not persona:
                    m = re.search(r"\*\*(?:작성 페르소나|[Pp]ersona)\*\*[:\s]+([^\s*]+)", line)
                    if m:
                        persona = m.group(1)
        except OSError:
            pass
        return title or path.name, priority or "?", persona or "?"

    _priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_proposals = sorted(
        proposals,
        key=lambda p: (_priority_order.get(_parse_meta(p)[1], 9), p.name),
    )

    lines = [f"Pending proposals ({len(proposals)}):"]
    for i, p in enumerate(sorted_proposals, 1):
        title, priority, persona = _parse_meta(p)
        lines.append(f"\n  [{i}] {title}")
        lines.append(f"      priority: {priority} | persona: {persona}")
        lines.append(f"      {p.name}")
    lines.append("")
    lines.append("To execute: evonest_improve(project, proposal_id='<filename>')")
    lines.append("To mark done: evonest_proposals(project, action='done', filename='<filename>')")
    return "\n".join(lines)
