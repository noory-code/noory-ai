"""started_cards.py lists the cards in progress across fetched branches for a take-over."""

from __future__ import annotations

import json
import os
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

SCRIPT = STAGE / "scripts" / "started_cards.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
CURRENT = ".stage/work/current"
ARCHIVE = ".stage/official/work/archive/items"


def git(root: Path, *args: str, when: int = 0) -> str:
    env = dict(os.environ)
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{when} +0000"
    proc = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


class StartedCardsTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, stage)
        (stage / "settings.jsonc").unlink()
        (stage / "settings.json").write_text(json.dumps({"schema_version": 5}), encoding="utf-8")
        git(self.root, "init", "-q", "-b", "main")
        self.clock = 1_700_000_000
        self.commit("init")

    def commit(self, message: str) -> None:
        self.clock += 60
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", message, when=self.clock)

    def card(self, item: str, status: str = "active", next_action: str = "", root: str = CURRENT) -> None:
        path = self.root / root / item / "_story.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {item}\ntitle: 카드 {item}\nstatus: {status}\nverification: pending\n"
            f"review: pending\nscope: src/\n---\n\n# {item}\n\n## Next action\n\n{next_action}\n\n"
            "## Progress\n",
            encoding="utf-8",
        )

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(self.root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def branch(self, name: str) -> None:
        git(self.root, "checkout", "-q", "-b", name, "main")

    def test_a_card_started_on_an_unmerged_branch_is_listed_from_a_detached_head(self) -> None:
        self.branch("work")
        self.card("W-00000001")
        self.commit("start")
        git(self.root, "checkout", "-q", "--detach", "main")

        proc = self.run_script()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("Base: main", proc.stdout)
        self.assertIn("## Cards in progress: 1", proc.stdout)
        self.assertIn("- W-00000001 카드 W-00000001", proc.stdout)
        self.assertIn("status: active, verification: pending, review: pending", proc.stdout)
        self.assertIn(f"read: `{CURRENT}/W-00000001/_story.md` on `work`", proc.stdout)
        self.assertIn("next action: (empty)", proc.stdout)

    def test_a_card_the_base_branch_archived_is_dropped_from_a_stale_branch(self) -> None:
        self.branch("stale")
        self.card("W-00000001")
        self.commit("start")
        git(self.root, "checkout", "-q", "main")
        self.card("W-00000001", status="archived", root=ARCHIVE)
        self.commit("squash-merged and archived")

        proc = self.run_script()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("## Cards in progress: 0", proc.stdout)
        self.assertNotIn("W-00000001", proc.stdout)

    def test_the_copy_edited_last_is_the_one_to_read(self) -> None:
        self.branch("work")
        self.card("W-00000001")
        self.commit("start")
        git(self.root, "checkout", "-q", "-b", "zz-orchestrator", "work")
        self.card("W-00000001", next_action="- Waiting on user: pick A or B")
        self.commit("record the report")
        git(self.root, "checkout", "-q", "work")
        (self.root / "code.txt").write_text("later code\n", encoding="utf-8")
        self.commit("code only")
        git(self.root, "checkout", "-q", "--detach", "main")

        out = self.run_script().stdout

        self.assertIn("on `zz-orchestrator`", out)
        self.assertIn("other copies: `work`", out)
        self.assertIn("## Waiting in the records: 1", out)
        self.assertIn("- W-00000001: Waiting on user: pick A or B", out)

    def test_blocked_cards_open_decisions_and_questions_are_waiting(self) -> None:
        self.card("W-00000001", status="blocked", next_action="Ask which venue")
        stage = self.root / ".stage"
        (stage / "decisions/pending/DE-00000001.md").write_text(
            "---\nid: DE-00000001\nstatus: open\n---\n", encoding="utf-8"
        )
        (stage / "decisions/pending/DE-00000002.md").write_text(
            "---\nid: DE-00000002\nstatus: decided\n---\n", encoding="utf-8"
        )
        (stage / "state/questions").mkdir(parents=True, exist_ok=True)
        (stage / "state/questions/Q-00000001.md").write_text(
            "---\nid: Q-00000001\ntitle: Which host\n---\n", encoding="utf-8"
        )
        self.commit("records")

        out = self.run_script().stdout

        self.assertIn("- W-00000001 is `blocked`: Ask which venue", out)
        self.assertIn("- decision DE-00000001 (open): .stage/decisions/pending/DE-00000001.md", out)
        self.assertNotIn("DE-00000002", out)
        self.assertIn("- question Q-00000001 Which host: .stage/state/questions/Q-00000001.md", out)
        self.assertIn("## Waiting in the records: 3", out)

    def test_a_planned_card_is_not_in_progress(self) -> None:
        self.card("W-00000001", status="ready", root=".stage/work/planned")
        self.commit("plan")

        self.assertIn("## Cards in progress: 0", self.run_script().stdout)

    def test_a_missing_base_ref_is_an_error(self) -> None:
        proc = self.run_script("--base", "origin/nowhere")

        self.assertEqual(2, proc.returncode)
        self.assertIn("pass --base <ref>", proc.stderr)


if __name__ == "__main__":
    unittest.main()
