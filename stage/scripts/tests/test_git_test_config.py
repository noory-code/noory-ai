from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from git_test_config import (
    TEST_GIT_USER_EMAIL,
    TEST_GIT_USER_NAME,
    isolate_git_config,
)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout.strip()


class IsolatedGitConfigTest(unittest.TestCase):
    def setUp(self):
        self.config_path = isolate_git_config()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        git(self.root, "init", "-q")

    def test_every_call_points_git_at_the_same_configuration(self):
        self.assertEqual(self.config_path, isolate_git_config())
        self.assertEqual(str(self.config_path), os.environ["GIT_CONFIG_GLOBAL"])
        self.assertTrue(self.config_path.is_file())

    def test_a_fresh_repository_commits_as_the_test_identity_without_setup(self):
        (self.root / "seed.txt").write_text("seed", encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "seed")

        self.assertEqual(
            f"{TEST_GIT_USER_NAME} <{TEST_GIT_USER_EMAIL}>",
            git(self.root, "log", "-1", "--format=%an <%ae>"),
        )

    def test_commits_spawn_neither_maintenance_nor_a_signer(self):
        self.assertEqual("false", git(self.root, "config", "maintenance.auto"))
        self.assertEqual("0", git(self.root, "config", "gc.auto"))
        self.assertEqual("false", git(self.root, "config", "commit.gpgsign"))

    def test_init_copies_only_the_exclude_file_tests_append_to(self):
        git_dir = self.root / ".git"

        self.assertTrue((git_dir / "info" / "exclude").is_file())
        hooks = git_dir / "hooks"
        self.assertEqual([], sorted(hooks.iterdir()) if hooks.is_dir() else [])

    def test_repository_settings_still_override_the_test_identity(self):
        git(self.root, "config", "user.name", "Repository Owner")

        self.assertEqual("Repository Owner", git(self.root, "config", "user.name"))


if __name__ == "__main__":
    unittest.main()
