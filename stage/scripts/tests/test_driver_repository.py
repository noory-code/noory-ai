from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
HOOKS_DIR = SCRIPTS_DIR.parent / "hooks"
for import_dir in (HOOKS_DIR, SCRIPTS_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

import driver_git  # noqa: E402
import driver_repository  # noqa: E402

from git_test_config import isolate_git_config  # noqa: E402

isolate_git_config()


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


def seeded_repository(root: Path) -> None:
    (root / "tracked.txt").write_text("before\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")


class CountingRun:
    """Count subprocess launches while still running them."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self._run = subprocess.run

    def __call__(self, args, *rest, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(list(args))
        return self._run(args, *rest, **kwargs)


class RepositoryPathSnapshotTest(unittest.TestCase):
    def test_snapshot_matches_index_metadata_and_marks_untracked_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            (root / "tracked.txt").write_text("after\n", encoding="utf-8")
            (root / "new.txt").write_text("new\n", encoding="utf-8")
            runtime = root / ".stage/.runtime/state.json"
            runtime.parent.mkdir(parents=True)
            runtime.write_text("{}\n", encoding="utf-8")
            stage_line = git(root, "ls-files", "--stage", "--", "tracked.txt").stdout
            expected_metadata = stage_line.partition("\t")[0]

            snapshot = driver_repository.repository_path_snapshot(root)

        self.assertEqual(["new.txt", "tracked.txt"], sorted(snapshot))
        self.assertTrue(snapshot["new.txt"].startswith("untracked\0file\0"))
        self.assertTrue(snapshot["tracked.txt"].startswith(expected_metadata + "\0file\0"))

    @unittest.skipIf(sys.platform == "win32", "Windows file names cannot hold a tab")
    def test_untracked_name_with_a_tab_is_not_read_as_index_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            (root / "odd\tname.txt").write_text("new\n", encoding="utf-8")

            snapshot = driver_repository.repository_path_snapshot(root)

        self.assertTrue(snapshot["odd\tname.txt"].startswith("untracked\0"))

    def test_snapshot_of_a_worktree_starts_one_git_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            counting = CountingRun()
            with mock.patch.object(driver_repository.subprocess, "run", counting):
                driver_repository.repository_path_snapshot(root)

        self.assertEqual(1, len(counting.calls), counting.calls)

    def test_snapshot_outside_git_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            "os.environ", {"GIT_CEILING_DIRECTORIES": tmp}
        ):
            root = Path(tmp) / "plain"
            root.mkdir()
            self.assertEqual({}, driver_repository.repository_path_snapshot(root))

    def test_failed_listing_inside_a_worktree_raises_its_error(self):
        failed_listing = subprocess.CompletedProcess(
            args=["git", "ls-files"], returncode=128, stdout=b"", stderr=b"injected"
        )
        index_path = subprocess.CompletedProcess(
            args=["git", "rev-parse"], returncode=0, stdout=".git/index\n", stderr=""
        )
        with mock.patch.object(
            driver_repository.subprocess,
            "run",
            side_effect=[failed_listing, index_path],
        ), self.assertRaisesRegex(RuntimeError, "injected"):
            driver_repository.repository_path_snapshot(Path.cwd())


class GitDiffProcessCountTest(unittest.TestCase):
    def test_diff_of_a_worktree_with_head_starts_two_git_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            counting = CountingRun()
            with mock.patch.object(driver_repository.subprocess, "run", counting):
                driver_repository.git_diff(root)

        self.assertEqual(
            [["git", "diff"], ["git", "ls-files"]],
            [call[:2] for call in counting.calls],
        )

    def test_diff_outside_git_reports_no_worktree(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            "os.environ", {"GIT_CEILING_DIRECTORIES": tmp}
        ):
            root = Path(tmp) / "plain"
            root.mkdir()
            self.assertEqual("\0NO-GIT-WORKTREE\0", driver_repository.git_diff(root))


class RepositoryObservationTest(unittest.TestCase):
    def assert_matches_separate_reads(self, root: Path) -> None:
        self.assertEqual(
            (
                driver_repository.repository_fingerprint(root),
                driver_repository.repository_path_snapshot(root),
            ),
            driver_repository.repository_observation(root),
        )

    def test_observation_matches_fingerprint_and_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            "os.environ", {"GIT_CEILING_DIRECTORIES": tmp}
        ):
            committed = Path(tmp) / "committed"
            committed.mkdir()
            seeded_repository(committed)
            (committed / "tracked.txt").write_text("after\n", encoding="utf-8")
            (committed / "new.txt").write_text("new\n", encoding="utf-8")
            unborn = Path(tmp) / "unborn"
            unborn.mkdir()
            git(unborn, "init", "-q")
            (unborn / "staged.txt").write_text("staged\n", encoding="utf-8")
            git(unborn, "add", "staged.txt")
            (unborn / "loose.txt").write_text("loose\n", encoding="utf-8")
            plain = Path(tmp) / "plain"
            plain.mkdir()

            for root in (committed, unborn, plain):
                with self.subTest(root=root.name):
                    self.assert_matches_separate_reads(root)

    def test_observation_of_a_worktree_starts_two_git_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            counting = CountingRun()
            with mock.patch.object(driver_repository.subprocess, "run", counting):
                driver_repository.repository_observation(root)

        self.assertEqual(2, len(counting.calls), counting.calls)


class CurrentHeadOrEmptyTest(unittest.TestCase):
    def test_head_is_read_with_one_git_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeded_repository(root)
            expected = git(root, "rev-parse", "HEAD").stdout.strip()
            counting = CountingRun()
            with mock.patch.object(driver_git.subprocess, "run", counting):
                head, error = driver_git.current_head_or_empty(root)

        self.assertEqual((expected, ""), (head, error))
        self.assertEqual(1, len(counting.calls), counting.calls)

    def test_unborn_and_non_git_roots_have_an_empty_basis(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
            "os.environ", {"GIT_CEILING_DIRECTORIES": tmp}
        ):
            unborn = Path(tmp) / "unborn"
            unborn.mkdir()
            git(unborn, "init", "-q")
            plain = Path(tmp) / "plain"
            plain.mkdir()

            self.assertEqual(("", ""), driver_git.current_head_or_empty(unborn))
            self.assertEqual(("", ""), driver_git.current_head_or_empty(plain))


if __name__ == "__main__":
    unittest.main()
