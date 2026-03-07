"""ProcessManager — abstraction layer for subprocess communication.

Encapsulates subprocess complexity (retry, timeout, stderr handling)
to improve testability and reliability.
"""

from __future__ import annotations

import logging
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("evonest")


@dataclass
class ProcessResult:
    """Result of a process execution."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""
    elapsed_seconds: float = 0.0


_RATE_LIMIT_SIGNALS = ("rate limit", "429", "too many requests", "overloaded")


def _is_rate_limit(text: str) -> bool:
    """Check whether the text contains a rate limit signal."""
    lower = text.lower()
    return any(sig in lower for sig in _RATE_LIMIT_SIGNALS)


class ProcessManager:
    """Abstraction layer for running and communicating with subprocesses."""

    def __init__(
        self,
        *,
        timeout: float = 600.0,
        retry_on_rate_limit: bool = True,
        rate_limit_wait: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize ProcessManager.

        Args:
            timeout: Process execution timeout in seconds.
            retry_on_rate_limit: Whether to retry on rate limit errors.
            rate_limit_wait: Initial wait time in seconds before retrying
                after a rate limit. Exponential backoff is applied.
            max_retries: Maximum number of retries on rate limit.
        """
        self.timeout = timeout
        self.retry_on_rate_limit = retry_on_rate_limit
        self.rate_limit_wait = rate_limit_wait
        self.max_retries = max_retries

    def run(
        self,
        cmd: list[str],
        *,
        cwd: str | None = None,
        _retry_attempt: int = 0,
        _retry_chain_id: str | None = None,
    ) -> ProcessResult:
        """Run a command as a subprocess and return the result.

        Args:
            cmd: Command list to execute.
            cwd: Working directory.
            _retry_attempt: Internal use — current retry count (starts at 0).
            _retry_chain_id: Internal use — unique ID linking retries in the same chain.

        Returns:
            ProcessResult with output, exit_code, success.
        """
        # 재시도 체인의 첫 시도인 경우 새로운 chain ID 생성
        if _retry_chain_id is None:
            _retry_chain_id = str(uuid.uuid4())[:8]

        log_msg = f"subprocess starting: {' '.join(cmd)} (cwd={cwd})"
        if _retry_attempt > 0:
            attempt_info = f"{_retry_attempt + 1}/{self.max_retries + 1}"
            log_msg += f" [retry_chain={_retry_chain_id}, attempt={attempt_info}]"
        else:
            log_msg += f" [retry_chain={_retry_chain_id}]"
        logger.info(log_msg)

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

            # Detect rate limit and retry
            # Exponential backoff strategy: 30s → 60s → 120s (up to 3 retries)
            should_retry = (
                self.retry_on_rate_limit
                and _retry_attempt < self.max_retries
                and _is_rate_limit(stderr)
            )
            if should_retry:
                return self._retry_after_rate_limit(
                    cmd, cwd, elapsed, _retry_attempt, _retry_chain_id
                )

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

            # Retry on rate limit even when a timeout occurs (rate limit detected in stderr)
            should_retry_timeout = (
                self.retry_on_rate_limit
                and _retry_attempt < self.max_retries
                and _is_rate_limit(stderr_text)
            )
            if should_retry_timeout:
                return self._retry_after_rate_limit(
                    cmd, cwd, elapsed, _retry_attempt, _retry_chain_id
                )

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
        """Log the execution result."""
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
        self,
        cmd: list[str],
        cwd: str | None,
        elapsed: float,
        attempt: int,
        retry_chain_id: str,
    ) -> ProcessResult:
        """Retry with exponential backoff after a rate limit error.

        Retry schedule:
        - Attempt 1: wait 30s
        - Attempt 2: wait 60s
        - Attempt 3: wait 120s
        """
        next_attempt = attempt + 1
        # Exponential backoff: base_wait * 2^attempt
        delay = self.rate_limit_wait * (2**attempt)

        logger.warning(
            "Rate limited (429). Retry %d/%d after %.0fs (elapsed: %.1fs) [retry_chain=%s]",
            next_attempt,
            self.max_retries,
            delay,
            elapsed,
            retry_chain_id,
        )
        time.sleep(delay)

        logger.info(
            "Resuming after rate limit backoff [retry_chain=%s, next_attempt=%d]",
            retry_chain_id,
            next_attempt + 1,
        )
        return self.run(cmd, cwd=cwd, _retry_attempt=next_attempt, _retry_chain_id=retry_chain_id)

    @staticmethod
    def _decode_stderr(stderr: bytes | str | None) -> str:
        """Decode stderr to a string."""
        if stderr is None:
            return ""
        if isinstance(stderr, bytes):
            return stderr.decode(errors="replace")
        return stderr
