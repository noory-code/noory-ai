"""Tests for EvonestPaths."""

from pathlib import Path

import pytest

from evonest.core.paths import EvonestPaths


@pytest.fixture
def paths(tmp_path: Path) -> EvonestPaths:
    project = tmp_path / "myproject"
    project.mkdir()
    root = project / ".evonest"
    root.mkdir()
    return EvonestPaths(project, root)


def test_project_and_root(paths: EvonestPaths, tmp_path: Path) -> None:
    assert paths.project == tmp_path / "myproject"
    assert paths.root == tmp_path / "myproject" / ".evonest"


def test_config_path(paths: EvonestPaths) -> None:
    assert paths.config_path == paths.root / "config.json"


def test_identity_path(paths: EvonestPaths) -> None:
    assert paths.identity_path == paths.root / "identity.md"


def test_progress_path(paths: EvonestPaths) -> None:
    assert paths.progress_path == paths.root / "progress.json"


def test_backlog_path(paths: EvonestPaths) -> None:
    assert paths.backlog_path == paths.root / "backlog.json"


def test_lock_path(paths: EvonestPaths) -> None:
    assert paths.lock_path == paths.root / "lock"


def test_log_path(paths: EvonestPaths) -> None:
    assert paths.log_path == paths.root / "logs" / "orchestrator.log"


def test_history_dir(paths: EvonestPaths) -> None:
    assert paths.history_dir == paths.root / "history"


def test_stimuli_dir(paths: EvonestPaths) -> None:
    assert paths.stimuli_dir == paths.root / "stimuli"


def test_processed_stimuli_dir(paths: EvonestPaths) -> None:
    assert paths.processed_stimuli_dir == paths.root / "stimuli" / ".processed"


def test_decisions_dir(paths: EvonestPaths) -> None:
    assert paths.decisions_dir == paths.root / "decisions"


def test_dynamic_personas_path(paths: EvonestPaths) -> None:
    assert paths.dynamic_personas_path == paths.root / "dynamic-personas.json"


def test_dynamic_adversarials_path(paths: EvonestPaths) -> None:
    assert paths.dynamic_adversarials_path == paths.root / "dynamic-adversarials.json"


def test_advice_path(paths: EvonestPaths) -> None:
    assert paths.advice_path == paths.root / "advice.json"


def test_environment_path(paths: EvonestPaths) -> None:
    assert paths.environment_path == paths.root / "environment.json"


def test_proposals_dir(paths: EvonestPaths) -> None:
    assert paths.proposals_dir == paths.root / "proposals"


def test_proposals_done_dir(paths: EvonestPaths) -> None:
    assert paths.proposals_done_dir == paths.root / "proposals" / "done"


def test_scout_path(paths: EvonestPaths) -> None:
    assert paths.scout_path == paths.root / "scout.json"


def test_pending_path(paths: EvonestPaths) -> None:
    assert paths.pending_path == paths.root / "pending.json"


def test_observe_path(paths: EvonestPaths) -> None:
    assert paths.observe_path == paths.root / "observe.md"


def test_plan_path(paths: EvonestPaths) -> None:
    assert paths.plan_path == paths.root / "plan.md"


def test_execute_path(paths: EvonestPaths) -> None:
    assert paths.execute_path == paths.root / "execute.md"


def test_meta_observe_path(paths: EvonestPaths) -> None:
    assert paths.meta_observe_path == paths.root / "meta-observe.md"


def test_all_paths_under_root(paths: EvonestPaths) -> None:
    """All file paths must be descendants of root."""
    file_paths = [
        paths.config_path,
        paths.identity_path,
        paths.progress_path,
        paths.backlog_path,
        paths.lock_path,
        paths.log_path,
        paths.dynamic_personas_path,
        paths.dynamic_adversarials_path,
        paths.advice_path,
        paths.environment_path,
        paths.scout_path,
        paths.pending_path,
        paths.observe_path,
        paths.plan_path,
        paths.execute_path,
        paths.meta_observe_path,
    ]
    dir_paths = [
        paths.history_dir,
        paths.stimuli_dir,
        paths.processed_stimuli_dir,
        paths.decisions_dir,
        paths.proposals_dir,
        paths.proposals_done_dir,
    ]
    for p in file_paths + dir_paths:
        assert paths.root in p.parents or p.parent == paths.root, f"{p} not under root"
