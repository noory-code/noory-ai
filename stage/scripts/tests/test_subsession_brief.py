"""The briefs a main session sends work and verification sessions (DE-00000094, DE-00000099)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
BRIEF = SCRIPTS / "subsession_brief.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def brief(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BRIEF), "--project-root", str(root), "--main-session", "session_main", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class SubsessionBriefTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        write(self.root / ".stage/settings.json", '{"schema_version": 5}\n')
        write(
            self.root / ".stage/decisions/pending/DE-00000007.md",
            "---\nid: DE-00000007\n---\n\n# DE-00000007 Choice\n",
        )

    def card(self, extra: str = "", where: str = "W-00000002/_story.md") -> None:
        write(
            self.root / ".stage/work/current" / where,
            "---\nid: W-00000002\ntitle: Build it\nstatus: active\nscope: src/\n"
            "acceptance:\n  - \"python3 -m unittest -q\"\n"
            f"decision_refs: DE-00000007\n{extra}---\n\n# W-00000002 Build it\n",
        )

    def test_a_card_with_reserved_ids_tells_the_sub_session_how_to_take_them(self) -> None:
        self.card("reserved_ids: DE-00000008, DE-00000009\n")

        proc = brief(self.root, "W-00000002", "--branch", "claude/w2")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("sub-session of the main session `session_main`", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn("`python3 -m unittest -q`", out)
        self.assertIn("reserved `DE-00000008, DE-00000009`", out)
        self.assertIn("--from-card W-00000002 <PREFIX>", out)
        self.assertIn("own branch `claude/w2`", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("send the main session `session_main` one message", out)
        self.assertIn("Do not edit the card's `## Progress` or `## Next action` section", out)

    def test_the_brief_asks_for_scope_crossings_in_the_commit_report(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("outside the scope, and why, in that report's `Decisions made:`", out)
        self.assertIn("reads only the commit's report, not your message", out)

    def test_the_brief_leaves_other_os_checks_to_the_main_session(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("Checks that must run on another OS (for example Windows) are not yours to run", out)
        self.assertIn("The main session opens the pull request and reads its CI jobs.", out)

    def test_a_card_without_reserved_ids_forbids_new_records(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("No ids are reserved for this card", out)
        self.assertNotIn("--from-card", out)

    def test_a_nested_story_lists_its_epic_first(self) -> None:
        write(
            self.root / ".stage/work/current/W-00000001/_epic.md",
            "---\nid: W-00000001\ntitle: Epic\nstatus: active\n---\n",
        )
        self.card(where="W-00000001/W-00000002/_story.md")

        out = brief(self.root, "W-00000002").stdout

        epic = out.index("W-00000001/_epic.md` (ancestor)")
        story = out.index("W-00000001/W-00000002/_story.md`")
        self.assertLess(epic, story)

    def epic(self) -> None:
        write(
            self.root / ".stage/work/current/W-00000001/_epic.md",
            "---\nid: W-00000001\ntitle: Ship it\nstatus: active\nscope: src/, docs/\n"
            "acceptance: []\n---\n\n# W-00000001 Ship it\n",
        )
        self.card(where="W-00000001/W-00000002/_story.md")
        write(
            self.root / ".stage/work/current/W-00000001/W-00000003/_story.md",
            "---\nid: W-00000003\ntitle: Document it\nstatus: completed\nscope: docs/\n"
            "acceptance: []\n---\n\n# W-00000003 Document it\n",
        )

    def test_an_epic_brief_runs_its_stories_in_sub_agents_with_one_commit_each(self) -> None:
        self.epic()

        proc = brief(self.root, "W-00000001", "--branch", "claude/w1")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("work session of the main session `session_main`. You build one Stage epic", out)
        self.assertIn("(DE-00000094, DE-00000099)", out)
        self.assertIn(
            "- W-00000002 Build it (`active`): `.stage/work/current/W-00000001/W-00000002/_story.md`",
            out,
        )
        self.assertIn("  - scope: `src/`", out)
        self.assertIn("  - check: `python3 -m unittest -q`", out)
        self.assertIn("- W-00000003 Document it (`completed`)", out)
        self.assertIn("status is not one of `archived`, `completed`, `rejected`", out)
        self.assertIn("Do not create\n  another cloud session for a story", out)
        self.assertIn("Commit each story as its own commit, with the story's id", out)
        self.assertIn("Write one `### Executor report` per story", out)
        self.assertIn("each story's id and the commit that carries its executor report", out)
        self.assertIn("Do not edit any card's `status`", out)

    def test_a_story_brief_has_no_stories_section(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertNotIn("## Stories", out)
        self.assertIn("Write the `### Executor report` in the body of your last commit", out)

    def test_a_verify_brief_judges_and_changes_nothing(self) -> None:
        self.card("reserved_ids: DE-00000008\n")

        proc = brief(
            self.root, "W-00000002", "--role", "verify", "--branch", "claude/w2", "--commit", "abc1234"
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("verification session of the main session `session_main`. You judge one Stage card", out)
        self.assertIn("you change nothing", out)
        self.assertIn("the main session closes and merges it", out)
        self.assertIn("The change is commit `abc1234` on branch `claude/w2`.", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn("Judge every item under the card's `## Success criteria`", out)
        self.assertIn("Run these checks yourself:\n- `python3 -m unittest -q`", out)
        self.assertIn("Do not edit, commit, or push anything", out)
        self.assertIn("Do not write a review verdict file", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("`PASS` or `FAIL`", out)
        self.assertIn("`approved: true` when every criterion passes", out)
        self.assertIn("Send the main session `session_main` one message with:", out)
        self.assertNotIn("## Record ids", out)
        self.assertNotIn("--from-card", out)
        self.assertNotIn("Commit and push only to your own branch", out)

    def test_a_verify_brief_without_a_commit_finds_the_card_by_id_in_the_log(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002", "--role", "verify").stdout

        self.assertIn(
            "The change is on the branch you were created from: for each card, the last commit "
            "whose message names its id.",
            out,
        )

    def test_a_verify_brief_for_an_epic_judges_each_story(self) -> None:
        self.epic()

        out = brief(self.root, "W-00000001", "--role", "verify", "--branch", "claude/w1").stdout

        self.assertIn("You judge one Stage epic, story by story", out)
        self.assertIn("- W-00000002 Build it (`active`)", out)
        self.assertIn("Judge each story on its own commit, then the epic's own success criteria.", out)
        self.assertIn("one message per story, and one for the epic, with:", out)

    def test_an_unknown_role_is_refused(self) -> None:
        self.card()

        proc = brief(self.root, "W-00000002", "--role", "plan")

        self.assertEqual(2, proc.returncode)
        self.assertIn("invalid choice", proc.stderr)

    def test_a_card_that_is_not_started_has_no_brief(self) -> None:
        proc = brief(self.root, "W-00000099")

        self.assertEqual(1, proc.returncode)
        self.assertIn("start it first", proc.stderr)


if __name__ == "__main__":
    unittest.main()
