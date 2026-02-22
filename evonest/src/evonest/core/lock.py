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
            raise RuntimeError(
                f"Another evolution is running (lock file: {self.lock_path}). "
                "If this is stale, delete it manually."
            )
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path.write_text(str(os.getpid()), encoding="utf-8")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.lock_path.unlink(missing_ok=True)
