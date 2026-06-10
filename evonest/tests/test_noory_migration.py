"""R9 — evonest artifacts live under `<project>/.noory/evonest/`."""

from __future__ import annotations

from pathlib import Path

from evonest.core.data_root import evonest_data_root, has_data_root
from evonest.core.initializer import init_project
from evonest.core.state import ProjectState


def test_data_root_lives_under_noory(tmp_path: Path) -> None:
    root = evonest_data_root(tmp_path, create=True)
    assert root == tmp_path / ".noory" / "evonest"
    assert root.is_dir()


def test_read_path_is_side_effect_free(tmp_path: Path) -> None:
    root = evonest_data_root(tmp_path)
    assert root == tmp_path / ".noory" / "evonest"
    assert not root.exists()


def test_legacy_dot_evonest_migrates_on_first_access(tmp_path: Path) -> None:
    legacy = tmp_path / ".evonest"
    (legacy / "logs").mkdir(parents=True)
    (legacy / "config.json").write_text("{}", encoding="utf-8")

    root = evonest_data_root(tmp_path)

    assert (root / "config.json").is_file()
    assert (root / "logs").is_dir()
    assert not legacy.exists(), "legacy must be moved, not copied"


def test_legacy_migration_never_clobbers_existing_noory(tmp_path: Path) -> None:
    (tmp_path / ".evonest").mkdir()
    (tmp_path / ".noory" / "evonest").mkdir(parents=True)

    root = evonest_data_root(tmp_path)

    assert root == tmp_path / ".noory" / "evonest"
    assert (tmp_path / ".evonest").is_dir(), "must not destroy legacy data"


def test_initialize_creates_the_noory_layout_and_scoped_gitignore(tmp_path: Path) -> None:
    init_project(str(tmp_path))
    assert (tmp_path / ".noory" / "evonest" / "config.json").is_file()
    # The gitignore entry is SCOPED to our subtree — `.noory/` is shared with
    # plugins whose artifacts are source-of-truth (e.g. plot canvases).
    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert ".noory/evonest/" in gitignore
    assert "\n.noory/\n" not in gitignore


def test_state_reads_the_migrated_root(tmp_path: Path) -> None:
    init_project(str(tmp_path))
    state = ProjectState(tmp_path)
    assert state.paths.root == tmp_path / ".noory" / "evonest"


def test_has_data_root_sees_both_layouts(tmp_path: Path) -> None:
    assert not has_data_root(tmp_path)
    (tmp_path / ".evonest").mkdir()
    assert has_data_root(tmp_path), "legacy layout must be discoverable"


def test_migration_carries_the_gitignore_intent(tmp_path: Path) -> None:
    """A project that ignored `.evonest/` must keep ignoring the data after
    the move — otherwise the next blanket `git add` silently tracks runtime
    data (this exact accident happened to evonest's own dogfood data)."""
    (tmp_path / ".evonest").mkdir()
    (tmp_path / ".gitignore").write_text("# data\n.evonest/\n", encoding="utf-8")

    evonest_data_root(tmp_path)

    content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert ".noory/evonest/" in content


def test_migration_leaves_gitignore_alone_when_user_never_ignored(tmp_path: Path) -> None:
    """No `.gitignore`, or one without the legacy entry → do not invent
    ignore policy for the user."""
    (tmp_path / ".evonest").mkdir()
    evonest_data_root(tmp_path)
    assert not (tmp_path / ".gitignore").exists()
