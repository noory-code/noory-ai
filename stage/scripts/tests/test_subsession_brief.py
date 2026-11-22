"""The brief a main session sends a sub-session for one started card (DE-00000094)."""

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

    def test_a_card_that_is_not_started_has_no_brief(self) -> None:
        proc = brief(self.root, "W-00000099")

        self.assertEqual(1, proc.returncode)
        self.assertIn("start it first", proc.stderr)


if __name__ == "__main__":
    unittest.main()
