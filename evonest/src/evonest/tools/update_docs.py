"""evonest_update_docs — sync skills/commands/agents/rules/CLAUDE.md with code."""

from __future__ import annotations

import json

from evonest.server import mcp

_VALID_TARGETS = {"all", "skills", "commands", "agents", "rules", "claude_md"}


@mcp.tool()
async def evonest_update_docs(
    project: str,
    target: str = "all",
    dry_run: bool = True,
) -> str:
    """Sync Claude Code files (skills, commands, agents, rules, CLAUDE.md) with source code.

    Reads the project's MCP tool definitions and docstrings, then proposes updates
    to any Claude Code documentation files that are out of sync.

    By default runs in dry_run mode — returns a JSON diff for review without
    writing anything. Set dry_run=False to apply changes directly.

    Args:
        project: Absolute path to the target project.
        target: Which files to sync. One of:
                "all" (default), "skills", "commands", "agents", "rules", "claude_md".
        dry_run: If True (default), return proposed changes as JSON without writing.
                 If False, apply changes to disk and return a summary.
    """
    from pathlib import Path

    from evonest.core.config import EvonestConfig
    from evonest.core.doc_updater import (
        apply_doc_changes,
        format_changes_summary,
        run_update_docs,
    )
    from evonest.core.state import ProjectState

    if target not in _VALID_TARGETS:
        return (
            f"Invalid target '{target}'. "
            f"Valid values: {', '.join(sorted(_VALID_TARGETS))}"
        )

    state = ProjectState(project)
    config = EvonestConfig.load(state.root)

    state.log(f"[update_docs] starting (target={target}, dry_run={dry_run})")
    changes = run_update_docs(Path(project), target=target, model=config.model)

    if not changes:
        return "No documentation changes needed — all files are up to date."

    if dry_run:
        payload = {
            "dry_run": True,
            "change_count": len(changes),
            "files": [
                {
                    "path": c.path,
                    "action": c.action,
                    "reason": c.reason,
                    "new_content": c.new_content,
                }
                for c in changes
            ],
        }
        summary = format_changes_summary(changes)
        diff_json = json.dumps(payload, indent=2, ensure_ascii=False)
        return f"{summary}\n\nCall evonest_update_docs with dry_run=False to apply.\n\n{diff_json}"

    applied = apply_doc_changes(Path(project), changes)
    state.log(f"[update_docs] applied {len(applied)} file(s): {applied}")
    return (
        f"Updated {len(applied)} file(s):\n"
        + "\n".join(f"  - {p}" for p in applied)
    )
