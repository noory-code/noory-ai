"""Tests for domain repositories."""

from pathlib import Path

import pytest

from evonest.core.paths import EvonestPaths
from evonest.core.repositories import (
    AdviceRepository,
    BacklogRepository,
    DecisionRepository,
    EnvironmentRepository,
    HistoryRepository,
    IdentityRepository,
    MutationsRepository,
    PendingRepository,
    ProgressRepository,
    ProposalRepository,
    ScoutRepository,
    StimulusRepository,
)


@pytest.fixture
def paths(tmp_path: Path) -> EvonestPaths:
    project = tmp_path / "proj"
    project.mkdir()
    root = project / ".evonest"
    root.mkdir()
    return EvonestPaths(project, root)


# ---------------------------------------------------------------------------
# IdentityRepository
# ---------------------------------------------------------------------------


def test_identity_read_missing(paths: EvonestPaths) -> None:
    repo = IdentityRepository(paths)
    assert repo.read() == ""


def test_identity_write_read(paths: EvonestPaths) -> None:
    repo = IdentityRepository(paths)
    repo.write("hello identity")
    assert repo.read() == "hello identity"


def test_identity_write_creates_parent(paths: EvonestPaths) -> None:
    repo = IdentityRepository(paths)
    repo.write("content")
    assert paths.identity_path.exists()


# ---------------------------------------------------------------------------
# ProgressRepository
# ---------------------------------------------------------------------------


def test_progress_read_missing(paths: EvonestPaths) -> None:
    repo = ProgressRepository(paths)
    assert repo.read() == {}


def test_progress_write_read(paths: EvonestPaths) -> None:
    repo = ProgressRepository(paths)
    repo.write({"total_cycles": 5})
    assert repo.read() == {"total_cycles": 5}


def test_progress_read_corrupt(paths: EvonestPaths) -> None:
    paths.progress_path.write_text("not json", encoding="utf-8")
    repo = ProgressRepository(paths)
    assert repo.read() == {}


# ---------------------------------------------------------------------------
# BacklogRepository
# ---------------------------------------------------------------------------


def test_backlog_read_missing(paths: EvonestPaths) -> None:
    repo = BacklogRepository(paths)
    result = repo.read()
    assert result == {"version": 2, "items": []}


def test_backlog_write_read(paths: EvonestPaths) -> None:
    repo = BacklogRepository(paths)
    data = {"version": 2, "items": [{"id": "1", "title": "test"}]}
    repo.write(data)
    assert repo.read() == data


# ---------------------------------------------------------------------------
# MutationsRepository
# ---------------------------------------------------------------------------


def test_mutations_personas_missing(paths: EvonestPaths) -> None:
    repo = MutationsRepository(paths)
    assert repo.read_personas() == []


def test_mutations_personas_write_read(paths: EvonestPaths) -> None:
    repo = MutationsRepository(paths)
    repo.write_personas([{"id": "p1"}])
    assert repo.read_personas() == [{"id": "p1"}]


def test_mutations_adversarials_missing(paths: EvonestPaths) -> None:
    repo = MutationsRepository(paths)
    assert repo.read_adversarials() == []


def test_mutations_adversarials_write_read(paths: EvonestPaths) -> None:
    repo = MutationsRepository(paths)
    repo.write_adversarials([{"id": "a1"}])
    assert repo.read_adversarials() == [{"id": "a1"}]


# ---------------------------------------------------------------------------
# AdviceRepository
# ---------------------------------------------------------------------------


def test_advice_read_missing(paths: EvonestPaths) -> None:
    assert AdviceRepository(paths).read() == {}


def test_advice_write_read(paths: EvonestPaths) -> None:
    repo = AdviceRepository(paths)
    repo.write({"key": "value"})
    assert repo.read() == {"key": "value"}


# ---------------------------------------------------------------------------
# EnvironmentRepository
# ---------------------------------------------------------------------------


def test_environment_read_missing(paths: EvonestPaths) -> None:
    assert EnvironmentRepository(paths).read() == {}


def test_environment_write_read(paths: EvonestPaths) -> None:
    repo = EnvironmentRepository(paths)
    repo.write({"lang": "python"})
    assert repo.read() == {"lang": "python"}


# ---------------------------------------------------------------------------
# ScoutRepository
# ---------------------------------------------------------------------------


def test_scout_read_missing(paths: EvonestPaths) -> None:
    assert ScoutRepository(paths).read() == {}


def test_scout_write_read(paths: EvonestPaths) -> None:
    repo = ScoutRepository(paths)
    repo.write({"results": []})
    assert repo.read() == {"results": []}


# ---------------------------------------------------------------------------
# PendingRepository
# ---------------------------------------------------------------------------


def test_pending_read_missing(paths: EvonestPaths) -> None:
    assert PendingRepository(paths).read() == {}


def test_pending_write_read(paths: EvonestPaths) -> None:
    repo = PendingRepository(paths)
    repo.write({"paused": True})
    assert repo.read() == {"paused": True}


def test_pending_clear(paths: EvonestPaths) -> None:
    repo = PendingRepository(paths)
    repo.write({"paused": True})
    repo.clear()
    assert not paths.pending_path.exists()


def test_pending_clear_noop(paths: EvonestPaths) -> None:
    repo = PendingRepository(paths)
    repo.clear()  # no error if file doesn't exist


