"""Tests for CLI (cli.py)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run evonest CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "evonest", *args],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )


def test_cli_help() -> None:
    """--help should print usage and exit 0."""
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_main_no_command() -> None:
    """cli_main() with no subcommand should exit 1."""
    from evonest.cli import cli_main

    with patch("sys.argv", ["evonest"]):
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        assert exc_info.value.code == 1


def test_cli_init(tmp_path: Path) -> None:
    """evonest init should create .evonest/ directory."""
    result = _run_cli("init", str(tmp_path))
    assert result.returncode == 0
    assert "Initialized" in result.stdout
    assert (tmp_path / ".evonest" / "config.json").exists()


def test_cli_init_already_initialized(tmp_path: Path) -> None:
    """evonest init on already initialized project should be idempotent."""
    _run_cli("init", str(tmp_path))
    result = _run_cli("init", str(tmp_path))
    assert result.returncode == 0
    assert "already initialized" in result.stdout.lower() or "Initialized" in result.stdout


def test_cli_status(tmp_project: Path) -> None:
    """evonest status should print project summary."""
    result = _run_cli("status", str(tmp_project))
    assert result.returncode == 0
    assert "Cycles:" in result.stdout


def test_cli_history_empty(tmp_project: Path) -> None:
    """evonest history should work with no history."""
    result = _run_cli("history", str(tmp_project))
    assert result.returncode == 0
    assert "No cycle history" in result.stdout


def test_cli_progress(tmp_project: Path) -> None:
    """evonest progress should print progress report."""
    result = _run_cli("progress", str(tmp_project))
    assert result.returncode == 0
    assert "Total cycles:" in result.stdout


def test_cli_config_read(tmp_project: Path) -> None:
    """evonest config should print config JSON."""
    result = _run_cli("config", str(tmp_project))
    assert result.returncode == 0
    assert "model" in result.stdout
    assert "max_cycles_per_run" in result.stdout


def test_cli_config_set(tmp_project: Path) -> None:
    """evonest config --set should update a value."""
    result = _run_cli("config", str(tmp_project), "--set", "model", "opus")
    assert result.returncode == 0
    assert "Set model = opus" in result.stdout

    # Verify persisted
    result2 = _run_cli("config", str(tmp_project))
    assert '"opus"' in result2.stdout


def test_cli_identity_read(tmp_project: Path) -> None:
    """evonest identity should print identity content."""
    result = _run_cli("identity", str(tmp_project))
    assert result.returncode == 0


def test_cli_identity_set(tmp_project: Path) -> None:
    """evonest identity --set FILE should update identity."""
    id_file = tmp_project / "new-identity.md"
    id_file.write_text("# Test Project\nA CLI test.")

    result = _run_cli("identity", str(tmp_project), "--set", str(id_file))
    assert result.returncode == 0
    assert "Identity updated" in result.stdout

    result2 = _run_cli("identity", str(tmp_project))
    assert "# Test Project" in result2.stdout


def test_cli_identity_refresh_updates(tmp_project: Path) -> None:
    """evonest identity --refresh with 'y' input should update identity.md."""
    import argparse

    from evonest.cli import _dispatch

    draft_content = "# Refreshed Identity\nNew content."
    with patch("evonest.core.initializer._draft_identity_via_claude", return_value=draft_content):
        with patch("builtins.input", return_value="y"):
            args = argparse.Namespace(
                command="identity",
                project=str(tmp_project),
                refresh=True,
                set=None,
            )
            _dispatch(args)

    from evonest.core.state import ProjectState

    state = ProjectState(tmp_project)
    assert "# Refreshed Identity" in state.read_identity()


def test_cli_identity_refresh_cancelled(tmp_project: Path) -> None:
    """evonest identity --refresh with 'n' input should leave identity.md unchanged."""
    import argparse

    from evonest.cli import _dispatch
    from evonest.core.state import ProjectState

    state = ProjectState(tmp_project)
    original = state.read_identity()

    draft_content = "# Completely Different\nShould not be saved."
    with patch("evonest.core.initializer._draft_identity_via_claude", return_value=draft_content):
        with patch("builtins.input", return_value="n"):
            args = argparse.Namespace(
                command="identity",
                project=str(tmp_project),
                refresh=True,
                set=None,
            )
            _dispatch(args)

    assert state.read_identity() == original


def test_cli_backlog_list_empty(tmp_project: Path) -> None:
    """evonest backlog should list empty backlog."""
    result = _run_cli("backlog", str(tmp_project))
    assert result.returncode == 0
    assert "empty" in result.stdout.lower()


def test_cli_backlog_add(tmp_project: Path) -> None:
    """evonest backlog add should add items."""
    result = _run_cli("backlog", str(tmp_project), "add", "--title", "New task")
    assert result.returncode == 0
    assert "Added" in result.stdout


def test_cli_backlog_prune(tmp_project: Path) -> None:
    """evonest backlog prune should work."""
    result = _run_cli("backlog", str(tmp_project), "prune")
    assert result.returncode == 0
    assert "Pruned" in result.stdout


def test_resolve_project_explicit() -> None:
    """_resolve_project returns the explicit path unchanged."""
    from evonest.cli import _resolve_project

    assert _resolve_project("/some/path") == "/some/path"


def test_resolve_project_env_var(tmp_project: Path) -> None:
    """_resolve_project uses EVONEST_PROJECT env var when no explicit path."""
    import os
    from unittest.mock import patch

    from evonest.cli import _resolve_project

    with patch.dict(os.environ, {"EVONEST_PROJECT": str(tmp_project)}):
        result = _resolve_project(None)
    assert result == str(tmp_project)


def test_resolve_project_cwd_walk(tmp_project: Path) -> None:
    """_resolve_project walks up from cwd to find .evonest/."""
    from unittest.mock import patch

    from evonest.cli import _resolve_project

    subdir = tmp_project / "src" / "pkg"
    subdir.mkdir(parents=True)

    with patch("evonest.cli.Path") as mock_path_cls:
        # Make Path.cwd() return our subdir
        mock_cwd = MagicMock()
        mock_cwd.__truediv__ = lambda self, other: subdir / other
        mock_cwd.parents = subdir.parents
        mock_path_cls.cwd.return_value = subdir

        result = _resolve_project(None)
    assert result == str(tmp_project)


def test_resolve_project_not_found(tmp_path: Path) -> None:
    """_resolve_project raises FileNotFoundError when no .evonest/ found."""
    from unittest.mock import patch

    from evonest.cli import _resolve_project

    with patch("evonest.cli.Path") as mock_path_cls:
        mock_path_cls.cwd.return_value = tmp_path
        # No .evonest/ in tmp_path → should raise
        import pytest

        with pytest.raises(FileNotFoundError, match=".evonest"):
            _resolve_project(None)


def test_cli_status_cwd(tmp_project: Path) -> None:
    """evonest status without project arg works from project cwd."""
    result = subprocess.run(
        [sys.executable, "-m", "evonest", "status"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(tmp_project),
    )
    assert result.returncode == 0
    assert "Cycles:" in result.stdout
