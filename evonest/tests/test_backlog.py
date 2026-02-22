"""Tests for core/backlog.py."""

from __future__ import annotations

from pathlib import Path

from evonest.core.backlog import (
    build_context,
    manage_backlog,
    prune,
    save_observations,
    update_status,
)
from evonest.core.state import ProjectState


def test_save_observations(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    improvements = [
        {"title": "Add tests for parser", "category": "test-coverage", "priority": "high"},
        {"title": "Fix error handling", "category": "reliability"},
    ]
    added = save_observations(state, improvements, "security-auditor", 1)
    assert added == 2

    backlog = state.read_backlog()
    assert len(backlog["items"]) == 2
    assert backlog["items"][0]["title"] == "Add tests for parser"
    assert backlog["items"][0]["status"] == "pending"
    assert backlog["items"][0]["attempts"] == 0


def test_save_observations_dedup(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    improvements = [{"title": "Fix bug"}]
    save_observations(state, improvements, "test", 1)
    added = save_observations(state, improvements, "test", 2)
    assert added == 0

    backlog = state.read_backlog()
    assert len(backlog["items"]) == 1


def test_save_observations_files_as_string(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    improvements = [{"title": "Fix", "files": "src/a.py, src/b.py"}]
    save_observations(state, improvements, "test", 1)

    backlog = state.read_backlog()
    assert backlog["items"][0]["files"] == ["src/a.py", "src/b.py"]


def test_update_status_completed(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Task"}], "test", 1)
    item_id = state.read_backlog()["items"][0]["id"]

    update_status(state, item_id, "completed")
    assert state.read_backlog()["items"][0]["status"] == "completed"


def test_update_status_failed_increments_attempts(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Task"}], "test", 1)
    item_id = state.read_backlog()["items"][0]["id"]

    update_status(state, item_id, "pending")
    assert state.read_backlog()["items"][0]["attempts"] == 1

    update_status(state, item_id, "pending")
    assert state.read_backlog()["items"][0]["attempts"] == 2


def test_update_status_stale_after_max_attempts(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Task"}], "test", 1)
    item_id = state.read_backlog()["items"][0]["id"]

    for _ in range(3):
        update_status(state, item_id, "pending")

    assert state.read_backlog()["items"][0]["status"] == "stale"


def test_prune_removes_old_completed(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Old task"}], "test", 1)
    item_id = state.read_backlog()["items"][0]["id"]
    update_status(state, item_id, "completed")

    removed = prune(state, current_cycle=25)
    assert removed == 1
    assert len(state.read_backlog()["items"]) == 0


def test_prune_keeps_recent(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Recent task"}], "test", 10)
    item_id = state.read_backlog()["items"][0]["id"]
    update_status(state, item_id, "completed")

    removed = prune(state, current_cycle=25)
    assert removed == 0  # source_cycle=10 > cutoff=5


def test_prune_keeps_pending(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(state, [{"title": "Pending task"}], "test", 1)

    removed = prune(state, current_cycle=100)
    assert removed == 0


def test_build_context_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert build_context(state) == ""


def test_build_context_with_items(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    save_observations(
        state,
        [
            {"title": "High priority", "priority": "high", "category": "security"},
            {"title": "Low priority", "priority": "low", "category": "style"},
        ],
        "test",
        1,
    )

    context = build_context(state)
    assert "Accumulated Backlog" in context
    assert "High priority" in context
    # High priority should come first
    assert context.index("High priority") < context.index("Low priority")


def test_manage_backlog_list(tmp_project: Path) -> None:
    result = manage_backlog(tmp_project, "list")
    assert "empty" in result.lower()


def test_manage_backlog_add(tmp_project: Path) -> None:
    result = manage_backlog(tmp_project, "add", {"title": "New item", "priority": "high"})
    assert "Added 1" in result

    result = manage_backlog(tmp_project, "list")
    assert "New item" in result


def test_manage_backlog_remove(tmp_project: Path) -> None:
    manage_backlog(tmp_project, "add", {"title": "To remove"})
    state = ProjectState(tmp_project)
    item_id = state.read_backlog()["items"][0]["id"]

    result = manage_backlog(tmp_project, "remove", {"id": item_id})
    assert "Removed" in result
    assert len(state.read_backlog()["items"]) == 0


def test_manage_backlog_prune(tmp_project: Path) -> None:
    result = manage_backlog(tmp_project, "prune")
    assert "Pruned" in result
