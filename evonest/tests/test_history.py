"""Tests for core/history.py."""

from __future__ import annotations

from pathlib import Path

from evonest.core.history import build_history_summary, get_recent_history
from evonest.core.state import ProjectState


def _save_cycle(
    state: ProjectState, num: int, success: bool, persona: str = "test", adversarial: str = "none"
) -> None:
    state.save_cycle_history(
        num,
        {
            "timestamp": f"2025-01-{num:02d}T00:00:00Z",
            "success": success,
            "mutation": {"persona": persona, "adversarial": adversarial},
            "duration_seconds": 30,
            "improvement_title": f"Improvement {num}",
            "commit_message": f"fix(test): cycle {num}" if success else "",
        },
    )


def test_build_history_summary_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert build_history_summary(state) == ""


def test_build_history_summary(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    _save_cycle(state, 1, True, "security-auditor")
    _save_cycle(state, 2, False, "chaos-engineer", "break-interfaces")
    _save_cycle(state, 3, True, "architect")

    summary = build_history_summary(state, count=5)
    assert "Recent Cycle History" in summary
    assert "SUCCESS" in summary
    assert "FAIL" in summary
    assert "security-auditor" in summary
    assert "break-interfaces" in summary


def test_build_history_summary_limits(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    for i in range(10):
        _save_cycle(state, i + 1, True)

    summary = build_history_summary(state, count=3)
    assert summary.count("SUCCESS") == 3


def test_get_recent_history_empty(tmp_project: Path) -> None:
    result = get_recent_history(tmp_project)
    assert "No cycle history" in result


def test_get_recent_history(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    _save_cycle(state, 1, True, "security-auditor")
    _save_cycle(state, 2, False, "chaos-engineer", "corrupt-state")

    result = get_recent_history(tmp_project, count=5)
    assert "2 of 2" in result
    assert "security-auditor" in result
    assert "corrupt-state" in result
    assert "SUCCESS" in result
    assert "FAIL" in result


def test_get_recent_history_limits(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    for i in range(20):
        _save_cycle(state, i + 1, True)

    result = get_recent_history(tmp_project, count=5)
    assert "5 of 20" in result
