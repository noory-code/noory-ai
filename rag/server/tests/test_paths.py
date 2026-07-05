"""Unit tests for :mod:`rag_mcp.infrastructure.paths`."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from rag_mcp.infrastructure.paths import (
    CLAUDE_PROJECT_DIR_ENV,
    CODEX_PROJECT_DIR_ENV,
    PROJECT_ROOT_ENV,
    STATE_DIR_NAME,
    RagPaths,
    RagPathsConfigError,
)


def test_from_cwd_resolves_layout(tmp_path: Path) -> None:
    paths = RagPaths.from_cwd(tmp_path)
    assert paths.project_root == tmp_path.resolve()
    assert paths.state_dir == (tmp_path / STATE_DIR_NAME).resolve()
    assert paths.raw_dir.name == "raw"
    assert paths.settings_file.name == "settings.json"
    assert paths.vec_db.name == "vec.db"
    assert paths.graph_dir.name == "graph"


def test_ensure_state_layout_creates_dirs(tmp_path: Path) -> None:
    paths = RagPaths.from_cwd(tmp_path)
    paths.ensure_state_layout()
    assert paths.state_dir.is_dir()
    assert paths.raw_dir.is_dir()
    assert (paths.raw_dir / ".gitkeep").is_file()
    assert paths.cache_dir.is_dir()


def test_ensure_project_gitignore_creates_new_file(tmp_path: Path) -> None:
    paths = RagPaths.from_cwd(tmp_path)
    paths.ensure_state_layout()
    changed = paths.ensure_project_gitignore()
    assert changed is True
    gi = (tmp_path / ".gitignore").read_text()
    assert ".noory/rag/" in gi


def test_ensure_project_gitignore_idempotent(tmp_path: Path) -> None:
    paths = RagPaths.from_cwd(tmp_path)
    paths.ensure_state_layout()
    paths.ensure_project_gitignore()
    second = paths.ensure_project_gitignore()
    assert second is False
    assert (tmp_path / ".gitignore").read_text().count(".noory/rag/") == 1


def test_ensure_project_gitignore_appends(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n.env\n")
    paths = RagPaths.from_cwd(tmp_path)
    changed = paths.ensure_project_gitignore()
    assert changed is True
    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content
    assert ".noory/rag/" in content


def test_from_cwd_prefers_rag_project_root_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When `RAG_PROJECT_ROOT` is set, it wins over `os.getcwd()` —
    this is the production code path under `uv --directory`."""
    project = tmp_path / "real-project"
    project.mkdir()
    elsewhere = tmp_path / "plugin-cache" / "server"
    elsewhere.mkdir(parents=True)

    monkeypatch.setenv(PROJECT_ROOT_ENV, str(project))
    monkeypatch.delenv(CLAUDE_PROJECT_DIR_ENV, raising=False)
    monkeypatch.delenv(CODEX_PROJECT_DIR_ENV, raising=False)
    monkeypatch.chdir(elsewhere)

    paths = RagPaths.from_cwd()
    assert paths.project_root == project.resolve()
    assert paths.state_dir == (project / STATE_DIR_NAME).resolve()


def test_from_cwd_falls_back_to_claude_project_dir_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without `RAG_PROJECT_ROOT`, `CLAUDE_PROJECT_DIR` is the next pick —
    defensive fallback if `.mcp.json` ever drops the explicit wiring."""
    project = tmp_path / "claude-project"
    project.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    monkeypatch.delenv(PROJECT_ROOT_ENV, raising=False)
    monkeypatch.setenv(CLAUDE_PROJECT_DIR_ENV, str(project))
    monkeypatch.delenv(CODEX_PROJECT_DIR_ENV, raising=False)
    monkeypatch.chdir(elsewhere)

    paths = RagPaths.from_cwd()
    assert paths.project_root == project.resolve()


def test_from_cwd_falls_back_to_codex_project_dir_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without `RAG_PROJECT_ROOT` or `CLAUDE_PROJECT_DIR`, Codex project env is accepted."""
    project = tmp_path / "codex-project"
    project.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    monkeypatch.delenv(PROJECT_ROOT_ENV, raising=False)
    monkeypatch.delenv(CLAUDE_PROJECT_DIR_ENV, raising=False)
    monkeypatch.setenv(CODEX_PROJECT_DIR_ENV, str(project))
    monkeypatch.chdir(elsewhere)

    paths = RagPaths.from_cwd()
    assert paths.project_root == project.resolve()


def test_from_cwd_explicit_arg_overrides_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit cwd argument (used by tests) overrides env vars."""
    explicit = tmp_path / "explicit"
    explicit.mkdir()
    env_root = tmp_path / "env-root"
    env_root.mkdir()

    monkeypatch.setenv(PROJECT_ROOT_ENV, str(env_root))
    paths = RagPaths.from_cwd(explicit)
    assert paths.project_root == explicit.resolve()


def test_from_cwd_raises_when_no_explicit_arg_or_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No env, no arg → fail-fast.

    Falling back to `os.getcwd()` would silently use the plugin server
    directory under `uv --directory` and reintroduce the 0.1.0 isolation bug.
    """
    monkeypatch.delenv(PROJECT_ROOT_ENV, raising=False)
    monkeypatch.delenv(CLAUDE_PROJECT_DIR_ENV, raising=False)
    monkeypatch.delenv(CODEX_PROJECT_DIR_ENV, raising=False)
    monkeypatch.chdir(tmp_path)  # cwd is set but must NOT be used

    with pytest.raises(RagPathsConfigError, match=PROJECT_ROOT_ENV):
        RagPaths.from_cwd()


def test_from_cwd_treats_blank_env_as_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty / whitespace env values are not honored.

    `${CLAUDE_PROJECT_DIR}` can expand to an empty string in some shells if
    Claude Code didn't inject it; we must fail-fast rather than resolve `""`
    to cwd via `Path("").resolve()`.
    """
    monkeypatch.setenv(PROJECT_ROOT_ENV, "   ")
    monkeypatch.setenv(CLAUDE_PROJECT_DIR_ENV, "")
    monkeypatch.setenv(CODEX_PROJECT_DIR_ENV, "")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RagPathsConfigError):
        RagPaths.from_cwd()
