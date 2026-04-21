"""Per-project git repo for session-bookmark tags.

The repo stays quiet (no automatic commits) until the user plants a tag.
Each tag is an annotated tag pointing at a commit that snapshots every
tracked file at that moment.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest

from plot_mcp.git_store import (
    TagAlreadyExistsError,
    delete_tag,
    ensure_repo,
    list_tags,
    tag_snapshot,
)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    d = tmp_path / "alpha"
    d.mkdir()
    (d / "core.json").write_text('{"canvas_id":"core"}', encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# ensure_repo
# ---------------------------------------------------------------------------


def test_ensure_repo_creates_dotgit(project_dir: Path) -> None:
    ensure_repo(project_dir)
    assert (project_dir / ".git").is_dir()


def test_ensure_repo_has_no_commits_yet(project_dir: Path) -> None:
    """Quiet-repo principle: until the user tags, git log is empty."""
    ensure_repo(project_dir)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    # HEAD resolution fails on a repo with zero commits.
    assert result.returncode != 0


def test_ensure_repo_is_idempotent(project_dir: Path) -> None:
    ensure_repo(project_dir)
    # Second call must not raise.
    ensure_repo(project_dir)
    assert (project_dir / ".git").is_dir()


def test_ensure_repo_configures_local_author(project_dir: Path) -> None:
    """Author identity doesn't depend on the user's global git config."""
    ensure_repo(project_dir)
    name = subprocess.run(
        ["git", "config", "--local", "user.name"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout.strip()
    email = subprocess.run(
        ["git", "config", "--local", "user.email"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert name == "Plot"
    assert email == "plot@noory-ai.local"


def test_ensure_repo_writes_gitignore(project_dir: Path) -> None:
    ensure_repo(project_dir)
    gi = (project_dir / ".gitignore").read_text(encoding="utf-8")
    assert "*.tmp" in gi


# ---------------------------------------------------------------------------
# tag_snapshot
# ---------------------------------------------------------------------------


def test_tag_snapshot_creates_commit_and_tag(project_dir: Path) -> None:
    ensure_repo(project_dir)
    result = tag_snapshot(project_dir, "session-start")
    assert result["name"] == "session-start"
    assert isinstance(result["sha"], str) and len(result["sha"]) == 40
    # HEAD now resolves.
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head == result["sha"]
    # Tag resolves to the same sha.
    tag = subprocess.run(
        ["git", "rev-list", "-n", "1", "session-start"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert tag == result["sha"]


def test_tag_snapshot_uses_message_when_given(project_dir: Path) -> None:
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "milestone-1", message="before BANAS refactor")
    msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert msg == "before BANAS refactor"


def test_tag_snapshot_duplicate_name_rejected(project_dir: Path) -> None:
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "dup")
    with pytest.raises(TagAlreadyExistsError):
        tag_snapshot(project_dir, "dup")


def test_tag_snapshot_captures_latest_file_state(project_dir: Path) -> None:
    """Each snapshot must reflect the on-disk state at tag time."""
    ensure_repo(project_dir)
    (project_dir / "core.json").write_text('{"canvas_id":"core","v":1}', encoding="utf-8")
    tag_snapshot(project_dir, "v1")
    (project_dir / "core.json").write_text('{"canvas_id":"core","v":2}', encoding="utf-8")
    tag_snapshot(project_dir, "v2")
    # Reading the v1 tag's tree should show v=1.
    blob = subprocess.run(
        ["git", "show", "v1:core.json"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout
    assert '"v":1' in blob


def test_tag_snapshot_with_no_changes_still_tags(project_dir: Path) -> None:
    """Back-to-back tags on an unchanged tree still produce a second tag
    (pointing at a no-op commit). Needed for "end-of-session" markers."""
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "a")
    tag_snapshot(project_dir, "b")
    tags = {t["name"] for t in list_tags(project_dir)}
    assert {"a", "b"} <= tags


# ---------------------------------------------------------------------------
# list_tags / delete_tag
# ---------------------------------------------------------------------------


def test_list_tags_empty_on_fresh_repo(project_dir: Path) -> None:
    ensure_repo(project_dir)
    assert list_tags(project_dir) == []


def test_list_tags_newest_first(project_dir: Path) -> None:
    """Sort precision is 1s (git's own resolution); the test spaces
    the two tags by just over a second so the ordering is well-defined."""
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "first")
    time.sleep(1.1)
    tag_snapshot(project_dir, "second")
    tags = list_tags(project_dir)
    assert [t["name"] for t in tags] == ["second", "first"]


def test_list_tags_returns_sha_and_message(project_dir: Path) -> None:
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "m1", message="first milestone")
    (tag,) = list_tags(project_dir)
    assert tag["name"] == "m1"
    assert isinstance(tag["sha"], str) and len(tag["sha"]) == 40
    assert tag["message"] == "first milestone"
    assert tag["ts"]  # ISO timestamp, non-empty


def test_delete_tag_removes_tag_only(project_dir: Path) -> None:
    ensure_repo(project_dir)
    tag_snapshot(project_dir, "doomed")
    delete_tag(project_dir, "doomed")
    assert list_tags(project_dir) == []
    # But the commit it pointed at is still reachable via reflog.
    reflog = subprocess.run(
        ["git", "reflog", "--all"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    ).stdout
    assert reflog  # non-empty


def test_delete_unknown_tag_raises(project_dir: Path) -> None:
    ensure_repo(project_dir)
    with pytest.raises(KeyError):
        delete_tag(project_dir, "never-existed")
