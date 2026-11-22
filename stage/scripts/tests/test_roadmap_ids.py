"""Roadmap record ids skip numbers held on cards or used on other branches (W-00000398).

`manage_roadmap.py` once counted only the roadmap and decision records in its own
checkout, so it could hand out a number a started card's `reserved_ids:` held for a
sub-session (DE-00000094) or a record on another branch already used. No test
reaches a network remote.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[2]
ROADMAP = STAGE_ROOT / "skills" / "stage-roadmap" / "manage_roadmap.py"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_test_config import isolate_git_config  # noqa: E402

isolate_git_config()


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout


def roadmap(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROADMAP), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class RoadmapIdTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        shutil.copytree(V4_TEMPLATE_ROOT, self.root / ".stage")
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "seed")

    def create_theme(self) -> str:
        proc = roadmap(
            self.root, "create-theme", "--title", "Reliability", "--intent", "Predictable"
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.split(":", 1)[0]

    def create_milestone(self, theme_id: str) -> str:
        proc = roadmap(
            self.root,
            "create-milestone",
            "--theme",
            theme_id,
            "--title",
            "Stable release",
            "--purpose",
            "Ship safely",
            "--period",
            "2026 Q3",
            "--completion-criteria",
            "All checks pass",
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.split(":", 1)[0]

    def test_a_decision_skips_ids_a_started_card_holds(self) -> None:
        write(
            self.root / ".stage/work/current/W-00000001/_story.md",
            "---\nid: W-00000001\nstatus: active\nreserved_ids: DE-00000001, DE-00000002\n"
            "---\n\n# W-00000001 Sub-session card\n",
        )
        milestone_id = self.create_milestone(self.create_theme())

        proc = roadmap(self.root, "open-pursuit", milestone_id)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("via DE-00000003", proc.stdout)
        self.assertTrue((self.root / ".stage/official/decisions/records/DE-00000003.md").is_file())

    def test_a_theme_skips_ids_used_on_another_branch(self) -> None:
        git(self.root, "checkout", "-q", "-b", "other-session")
        self.assertEqual("TH-00000001", self.create_theme())
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "theme on another branch")
        git(self.root, "checkout", "-q", "main")

        self.assertEqual("TH-00000002", self.create_theme())

    def test_a_milestone_skips_ids_used_on_another_branch(self) -> None:
        theme_id = self.create_theme()
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "theme")
        git(self.root, "checkout", "-q", "-b", "other-session")
        self.assertEqual("M-00000001", self.create_milestone(theme_id))
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "milestone on another branch")
        git(self.root, "checkout", "-q", "main")

        self.assertEqual("M-00000002", self.create_milestone(theme_id))


if __name__ == "__main__":
    unittest.main()
