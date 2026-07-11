"""Tests for core/claude_runner.py."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from evonest.core.claude_runner import ClaudeResult, run


def test_claude_result_dataclass() -> None:
    r = ClaudeResult(output="hello", exit_code=0, success=True)
    assert r.output == "hello"
    assert r.exit_code == 0
    assert r.success is True
    assert r.stderr == ""


def test_claude_result_stderr_field() -> None:
    r = ClaudeResult(output="hello", exit_code=0, success=True, stderr="some error")
    assert r.stderr == "some error"


def test_claude_result_stderr_defaults_to_empty() -> None:
    r = ClaudeResult(output="hello", exit_code=0, success=True)
    assert r.stderr == ""


def test_run_success() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "  observation output  "
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = run("test prompt", model="sonnet", max_turns=5)

    assert result.success is True
    assert result.output == "observation output"
    assert result.exit_code == 0
    assert result.stderr == ""

    args = mock_run.call_args
    cmd = args[0][0]
    assert cmd[0] == "claude"
    assert cmd[1] == "-p"
    assert cmd[2] == "test prompt"
    assert "--model" in cmd
    assert "sonnet" in cmd
    assert "--max-turns" in cmd
    assert "5" in cmd


def test_run_nonzero_exit() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "some output"
    mock_result.stderr = "error detail"
    mock_result.returncode = 1

    with patch("subprocess.run", return_value=mock_result):
        result = run("test prompt")

    assert result.success is False
    assert result.exit_code == 1
    assert result.stderr == "error detail"


def test_run_empty_output() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "   "
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        result = run("test prompt")

    assert result.success is False
    assert result.output == ""


def test_run_timeout() -> None:
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 600)):
        result = run("test prompt")

    assert result.success is False
    assert result.exit_code == -1


def test_run_command_not_found() -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        result = run("test prompt")

    assert result.success is False
    assert result.exit_code == -1


def test_run_with_cwd() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "output"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        run("prompt", cwd="/some/path")

    kwargs = mock_run.call_args[1]
    assert kwargs["cwd"] == "/some/path"


def test_run_allowed_tools() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "output"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        run("prompt", allowed_tools="Read,Write")

    cmd = mock_run.call_args[0][0]
    assert "--allowedTools" in cmd
    idx = cmd.index("--allowedTools")
    assert cmd[idx + 1] == "Read,Write"


def test_run_stderr_captured() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "output"
    mock_result.stderr = "  warning: something\n"
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result):
        result = run("test prompt")

    assert result.stderr == "warning: something"
    assert result.success is True


def test_run_codex_backend_uses_noninteractive_exec() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "codex output"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with (
        patch.dict("os.environ", {"EVONEST_AGENT_BACKEND": "codex"}, clear=False),
        patch("subprocess.run", return_value=mock_result) as mock_run,
    ):
        result = run("test prompt", allowed_tools="Read,Write")

    cmd = mock_run.call_args[0][0]
    assert cmd[:2] == ["codex", "exec"]
    assert "--ephemeral" in cmd
    assert "--ignore-user-config" in cmd
    assert "danger-full-access" in cmd
    assert "sonnet" not in cmd
    assert result.success is True


def test_run_codex_backend_uses_read_only_for_nonwriting_phase() -> None:
    mock_result = MagicMock()
    mock_result.stdout = "codex output"
    mock_result.stderr = ""
    mock_result.returncode = 0

    with (
        patch.dict("os.environ", {"EVONEST_AGENT_BACKEND": "codex"}, clear=False),
        patch("subprocess.run", return_value=mock_result) as mock_run,
    ):
        run("test prompt", allowed_tools="Read,Glob,Grep,Bash")

    cmd = mock_run.call_args[0][0]
    assert "read-only" in cmd


def test_run_rejects_unknown_backend() -> None:
    with (
        patch.dict("os.environ", {"EVONEST_AGENT_BACKEND": "unknown"}, clear=False),
        pytest.raises(ValueError, match="EVONEST_AGENT_BACKEND"),
    ):
        run("test prompt")


def test_command_not_found_error_message_contains_command() -> None:
    """On FileNotFoundError, the error message should include the command that was attempted."""
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        result = run("test prompt")

    assert result.success is False
    assert result.exit_code == -1
    # stderr should include the attempted command ('claude')
    assert "claude" in result.stderr.lower()


def test_timeout_error_message_contains_duration() -> None:
    """On timeout, the error message should include the timeout duration."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 600)):
        result = run("test prompt")

    assert result.success is False
    assert result.exit_code == -1
    # stderr should include the timeout duration (600 seconds)
    assert "600" in result.stderr or "timeout" in result.stderr.lower()
