"""Tests for core/state.py — ProjectState."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evonest.core.state import ProjectState


def test_init_valid_project(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.project == tmp_project.resolve()
    assert state.root == tmp_project / ".evonest"


def test_init_missing_dir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        ProjectState(tmp_path / "nonexistent")


def test_init_not_initialized(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not initialized"):
        ProjectState(tmp_path)


def test_path_properties(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.config_path == tmp_project / ".evonest" / "config.json"
    assert state.identity_path == tmp_project / ".evonest" / "identity.md"
    assert state.progress_path == tmp_project / ".evonest" / "progress.json"
    assert state.backlog_path == tmp_project / ".evonest" / "backlog.json"
    assert state.lock_path == tmp_project / ".evonest" / "lock"
    assert state.history_dir == tmp_project / ".evonest" / "history"
    assert state.stimuli_dir == tmp_project / ".evonest" / "stimuli"
    assert state.decisions_dir == tmp_project / ".evonest" / "decisions"
    assert state.advice_path == tmp_project / ".evonest" / "advice.json"
    assert state.environment_path == tmp_project / ".evonest" / "environment.json"
    assert state.proposals_dir == tmp_project / ".evonest" / "proposals"


def test_read_write_json(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    data = {"key": "value", "num": 42}
    path = state.root / "test.json"
    state.write_json(path, data)
    assert state.read_json(path) == data


def test_read_json_missing(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.read_json(state.root / "nope.json") == {}


def test_read_json_corrupt(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    path = state.root / "corrupt.json"
    path.write_text("{ not valid json !!!", encoding="utf-8")
    assert state.read_json(path) == {}


def test_read_progress_corrupt(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.progress_path.write_text("{ not valid json !!!", encoding="utf-8")
    assert state.read_progress() == {}


def test_read_backlog_corrupt(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.backlog_path.write_text("{ not valid json !!!", encoding="utf-8")
    assert state.read_backlog() == {}


def test_read_write_text(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    path = state.root / "test.txt"
    state.write_text(path, "hello world")
    assert state.read_text(path) == "hello world"


def test_read_text_missing(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.read_text(state.root / "nope.txt") == ""


def test_identity(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_identity("# My Project")
    assert state.read_identity() == "# My Project"


def test_progress(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = state.read_progress()
    assert progress["total_cycles"] == 0

    progress["total_cycles"] = 5
    state.write_progress(progress)
    assert state.read_progress()["total_cycles"] == 5


def test_backlog(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    backlog = state.read_backlog()
    assert backlog["version"] == 2
    assert backlog["items"] == []


def test_dynamic_mutations(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.read_dynamic_personas() == []
    assert state.read_dynamic_adversarials() == []

    personas = [{"id": "test", "name": "Test"}]
    state.write_dynamic_personas(personas)
    assert state.read_dynamic_personas() == personas


def test_advice(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.read_advice() == {}

    advice = {
        "generated_cycle": 10,
        "strategic_direction": "Focus on tests",
        "recommended_focus": "test coverage",
    }
    state.write_advice(advice)
    assert state.read_advice() == advice


def test_environment(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.read_environment() == {}

    env = {
        "last_scan_cycle": 5,
        "items": [{"id": "eco-001", "title": "Update TypeScript"}],
    }
    state.write_environment(env)
    assert state.read_environment() == env


def test_stimuli(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    path = state.add_stimulus("Focus on tests")
    assert Path(path).exists()
    assert "stimulus-" in path

    stimuli = state.consume_stimuli()
    assert len(stimuli) == 1
    assert stimuli[0] == "Focus on tests"
    assert not Path(path).exists()  # moved to .processed/


def test_decisions(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    path = state.add_decision("Prioritize auth module")
    assert Path(path).exists()

    decisions = state.consume_decisions()
    assert len(decisions) == 1
    assert decisions[0] == "Prioritize auth module"
    assert not Path(path).exists()  # deleted


def test_history(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    data = {"success": True, "persona": "test"}
    path = state.save_cycle_history(1, data)
    assert path.name == "cycle-0001.json"
    assert json.loads(path.read_text())["success"] is True

    files = state.list_history_files()
    assert len(files) == 1


def test_log(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.log("test message")
    content = state.log_path.read_text()
    assert "test message" in content


def test_summary(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    summary = state.summary()
    assert "Cycles: 0" in summary
    assert "Running: no" in summary


def test_ensure_dirs(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.ensure_dirs()
    assert state.history_dir.is_dir()
    assert state.stimuli_dir.is_dir()
    assert state.decisions_dir.is_dir()
    assert state.proposals_dir.is_dir()


def test_add_proposal_creates_file(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    content = "# Proposal: Refactor domain model"
    path_str = state.add_proposal(content)
    path = state.proposals_dir / path_str.split("/")[-1]
    assert path.exists()
    assert path.read_text() == content


def test_add_proposal_filename_pattern(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    path_str = state.add_proposal("test")
    fname = path_str.split("/")[-1]
    assert fname.startswith("proposal-")
    assert fname.endswith(".md")


def test_list_proposals_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert state.list_proposals() == []


def test_list_proposals_returns_files(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.add_proposal("Proposal A")
    state.add_proposal("Proposal B")
    proposals = state.list_proposals()
    assert len(proposals) == 2
    assert all(p.suffix == ".md" for p in proposals)
