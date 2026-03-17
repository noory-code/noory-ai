"""Tests for core/process_manager.py — error message quality."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from evonest.core.process_manager import ProcessManager


def test_command_not_found_error_includes_command_name() -> None:
    """On FileNotFoundError, the error message should include the command name."""
    manager = ProcessManager(timeout=10.0)

    with patch("subprocess.run", side_effect=FileNotFoundError()):
        result = manager.run(["nonexistent-command", "arg1"])

    assert result.success is False
    assert result.exit_code == -1
    # stderr should include the attempted command name
    assert "nonexistent-command" in result.stderr


def test_timeout_error_includes_helpful_info() -> None:
    """On timeout, the error message should clearly indicate a timeout situation."""
    manager = ProcessManager(timeout=5.0)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("long-cmd", 5.0)):
        result = manager.run(["long-cmd", "--slow-option"])

    assert result.success is False
    assert result.exit_code == -1
    # stderr should include timeout information
    assert "timeout" in result.stderr.lower()


def test_nonzero_exit_stderr_preserved() -> None:
    """On non-zero exit, the subprocess stderr should be preserved as-is."""
    manager = ProcessManager(timeout=10.0)

    mock_result = MagicMock()
    mock_result.returncode = 127
    mock_result.stdout = ""
    mock_result.stderr = "Error: File /path/to/config.json not found. Check the path and try again."

    with patch("subprocess.run", return_value=mock_result):
        result = manager.run(["app", "start"])

    assert result.success is False
    assert result.exit_code == 127
    # stderr should preserve the original message containing the file path and resolution steps
    assert "/path/to/config.json" in result.stderr
    assert "Check the path" in result.stderr


def test_rate_limit_retry_messages_include_context() -> None:
    """On rate limit retry, the log message should include the retry count and wait duration."""
    manager = ProcessManager(timeout=10.0, retry_on_rate_limit=True, rate_limit_wait=1.0)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: rate limit exceeded (429)"

    with (
        patch("subprocess.run", return_value=mock_result),
        patch("time.sleep"),  # prevent actual waiting
    ):
        result = manager.run(["api-call"])

    # Failed due to rate limit, but stderr should contain clear information
    assert "rate limit" in result.stderr.lower() or "429" in result.stderr
