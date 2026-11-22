"""start_work.py refuses a card another fetched branch already started or archived."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

STAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_test_config import isolate_git_config  # noqa: E402

isolate_git_config()

REGISTER = STAGE / "skills" / "stage-work" / "register_work.py"
START = STAGE / "scripts" / "start_work.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
SETTINGS = {"schema_version": 5, "venue_routing": {"fix": "claude"}}
ITEM = "W-00000001"


def run(script: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


class StartWorkOtherBranchTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, stage)
        (stage / "settings.jsonc").unlink()
        (stage / "settings.json").write_text(json.dumps(SETTINGS), encoding="utf-8")
        git(self.root, "init", "-q", "-b", "main")
        registered = run(
            REGISTER,
            self.root,
            "--backlog",
            "--title",
            "Fix the thing",
            "--kind",
            "fix",
            "--scale",
            "story",
            "--scope",
            "src/",
            "--purpose",
            "Deliver the requested outcome.",
            "--success-criterion",
            "The user can observe the requested outcome",
        )
        self.assertEqual(0, registered.returncode, registered.stderr)
        self.commit("register")

    def commit(self, message: str) -> None:
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", message)

    def start(self) -> subprocess.CompletedProcess[str]:
        return run(START, self.root, ITEM, "--scope", "src/")

    def start_on_branch(self, branch: str) -> None:
        git(self.root, "checkout", "-q", "-b", branch)
        started = self.start()
        self.assertEqual(0, started.returncode, started.stderr)
        self.commit("start")

    def test_refuses_a_card_another_branch_started(self) -> None:
        self.start_on_branch("other")
        git(self.root, "checkout", "-q", "main")

        proc = self.start()

        self.assertEqual(1, proc.returncode)
        self.assertIn(f"refusing: {ITEM} is already started on another branch", proc.stderr)
        self.assertIn("other (started)", proc.stderr)
        self.assertTrue((self.root / ".stage/work/planned" / ITEM / "_story.md").is_file())

    def test_refuses_a_card_another_branch_archived(self) -> None:
        git(self.root, "checkout", "-q", "-b", "other")
        archived = self.root / ".stage/official/work/archive/items" / ITEM
        archived.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(self.root / ".stage/work/planned" / ITEM), str(archived))
        self.commit("archive")
        git(self.root, "checkout", "-q", "main")

        proc = self.start()

        self.assertEqual(1, proc.returncode)
        self.assertIn("other (archived)", proc.stderr)

    def test_starts_when_another_branch_only_has_the_card_planned(self) -> None:
        git(self.root, "checkout", "-q", "-b", "other")
        (self.root / "notes.txt").write_text("unrelated\n", encoding="utf-8")
        self.commit("unrelated")
        git(self.root, "checkout", "-q", "main")

        proc = self.start()

        self.assertEqual(0, proc.returncode, proc.stderr)

    def test_starts_when_the_branch_that_started_it_is_merged(self) -> None:
        # A merged branch's state is already in HEAD; here HEAD planned the card again.
        self.start_on_branch("other")
        git(self.root, "checkout", "-q", "main")
        git(self.root, "merge", "-q", "--no-edit", "other")
        current = self.root / ".stage/work/current" / ITEM
        shutil.move(str(current), str(self.root / ".stage/work/planned" / ITEM))
        story = self.root / ".stage/work/planned" / ITEM / "_story.md"
        story.write_text(
            story.read_text(encoding="utf-8").replace("status: active", "status: captured"),
            encoding="utf-8",
        )
        self.commit("plan again")

        proc = self.start()

        self.assertEqual(0, proc.returncode, proc.stderr)


if __name__ == "__main__":
    unittest.main()
