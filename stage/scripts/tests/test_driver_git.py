from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
HOOKS_DIR = SCRIPTS_DIR.parent / "hooks"
for import_dir in (HOOKS_DIR, SCRIPTS_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_git import commit_item  # noqa: E402
from stage_work import WorkItem  # noqa: E402


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )


def initialize_git(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Stage Test")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")
    git(root, "checkout", "-q", "-b", "stage/driver/W-00000001-test")


def make_item(root: Path, scope: tuple[str, ...]) -> WorkItem:
    card_path = root / ".stage/work/current/W-00000001/_story.md"
    card_path.parent.mkdir(parents=True)
    card_path.write_text("---\nid: W-00000001\n---\n", encoding="utf-8")
    return WorkItem(
        path=card_path,
        item_id="W-00000001",
        title="Test item",
        status="active",
        verification="pending",
        retrospective="pending",
        promotion="pending",
        scope=scope,
        promotes=(),
    )


class CommitItemTest(unittest.TestCase):
    def test_missing_declared_path_is_omitted_while_remaining_output_is_committed(self):
        for missing_path in ("not-created.txt", "not-created/"):
            with self.subTest(missing_path=missing_path), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                item = make_item(root, ("output.txt", missing_path))
                (root / "output.txt").write_text("before\n", encoding="utf-8")
                initialize_git(root)
                base_head = git(root, "rev-parse", "HEAD").stdout.strip()
                (root / "output.txt").write_text("after\n", encoding="utf-8")

                committed, error, omitted_paths = commit_item(root, item, base_head)
                committed_paths = git(
                    root, "show", "--pretty=format:", "--name-only", "HEAD"
                ).stdout.splitlines()

                self.assertTrue(committed, error)
                self.assertEqual([missing_path], omitted_paths)
                self.assertEqual(["output.txt"], committed_paths)

    def test_deleted_tracked_directory_is_kept_so_its_deletion_is_committed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = make_item(root, ("doomed/",))
            doomed_file = root / "doomed/example.py"
            doomed_file.parent.mkdir()
            doomed_file.write_text("before\n", encoding="utf-8")
            initialize_git(root)
            base_head = git(root, "rev-parse", "HEAD").stdout.strip()
            doomed_file.unlink()
            doomed_file.parent.rmdir()

            committed, error, omitted_paths = commit_item(root, item, base_head)
            committed_changes = git(
                root, "show", "--pretty=format:", "--name-status", "HEAD"
            ).stdout.splitlines()

        self.assertTrue(committed, error)
        self.assertEqual([], omitted_paths)
        self.assertEqual(["D\tdoomed/example.py"], committed_changes)


if __name__ == "__main__":
    unittest.main()
