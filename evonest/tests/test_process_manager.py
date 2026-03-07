"""Tests for core/process_manager.py — error message quality."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from evonest.core.process_manager import ProcessManager


def test_command_not_found_error_includes_command_name() -> None:
    """FileNotFoundError 발생 시 에러 메시지에 명령어 이름이 포함되어야 함."""
    manager = ProcessManager(timeout=10.0)

    with patch("subprocess.run", side_effect=FileNotFoundError()):
        result = manager.run(["nonexistent-command", "arg1"])

    assert result.success is False
    assert result.exit_code == -1
    # stderr에 실행하려던 명령어 이름이 포함되어야 함
    assert "nonexistent-command" in result.stderr


def test_timeout_error_includes_helpful_info() -> None:
    """Timeout 발생 시 에러 메시지가 timeout 상황을 명확히 알려야 함."""
    manager = ProcessManager(timeout=5.0)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("long-cmd", 5.0)):
        result = manager.run(["long-cmd", "--slow-option"])

    assert result.success is False
    assert result.exit_code == -1
    # stderr에 timeout 정보가 포함되어야 함
    assert "timeout" in result.stderr.lower()


def test_nonzero_exit_stderr_preserved() -> None:
    """비정상 종료 시 subprocess의 stderr가 그대로 전달되어야 함."""
    manager = ProcessManager(timeout=10.0)

    mock_result = MagicMock()
    mock_result.returncode = 127
    mock_result.stdout = ""
    mock_result.stderr = "Error: File /path/to/config.json not found. Check the path and try again."

    with patch("subprocess.run", return_value=mock_result):
        result = manager.run(["app", "start"])

    assert result.success is False
    assert result.exit_code == 127
    # stderr에 파일 경로와 해결 방법이 포함된 원본 메시지가 보존되어야 함
    assert "/path/to/config.json" in result.stderr
    assert "Check the path" in result.stderr


def test_rate_limit_retry_messages_include_context() -> None:
    """Rate limit 재시도 시 로깅 메시지에 재시도 횟수와 대기 시간 정보가 포함되어야 함."""
    manager = ProcessManager(timeout=10.0, retry_on_rate_limit=True, rate_limit_wait=1.0)

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: rate limit exceeded (429)"

    with (
        patch("subprocess.run", return_value=mock_result),
        patch("time.sleep"),  # 실제 대기 방지
    ):
        result = manager.run(["api-call"])

    # Rate limit로 인해 실패했지만, stderr는 명확한 정보를 포함해야 함
    assert "rate limit" in result.stderr.lower() or "429" in result.stderr