# ---------------------------------------------------------------------------
# ProposalRepository
# ---------------------------------------------------------------------------


@pytest.fixture
def proposal_repo(paths: EvonestPaths) -> ProposalRepository:
    progress = ProgressRepository(paths)
    progress.write({"total_cycles": 3})
    return ProposalRepository(paths, progress)


def test_proposal_list_empty(paths: EvonestPaths, proposal_repo: ProposalRepository) -> None:
    assert proposal_repo.list() == []


def test_proposal_add_creates_file(paths: EvonestPaths, proposal_repo: ProposalRepository) -> None:
    path_str = proposal_repo.add("# Proposal content")
    path = Path(path_str)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# Proposal content"


def test_proposal_add_filename_pattern(
    paths: EvonestPaths, proposal_repo: ProposalRepository
) -> None:
    # No title: falls back to proposal-{HHMMSS}.md
    path_str = proposal_repo.add("content")
    name = Path(path_str).name
    assert name.startswith("proposal-")
    assert name.endswith(".md")


def test_proposal_add_filename_with_title_and_persona(
    paths: EvonestPaths, proposal_repo: ProposalRepository
) -> None:
    # With title + persona: {persona}-{title-slug}-{HHMMSS}.md
    path_str = proposal_repo.add(
        "content", title="Shell Injection Risk", persona_id="security-auditor"
    )
    name = Path(path_str).name
    assert name.startswith("security-auditor-shell-injection-risk-")
    assert name.endswith(".md")


def test_proposal_add_filename_with_title_only(
    paths: EvonestPaths, proposal_repo: ProposalRepository
) -> None:
    path_str = proposal_repo.add("content", title="My Improvement")
    name = Path(path_str).name
    assert name.startswith("my-improvement-")
    assert name.endswith(".md")


def test_proposal_list_returns_sorted(
    paths: EvonestPaths, proposal_repo: ProposalRepository
) -> None:
    proposal_repo.add("first")
    proposal_repo.add("second")
    proposal_repo.add("third")
    files = proposal_repo.list()
    assert len(files) == 3
    assert files == sorted(files)


def test_proposal_mark_done(paths: EvonestPaths, proposal_repo: ProposalRepository) -> None:
    path_str = proposal_repo.add("content")
    filename = Path(path_str).name
    dest = proposal_repo.mark_done(filename)
    assert dest.exists()
    assert not Path(path_str).exists()
    assert dest.parent == paths.proposals_done_dir


def test_proposal_mark_done_not_found(
    paths: EvonestPaths, proposal_repo: ProposalRepository
) -> None:
    with pytest.raises(FileNotFoundError):
        proposal_repo.mark_done("nonexistent.md")


# ---------------------------------------------------------------------------
# StimulusRepository
# ---------------------------------------------------------------------------


def test_stimulus_add(paths: EvonestPaths) -> None:
    repo = StimulusRepository(paths)
    path_str = repo.add("stimulus content")
    path = Path(path_str)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "stimulus content"


def test_stimulus_consume_empty(paths: EvonestPaths) -> None:
    repo = StimulusRepository(paths)
    assert repo.consume() == []


def test_stimulus_consume_moves_files(paths: EvonestPaths) -> None:
    repo = StimulusRepository(paths)
    repo.add("first")
    repo.add("second")
    results = repo.consume()
    assert len(results) == 2
    assert set(results) == {"first", "second"}
    # Files moved to .processed
    processed = list(paths.processed_stimuli_dir.glob("*.md"))
    assert len(processed) == 2
    # No files remaining in stimuli_dir
    remaining = list(paths.stimuli_dir.glob("*.md"))
    assert remaining == []


# ---------------------------------------------------------------------------
# DecisionRepository
# ---------------------------------------------------------------------------


def test_decision_add(paths: EvonestPaths) -> None:
    repo = DecisionRepository(paths)
    path_str = repo.add("decision content")
    path = Path(path_str)
    assert path.exists()


def test_decision_consume_empty(paths: EvonestPaths) -> None:
    repo = DecisionRepository(paths)
    assert repo.consume() == []


def test_decision_consume_deletes_files(paths: EvonestPaths) -> None:
    repo = DecisionRepository(paths)
    repo.add("decide A")
    repo.add("decide B")
    results = repo.consume()
    assert len(results) == 2
    assert set(results) == {"decide A", "decide B"}
    # Files deleted
    remaining = list(paths.decisions_dir.glob("*.md"))
    assert remaining == []


# ---------------------------------------------------------------------------
# HistoryRepository
# ---------------------------------------------------------------------------


def test_history_list_empty(paths: EvonestPaths) -> None:
    repo = HistoryRepository(paths)
    assert repo.list_files() == []


def test_history_save_cycle(paths: EvonestPaths) -> None:
    repo = HistoryRepository(paths)
    saved = repo.save_cycle(1, {"result": "ok"})
    assert saved.exists()
    assert saved.name == "cycle-0001.json"


def test_history_list_sorted(paths: EvonestPaths) -> None:
    repo = HistoryRepository(paths)
    repo.save_cycle(3, {})
    repo.save_cycle(1, {})
    repo.save_cycle(2, {})
    files = repo.list_files()
    names = [f.name for f in files]
    assert names == ["cycle-0001.json", "cycle-0002.json", "cycle-0003.json"]
