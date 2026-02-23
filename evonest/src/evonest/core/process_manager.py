"""ProcessManager — subprocess 통신 추상화 레이어.

subprocess 호출의 복잡성(retry, timeout, stderr 처리)을 캡슐화하여
테스트 가능성과 안정성을 개선합니다.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("evonest")


@dataclass
class ProcessResult:
    """프로세스 실행 결과."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""
    elapsed_seconds: float = 0.0


_RATE_LIMIT_SIGNALS = ("rate limit", "429", "too many requests", "overloaded")


def _is_rate_limit(text: str) -> bool:
    """텍스트에 rate limit 시그널이 포함되어 있는지 확인."""
    lower = text.lower()
    return any(sig in lower for sig in _RATE_LIMIT_SIGNALS)


class ProcessManager:
    """subprocess 실행 및 통신을 관리하는 추상화 레이어."""

    def __init__(
        self,
        *,
        timeout: float = 600.0,
        retry_on_rate_limit: bool = True,
        rate_limit_wait: float = 30.0,
    ) -> None:
        """ProcessManager 초기화.

        Args:
            timeout: 프로세스 실행 타임아웃 (초).
            retry_on_rate_limit: rate limit 발생 시 재시도 여부.
            rate_limit_wait: rate limit 재시도 전 대기 시간 (초).
        """
        self.timeout = timeout
        self.retry_on_rate_limit = retry_on_rate_limit
        self.rate_limit_wait = rate_limit_wait

    def run(
        self,
        cmd: list[str],
        *,
        cwd: str | None = None,
        _retry_attempt: bool = True,
    ) -> ProcessResult:
        """명령어를 subprocess로 실행하고 결과를 반환.

        Args:
            cmd: 실행할 명령어 리스트.
            cwd: 작업 디렉토리.
            _retry_attempt: 내부 사용 - 재시도 허용 여부.

        Returns:
            ProcessResult with output, exit_code, success.
        """
        logger.info("subprocess starting: %s (cwd=%s)", " ".join(cmd), cwd)
        started_at = datetime.now()

        try:
            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=self.timeout,
            )
            elapsed = (datetime.now() - started_at).total_seconds()
            output = result.stdout.strip()
            stderr = result.stderr.strip()

            self._log_result(result.returncode, elapsed, output, stderr)

            # rate limit 감지 및 재시도
            if self.retry_on_rate_limit and _retry_attempt and _is_rate_limit(stderr):
                return self._retry_after_rate_limit(cmd, cwd, elapsed)

            return ProcessResult(
                output=output,
                exit_code=result.returncode,
                success=result.returncode == 0 and len(output) > 0,
                stderr=stderr,
                elapsed_seconds=elapsed,
            )

        except subprocess.TimeoutExpired as exc:
            elapsed = (datetime.now() - started_at).total_seconds()
            stderr_text = self._decode_stderr(exc.stderr)

            # rate limit 재시도
            if self.retry_on_rate_limit and _retry_attempt and _is_rate_limit(stderr_text):
                return self._retry_after_rate_limit(cmd, cwd, elapsed)

            logger.error("subprocess timed out after %.1fs (limit=%.0fs)", elapsed, self.timeout)
            return ProcessResult(
                output="",
                exit_code=-1,
                success=False,
                stderr=stderr_text or "timeout",
                elapsed_seconds=elapsed,
            )

        except FileNotFoundError:
            logger.error("command not found: %s", cmd[0])
            return ProcessResult(
                output="",
                exit_code=-1,
                success=False,
                stderr=f"command not found: {cmd[0]}",
                elapsed_seconds=0.0,
            )

    def _log_result(self, exit_code: int, elapsed: float, output: str, stderr: str) -> None:
        """실행 결과를 로깅."""
        if exit_code != 0:
            logger.warning(
                "subprocess exited with code %d after %.1fs. stderr: %s",
                exit_code,
                elapsed,
                stderr[:500] if stderr else "(none)",
            )
        elif not output:
            logger.warning(
                "subprocess exited 0 but produced no output after %.1fs. stderr: %s",
                elapsed,
                stderr[:500] if stderr else "(none)",
            )
        else:
            logger.info(
                "subprocess completed in %.1fs (output=%d chars)",
                elapsed,
                len(output),
            )

    def _retry_after_rate_limit(
        self, cmd: list[str], cwd: str | None, elapsed: float
    ) -> ProcessResult:
        """rate limit 발생 후 재시도."""
        logger.warning(
            "subprocess rate limited after %.1fs — waiting %.0fs before retry",
            elapsed,
            self.rate_limit_wait,
        )
        time.sleep(self.rate_limit_wait)
        return self.run(cmd, cwd=cwd, _retry_attempt=False)

    @staticmethod
    def _decode_stderr(stderr: bytes | str | None) -> str:
        """stderr를 문자열로 디코딩."""
        if stderr is None:
            return ""
        if isinstance(stderr, bytes):
            return stderr.decode(errors="replace")
        return stderr
