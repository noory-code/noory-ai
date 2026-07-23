from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / "init_stage.py"
RUNTIME_IGNORE_ENTRY = ".stage/.runtime/"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


class InitStageGitignoreTest(unittest.TestCase):
    def make(self, git_kind: str = "directory") -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        if git_kind == "directory":
            (root / ".git").mkdir()
        elif git_kind == "file":
            (root / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        return tmp, root

    def test_creates_gitignore_in_git_repository(self):
        tmp, root = self.make()
        with tmp:
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_bytes()

        self.assertEqual(f"{RUNTIME_IGNORE_ENTRY}\n".encode(), content)
        self.assertIn("created .gitignore", result.stdout)

    def test_appends_entry_and_preserves_existing_content(self):
        tmp, root = self.make()
        with tmp:
            original = b"build/\r\n*.log\r\n"
            (root / ".gitignore").write_bytes(original)
            result = run(root, "--force")
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_bytes()

        self.assertEqual(original + f"{RUNTIME_IGNORE_ENTRY}\n".encode(), content)
        self.assertIn("appended", result.stdout)

    def test_existing_entry_without_trailing_slash_is_unchanged(self):
        tmp, root = self.make()
        with tmp:
            original = b"build/\n  .stage/.runtime  \n"
            (root / ".gitignore").write_bytes(original)
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_bytes()

        self.assertEqual(original, content)
        self.assertEqual(1, content.count(b".stage/.runtime"))
        self.assertIn("preserved existing", result.stdout)

    def test_appends_cleanly_after_line_without_trailing_newline(self):
        tmp, root = self.make()
        with tmp:
            original = b"build/"
            (root / ".gitignore").write_bytes(original)
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_bytes()

        self.assertEqual(original + f"\n{RUNTIME_IGNORE_ENTRY}\n".encode(), content)

    def test_git_file_is_treated_as_git_repository(self):
        tmp, root = self.make(git_kind="file")
        with tmp:
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_text(encoding="utf-8")

        self.assertEqual(f"{RUNTIME_IGNORE_ENTRY}\n", content)

    def test_non_git_directory_does_not_get_gitignore(self):
        tmp, root = self.make(git_kind="none")
        with tmp:
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            gitignore_exists = (root / ".gitignore").exists()

        self.assertFalse(gitignore_exists)
        self.assertIn("skipped (not a git repository)", result.stdout)

    def test_commented_entry_does_not_count_as_present(self):
        tmp, root = self.make()
        with tmp:
            original = b"# .stage/.runtime/\n"
            (root / ".gitignore").write_bytes(original)
            result = run(root)
            self.assertEqual(0, result.returncode, result.stderr)
            content = (root / ".gitignore").read_bytes()

        self.assertEqual(original + f"{RUNTIME_IGNORE_ENTRY}\n".encode(), content)


if __name__ == "__main__":
    unittest.main()
