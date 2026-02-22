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
