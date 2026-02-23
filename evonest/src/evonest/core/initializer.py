"""Project initialization — create .evonest/ with templates."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path

logger = logging.getLogger("evonest")


def _get_template(name: str) -> str:
    """Read a template file from the package."""
    ref = resources.files("evonest") / "templates" / name
    return ref.read_text(encoding="utf-8")


def _clean_identity_draft(raw: str) -> str:
    """Strip LLM preamble and code fences from identity.md draft output."""
    text = raw.strip()

    # If the output is wrapped in a code fence, extract the content inside
    fence_match = re.search(r"```(?:markdown|md)?\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Strip any preamble before the first markdown heading
    heading_match = re.search(r"^(#\s+.+)$", text, re.MULTILINE)
    if heading_match:
        text = text[heading_match.start() :]

    return text.strip()


def _draft_identity_via_claude(project: Path) -> str | None:
    """Call claude -p to explore the project and produce an identity.md draft.

    Falls back to None (use blank template) if claude is unavailable or fails.
    """
    try:
        from evonest.core import claude_runner

        prompt_ref = resources.files("evonest") / "prompts" / "identity_draft.md"
        prompt = prompt_ref.read_text(encoding="utf-8")
        result = claude_runner.run(
            prompt,
            model="haiku",
            max_turns=15,
            allowed_tools=claude_runner.OBSERVE_TOOLS,
            cwd=str(project),
        )
        if result.success and result.output.strip():
            return _clean_identity_draft(result.output)
    except Exception:
        logger.debug("identity draft via claude failed", exc_info=True)
    return None


def init_project(path: str | Path, level: str = "standard") -> str:
    """Initialize .evonest/ in a project directory.

    Creates config, identity, progress, backlog templates and required subdirectories.
    Adds .evonest/ to the project's .gitignore if not already present.

    Args:
        path: Path to the target project directory.
        level: Analysis depth preset — "quick", "standard", or "deep".
               Sets active_level in config.json.

    Returns a status message.
    """
    project = Path(path).resolve()
    if not project.is_dir():
        raise FileNotFoundError(f"Directory not found: {project}")

    evonest_dir = project / ".evonest"
    created_files: list[str] = []

    # Create directories
    for d in (
        evonest_dir,
        evonest_dir / "history",
        evonest_dir / "logs",
        evonest_dir / "stimuli",
        evonest_dir / "stimuli" / ".processed",
        evonest_dir / "decisions",
        evonest_dir / "proposals",
    ):
        d.mkdir(parents=True, exist_ok=True)

    # Copy templates (skip if already exists)
    template_files = {
        "config.json": "config.json",
        "identity.md": "identity.md",
        "progress.json": "progress.json",
        "backlog.json": "backlog.json",
    }

    for template_name, target_name in template_files.items():
        target = evonest_dir / target_name
        if not target.exists():
            if template_name == "identity.md":
                # Try to auto-draft identity.md using Claude
                draft = _draft_identity_via_claude(project)
                content = draft if draft else _get_template("identity.md")
            else:
                content = _get_template(template_name)
            # Inject selected level and populate full persona toggle maps
            if template_name == "config.json":
                try:
                    from evonest.core.config import _strip_jsonc_comments
                    from evonest.core.mutations import _load_builtin

                    cfg_data = json.loads(_strip_jsonc_comments(content))
                    if level != "standard":
                        cfg_data["active_level"] = level
                    # Populate full toggle maps from built-in mutations
                    cfg_data["personas"] = {
                        p["id"]: True for p in _load_builtin("personas.json") if "id" in p
                    }
                    cfg_data["adversarials"] = {
                        a["id"]: True for a in _load_builtin("adversarial.json") if "id" in a
                    }
                    content = json.dumps(cfg_data, indent=2, ensure_ascii=False) + "\n"
                except (json.JSONDecodeError, ImportError):
                    pass  # Leave as-is if parsing fails
            # Inject initialized_at into progress.json
            if template_name == "progress.json":
                try:
                    prog_data = json.loads(content)
                    prog_data.setdefault("activation", {})["initialized_at"] = datetime.now(
                        UTC
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                    content = json.dumps(prog_data, indent=2, ensure_ascii=False) + "\n"
                except json.JSONDecodeError:
                    pass
            target.write_text(content, encoding="utf-8")
            created_files.append(target_name)

    # Create empty dynamic mutation files
    for name in ("dynamic-personas.json", "dynamic-adversarials.json"):
        target = evonest_dir / name
        if not target.exists():
            target.write_text(json.dumps([], indent=2) + "\n", encoding="utf-8")
            created_files.append(name)

    # Create empty advisor + environment + scout cache files
    for name in ("advice.json", "environment.json", "scout.json"):
        target = evonest_dir / name
        if not target.exists():
            target.write_text(json.dumps({}, indent=2) + "\n", encoding="utf-8")
            created_files.append(name)

    # Update .gitignore
    gitignore = project / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if ".evonest" not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\n# Evonest evolution data\n.evonest/\n")
    else:
        gitignore.write_text("# Evonest evolution data\n.evonest/\n", encoding="utf-8")

    lines = [f"Initialized: {evonest_dir}"]
    if created_files:
        lines.append(f"Created: {', '.join(created_files)}")
    lines.extend(
        [
            "",
            "Next steps:",
            f"  1. Edit {evonest_dir / 'identity.md'} — describe your project",
            f"  2. Edit {evonest_dir / 'config.json'} — set verify commands",
            f"  3. Run first analysis: evonest analyze {project}",
            f'     or via MCP:        evonest_analyze(project="{project}")',
        ]
    )
    return "\n".join(lines)
