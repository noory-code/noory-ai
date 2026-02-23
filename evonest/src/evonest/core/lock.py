"""Lock file context manager for concurrent execution prevention."""

from __future__ import annotations

import os
from pathlib import Path
from types import TracebackType


class EvonestLock:
    """File-based lock to prevent concurrent evolution runs on the same project."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path

    def __enter__(self) -> EvonestLock:
        if self.lock_path.exists():
            self._check_and_clean_stale_lock()
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path.write_text(str(os.getpid()), encoding="utf-8")
        return self

    def _check_and_clean_stale_lock(self) -> None:
        """stale lock 파일 확인 후 자동 정리."""
        try:
            pid_str = self.lock_path.read_text(encoding="utf-8").strip()
            pid = int(pid_str)
        except (ValueError, OSError):
            self.lock_path.unlink(missing_ok=True)
            return

        if not self._is_process_running(pid):
            self.lock_path.unlink(missing_ok=True)
        else:
            raise RuntimeError(
                f"Another evolution is running (lock file: {self.lock_path}, PID: {pid})"
            )

    def _is_process_running(self, pid: int) -> bool:
        """프로세스가 실행 중인지 확인."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.lock_path.unlink(missing_ok=True)
