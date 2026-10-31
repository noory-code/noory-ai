#!/usr/bin/env python3
"""Run the installed Codex plugin's companion script with the given arguments.

Driver and review commands used to call the companion by an absolute path that
named one user's home directory and one plugin version, so every plugin update
or other machine broke them silently. This resolves the script at run time, in
order: the `STAGE_CODEX_COMPANION` override, the install path Claude Code
records for `codex@openai-codex`, then the highest cached version.

Usage:
    python3 stage/scripts/codex_companion.py task --model <model> ... "<prompt>"
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ID = "codex@openai-codex"
OVERRIDE_ENV = "STAGE_CODEX_COMPANION"
SCRIPT_RELATIVE = Path("scripts", "codex-companion.mjs")
# Prefer the install a user chose for every project over narrower scopes.
SCOPE_ORDER = ("user", "managed", "project", "local")


def plugins_root(home: Path) -> Path:
    return home / ".claude" / "plugins"


def recorded_install(home: Path) -> Path | None:
    """Return the companion under the install path Claude Code recorded, if usable."""

    try:
        data = json.loads(
            (plugins_root(home) / "installed_plugins.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None
    entries = data.get("plugins", {}).get(PLUGIN_ID) if isinstance(data, dict) else None
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        return None
    ranked = sorted(
        (entry for entry in entries if isinstance(entry, dict)),
        key=lambda entry: (
            SCOPE_ORDER.index(entry["scope"])
            if entry.get("scope") in SCOPE_ORDER
            else len(SCOPE_ORDER)
        ),
    )
    for entry in ranked:
        install_path = entry.get("installPath")
        if isinstance(install_path, str) and install_path:
            script = Path(install_path) / SCRIPT_RELATIVE
            if script.is_file():
                return script
    return None


def version_key(name: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", name))


def cached_install(home: Path) -> Path | None:
    """Return the companion of the highest cached plugin version, if any."""

    cache = plugins_root(home) / "cache" / "openai-codex" / "codex"
    if not cache.is_dir():
        return None
    candidates = [
        version_dir / SCRIPT_RELATIVE
        for version_dir in cache.iterdir()
        if (version_dir / SCRIPT_RELATIVE).is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda script: version_key(script.parent.parent.name))


def resolve_companion(environ: dict[str, str], home: Path) -> Path | None:
    override = environ.get(OVERRIDE_ENV, "")
    if override:
        return Path(override)
    return recorded_install(home) or cached_install(home)


def main(argv: list[str]) -> int:
    script = resolve_companion(dict(os.environ), Path.home())
    if script is None or not script.is_file():
        searched = f"{OVERRIDE_ENV}, {PLUGIN_ID} in installed_plugins.json, plugin cache"
        detail = f" ({script})" if script is not None else ""
        print(
            f"codex_companion: no Codex companion script found{detail}; searched {searched}",
            file=sys.stderr,
        )
        return 127
    node = shutil.which("node")
    if node is None:
        print("codex_companion: `node` is not on PATH", file=sys.stderr)
        return 127
    return subprocess.run([node, str(script), *argv]).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
