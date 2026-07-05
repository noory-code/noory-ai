"""List every available skill (one per line). Plugin-namespaced skills are emitted
as ``<plugin>:<skill>``. Caller should pipe to ``sort -u`` for deduplication.

Pure stdlib — cross-platform (no find/bash). Failures surface (unlike the
best-effort append-log.py) since ``/skill-stats`` invokes this synchronously.

No shebang (CLAUDE.md) — invoked as ``python3 list-all-skills.py``.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path


def scan_dir(root: Path, namespace: str) -> None:
    """Emit each ``<root>/**/SKILL.md``'s containing-directory name (namespaced if given)."""
    if not root.is_dir():
        return
    for skill_md in root.rglob("SKILL.md"):
        if not skill_md.is_file():
            continue
        name = skill_md.parent.name
        print(f"{namespace}:{name}" if namespace else name)


def _plugin_name_for_skills_dir(skills_dir: Path) -> str:
    """Resolve a plugin namespace from a Codex plugin root's manifest when present."""
    plugin_root = skills_dir.parent
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    if manifest.is_file():
        try:
            name = json.loads(manifest.read_text(encoding="utf-8")).get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        except Exception:
            pass
    return plugin_root.name


def scan_codex_plugin_skills(root: Path) -> None:
    """Emit Codex plugin skills as ``<plugin>:<skill>``.

    Codex cache layouts can include version/hash directories under the plugin
    name. Reading the plugin manifest avoids guessing from path depth.
    """
    if not root.is_dir():
        return
    for skill_md in root.rglob("SKILL.md"):
        if not skill_md.is_file():
            continue
        skills_dir = skill_md.parent.parent
        if skills_dir.name != "skills":
            continue
        print(f"{_plugin_name_for_skills_dir(skills_dir)}:{skill_md.parent.name}")


def main() -> int:
    home = Path.home()

    # 1. User-global skills: ~/.claude/skills/<name>/SKILL.md
    scan_dir(home / ".claude" / "skills", "")
    scan_dir(home / ".codex" / "skills", "")

    # 2. Project-local skills.
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or ""
    if proj:
        scan_dir(Path(proj) / ".claude" / "skills", "")
        scan_dir(Path(proj) / ".codex" / "skills", "")

    # 3. Plugin skills installed via marketplaces — exact canonical shape only:
    #    ~/.claude/plugins/marketplaces/<marketplace>/plugins/<plugin>/skills/<skill>/SKILL.md
    #    Enforced via path parts relative to the marketplaces root (a substring check like
    #    "plugins" in parts is a no-op — every path here contains "plugins"). Stray
    #    SKILL.md files elsewhere in a marketplace checkout (docs examples, repo-root
    #    skills/, maintainer .claude/skills/) must not be emitted with a bogus namespace.
    marketplaces = home / ".claude" / "plugins" / "marketplaces"
    if marketplaces.is_dir():
        for skill_md in marketplaces.rglob("SKILL.md"):
            if not skill_md.is_file():
                continue
            rel = skill_md.relative_to(marketplaces).parts
            # exactly (<mp>, "plugins", <plugin>, "skills", <skill>, "SKILL.md")
            if len(rel) != 6 or rel[1] != "plugins" or rel[3] != "skills":
                continue
            print(f"{rel[2]}:{rel[4]}")  # <plugin>:<skill>

    # 4. Codex plugin cache / local plugin skills.
    scan_codex_plugin_skills(home / ".codex" / "plugins")

    return 0


if __name__ == "__main__":
    sys.exit(main())
