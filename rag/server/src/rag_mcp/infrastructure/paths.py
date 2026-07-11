"""Resolve project-scoped paths for the .noory/rag/ state directory.

Claude Code launches the MCP server with `uv --directory`, so its manifest
supplies `RAG_PROJECT_ROOT` explicitly. Codex launches with `uv run --project`,
which selects the plugin project without changing the workspace cwd; its
manifest sets `RAG_PROJECT_ROOT_FROM_CWD=1` to opt into that host contract.

Resolution order for the project root:
  1. Explicit `cwd` argument (used by tests).
  2. `RAG_PROJECT_ROOT` env var (production path).
  3. `CLAUDE_PROJECT_DIR` env var (defensive fallback).
  4. Process cwd only when `RAG_PROJECT_ROOT_FROM_CWD=1` is explicitly set by
     the Codex plugin manifest.
  5. None of the above → raise :class:`RagPathsConfigError`.

All filesystem ops go through :mod:`os.environ` and :mod:`pathlib`, so the
resolver is OS-independent and works the same way on Windows as on POSIX.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

STATE_DIR_NAME = ".noory/rag"

PROJECT_ROOT_ENV = "RAG_PROJECT_ROOT"
PROJECT_ROOT_FROM_CWD_ENV = "RAG_PROJECT_ROOT_FROM_CWD"
CLAUDE_PROJECT_DIR_ENV = "CLAUDE_PROJECT_DIR"


class RagPathsConfigError(RuntimeError):
    """Raised when neither the explicit cwd arg nor any expected env var is set."""


def _resolve_project_root(cwd: Path | str | None) -> Path:
    if cwd is not None:
        return Path(cwd).resolve()
    for var in (PROJECT_ROOT_ENV, CLAUDE_PROJECT_DIR_ENV):
        raw = os.environ.get(var)
        if raw and raw.strip():
            return Path(raw.strip()).expanduser().resolve()
    if os.environ.get(PROJECT_ROOT_FROM_CWD_ENV) == "1":
        return Path.cwd().resolve()
    raise RagPathsConfigError(
        f"project root unresolved: set ${PROJECT_ROOT_ENV} "
        f"or opt into the verified Codex cwd contract with "
        f"${PROJECT_ROOT_FROM_CWD_ENV}=1."
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
