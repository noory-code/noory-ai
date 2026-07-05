"""Resolve project-scoped paths for the .noory/rag/ state directory.

The MCP server is launched by `uv --directory <plugin>/server run …`, which
sets the process cwd to the plugin's server folder — NOT the user's project
root. So `os.getcwd()` is the wrong default on every platform (macOS /
Linux / Windows). The project root must be supplied explicitly via an env
variable. Claude Code wires `RAG_PROJECT_ROOT` from `${CLAUDE_PROJECT_DIR}`
via `.mcp.json`; Codex wires it from `${CODEX_PROJECT_DIR}` via the Codex
plugin manifest.

Resolution order for the project root:
  1. Explicit `cwd` argument (used by tests).
  2. `RAG_PROJECT_ROOT` env var (production path).
  3. `CLAUDE_PROJECT_DIR` env var (defensive fallback).
  4. `CODEX_PROJECT_DIR` env var (defensive fallback).
  4. None of the above → raise :class:`RagPathsConfigError`. We deliberately
     do NOT fall back to `os.getcwd()` — that path would silently anchor the
     index in the plugin cache directory and reproduce the project-isolation
     bug.

All filesystem ops go through :mod:`os.environ` and :mod:`pathlib`, so the
resolver is OS-independent and works the same way on Windows as on POSIX.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

STATE_DIR_NAME = ".noory/rag"

PROJECT_ROOT_ENV = "RAG_PROJECT_ROOT"
CLAUDE_PROJECT_DIR_ENV = "CLAUDE_PROJECT_DIR"
CODEX_PROJECT_DIR_ENV = "CODEX_PROJECT_DIR"


class RagPathsConfigError(RuntimeError):
    """Raised when neither the explicit cwd arg nor any expected env var is set."""


def _resolve_project_root(cwd: Path | str | None) -> Path:
    if cwd is not None:
        return Path(cwd).resolve()
    for var in (PROJECT_ROOT_ENV, CLAUDE_PROJECT_DIR_ENV, CODEX_PROJECT_DIR_ENV):
        raw = os.environ.get(var)
        if raw and raw.strip():
            return Path(raw.strip()).expanduser().resolve()
    raise RagPathsConfigError(
        f"project root unresolved: set ${PROJECT_ROOT_ENV} "
        f"(plugin MCP config should wire it from the active project dir). "
        f"This server was launched via `uv --directory`, so its cwd is the "
        f"plugin cache — falling back to cwd would corrupt project isolation."
    )


@dataclass(frozen=True)
class RagPaths:
    project_root: Path
    state_dir: Path
    raw_dir: Path
    settings_file: Path
    probes_file: Path
    feedback_file: Path
    manifest_file: Path
    vec_db: Path
    graph_dir: Path
    cache_dir: Path

    @classmethod
    def from_cwd(cls, cwd: Path | str | None = None) -> "RagPaths":
        root = _resolve_project_root(cwd)
        state = root / STATE_DIR_NAME
        return cls(
            project_root=root,
            state_dir=state,
            raw_dir=state / "raw",
            settings_file=state / "settings.json",
            probes_file=state / "probes.json",
            feedback_file=state / "feedback.json",
            manifest_file=state / "manifest.json",
            vec_db=state / "vec.db",
            graph_dir=state / "graph",
            cache_dir=state / "cache",
        )

    def ensure_state_layout(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        gitkeep = self.raw_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    def state_exists(self) -> bool:
        return self.state_dir.exists() and self.settings_file.exists()

    def ensure_project_gitignore(self) -> bool:
        """Append `.noory/rag/` to the project root .gitignore if missing.

        Returns True if a line was added, False if already present or no file written.
        """
        gi = self.project_root / ".gitignore"
        line = f"{STATE_DIR_NAME}/"
        if gi.exists():
            existing = gi.read_text(encoding="utf-8").splitlines()
            if any(s.strip().rstrip("/") == STATE_DIR_NAME for s in existing):
                return False
            with gi.open("a", encoding="utf-8") as f:
                if existing and existing[-1].strip() != "":
                    f.write("\n")
                f.write(f"# rag local state\n{line}\n")
            return True
        gi.write_text(f"# rag local state\n{line}\n", encoding="utf-8")
        return True
