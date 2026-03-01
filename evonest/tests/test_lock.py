"""Tests for core/lock.py — EvonestLock."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from evonest.core.lock import EvonestLock


def test_lock_creates_and_removes(tmp_path: Path) -> None:
    lock_path = tmp_path / "lock"
    with EvonestLock(lock_path):
        assert lock_path.exists()
        assert lock_path.read_text() == str(os.getpid())
    assert not lock_path.exists()


def test_lock_prevents_concurrent(tmp_path: Path) -> None:
    lock_path = tmp_path / "lock"
    with EvonestLock(lock_path):
        with pytest.raises(RuntimeError, match="Another evolution"):
            with EvonestLock(lock_path):
                pass


def test_lock_cleanup_on_exception(tmp_path: Path) -> None:
    lock_path = tmp_path / "lock"
    with pytest.raises(ValueError):
        with EvonestLock(lock_path):
            raise ValueError("test error")
    assert not lock_path.exists()


def test_lock_creates_parent_dirs(tmp_path: Path) -> None:
    lock_path = tmp_path / "subdir" / "lock"
    with EvonestLock(lock_path):
        assert lock_path.exists()
    assert not lock_path.exists()


def test_stale_lock_auto_cleanup(tmp_path: Path) -> None:
    """A lock file with a non-existent PID is automatically cleaned up."""
    lock_path = tmp_path / "lock"
    lock_path.write_text("999999", encoding="utf-8")

    with EvonestLock(lock_path):
        assert lock_path.exists()
        assert lock_path.read_text() == str(os.getpid())
    assert not lock_path.exists()


def test_invalid_lock_file_auto_cleanup(tmp_path: Path) -> None:
    """A lock file with an invalid format is automatically cleaned up."""
    lock_path = tmp_path / "lock"
    lock_path.write_text("not-a-number", encoding="utf-8")

    with EvonestLock(lock_path):
        assert lock_path.exists()
        assert lock_path.read_text() == str(os.getpid())
    assert not lock_path.exists()


def test_lock_prevents_concurrent_with_running_process(tmp_path: Path) -> None:
    """A lock file for a running process is preserved and raises an error."""
    lock_path = tmp_path / "lock"
    with EvonestLock(lock_path):
        with pytest.raises(RuntimeError, match=r"Another evolution.*PID:"):
            with EvonestLock(lock_path):
                pass
