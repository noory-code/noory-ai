"""doc_updater — sync skills/commands/agents/rules/CLAUDE.md with source code."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Literal

logger = logging.getLogger("evonest")

DocAction = Literal["update", "create"]

# Glob patterns for each target category
_TARGET_GLOBS: dict[str, list[str]] = {
    "skills": ["skills/**/*.md", ".claude/skills/**/*.md"],
    "commands": ["commands/*.md", ".claude/commands/*.md"],
    "agents": [".claude/agents/*.md"],
    "rules": [".claude/rules/*.md"],
    "claude_md": ["CLAUDE.md"],
}


@dataclass
class DocChange:
    """A proposed change to a single documentation file."""

    path: str  # relative to project root
    action: DocAction
    current_content: str
    new_content: str
    reason: str


def _load_prompt() -> str:
    ref = resources.files("evonest") / "prompts" / "update_docs.md"
    return ref.read_text(encoding="utf-8")


def _collect_targets(project: Path, target: str) -> dict[str, str]:
    """Return {relative_path: content} for all existing target files."""
    globs = _TARGET_GLOBS.get(target, []) if target != "all" else [
        g for patterns in _TARGET_GLOBS.values() for g in patterns
    ]
    result: dict[str, str] = {}
    for pattern in globs:
        for path in sorted(project.glob(pattern)):
            if path.is_file():
                rel = str(path.relative_to(project))
                try:
                    result[rel] = path.read_text(encoding="utf-8")
                except OSError as exc:
                    logger.warning("update_docs: cannot read %s: %s", rel, exc)
    return result


def _parse_llm_output(raw: str) -> list[DocChange]:
    """Extract DocChange list from LLM JSON output."""
    # Strip code fences if present
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # Find outermost JSON object
    brace = text.find("{")
    if brace != -1:
        text = text[brace:]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("update_docs: LLM output is not valid JSON: %s", exc)
        return []

    changes: list[DocChange] = []
    for item in data.get("files", []):
        try:
            changes.append(
                DocChange(
                    path=item["path"],
                    action=item.get("action", "update"),
                    current_content=item.get("current_content", ""),
                    new_content=item["new_content"],
                    reason=item.get("reason", ""),
                )
            )
        except (KeyError, TypeError) as exc:
            logger.warning("update_docs: skipping malformed entry: %s", exc)
    return changes


def run_update_docs(
    project: Path,
    target: str,
    model: str = "sonnet",
    max_turns: int = 20,
) -> list[DocChange]:
    """Run the LLM-based docs sync and return proposed changes.

    No files are written — caller decides whether to apply.
    """
    from evonest.core import claude_runner

    targets = _collect_targets(project, target)
    if not targets:
        logger.info("update_docs: no target files found for target=%s", target)
        return []

    prompt = _load_prompt()

    # Append current target file contents so LLM can see what exists
    sections = [prompt, "\n\n---\n\n## Current target file contents\n"]
    for rel, content in targets.items():
        sections.append(f"\n### `{rel}`\n```\n{content}\n```\n")

    full_prompt = "".join(sections)

    result = claude_runner.run(
        full_prompt,
        model=model,
        max_turns=max_turns,
        allowed_tools=claude_runner.EXECUTE_TOOLS,
        cwd=str(project),
    )

    if not result.success:
        logger.warning("update_docs: claude run failed: %s", result.stderr[:200])
        return []

    return _parse_llm_output(result.output)


def apply_doc_changes(project: Path, changes: list[DocChange]) -> list[str]:
    """Write proposed changes to disk. Returns list of modified relative paths."""
    applied: list[str] = []
    for change in changes:
        target_path = project / change.path
        if change.action == "create":
            target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            target_path.write_text(change.new_content, encoding="utf-8")
            applied.append(change.path)
            logger.info("update_docs: wrote %s (%s)", change.path, change.action)
        except OSError as exc:
            logger.warning("update_docs: failed to write %s: %s", change.path, exc)
    return applied


def format_changes_summary(changes: list[DocChange]) -> str:
    """Return a human-readable summary of proposed changes."""
    if not changes:
        return "No documentation changes needed — all files are up to date."

    lines = [f"{len(changes)} file(s) need updating:\n"]
    for change in changes:
        lines.append(f"  [{change.action.upper()}] {change.path}")
        lines.append(f"    → {change.reason}")
    return "\n".join(lines)
