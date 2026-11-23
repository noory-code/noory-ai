"""Which sections a work card carries: no retrospective copies, and a short maintenance card."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from python_shell_command import python_command

STAGE = Path(__file__).resolve().parents[2]
REGISTER = STAGE / "skills" / "stage-work" / "register_work.py"
SKILL = REGISTER.parent / "SKILL.md"
START = STAGE / "scripts" / "start_work.py"
CLOSE = STAGE / "skills" / "stage-retrospective" / "close_work.py"

RETROSPECTIVE_COPIES = ("## Retrospective", "## Promotion decision")
ACHIEVEMENT_ONLY = ("## User value", "## Risks", "## Next action", "## Related truth")


def run(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(cli), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def register(root: Path, *args: str) -> subprocess.CompletedProcess:
    return run(
        REGISTER,
        root,
        "--scale",
        "story",
        "--title",
        "Sample",
        "--kind",
        "fix",
        "--scope",
        "src/",
        "--purpose",
        "The export command fails on empty input",
        "--success-criterion",
        "The export command writes an empty file for empty input",
        *args,
    )


def headings(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("## ")]


class CardSectionsTest(unittest.TestCase):
    def make(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage = root / ".stage"
        (stage / "work/current").mkdir(parents=True)
        (stage / "work/planned").mkdir(parents=True)
        (stage / "work/retrospectives").mkdir(parents=True)
        (stage / "official/work/archive/items").mkdir(parents=True)
        (stage / "settings.json").write_text('{"schema_version": 5}\n', encoding="utf-8")
        return tmp, root

    def card(self, root: Path, lifecycle: str) -> str:
        return (root / ".stage/work" / lifecycle / "W-00000001/_story.md").read_text(
            encoding="utf-8"
        )

    def test_a_registered_card_has_no_retrospective_copies(self):
        tmp, root = self.make()
        with tmp:
            proc = register(root)
            card = self.card(root, "current")

        self.assertEqual(0, proc.returncode, proc.stderr)
        found = headings(card)
        for heading in RETROSPECTIVE_COPIES:
            self.assertNotIn(heading, found)
        for heading in (*ACHIEVEMENT_ONLY, "## Progress", "## Verification"):
            self.assertIn(heading, found)

    def test_a_started_card_has_no_retrospective_copies(self):
        tmp, root = self.make()
        with tmp:
            captured = register(root, "--backlog")
            started = run(START, root, "W-00000001", "--scope", "src/")
            card = self.card(root, "current")

        self.assertEqual(0, captured.returncode, captured.stderr)
        self.assertEqual(0, started.returncode, started.stderr)
        found = headings(card)
        for heading in RETROSPECTIVE_COPIES:
            self.assertNotIn(heading, found)
        for heading in ("## Related truth", "## Progress", "## Verification"):
            self.assertIn(heading, found)

    def test_a_card_without_retrospective_copies_closes(self):
        tmp, root = self.make()
        with tmp:
            register(root)
            path = root / ".stage/work/current/W-00000001/_story.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("retrospective: pending", "retrospective: completed")
            text = text.replace("retrospective_ref:", "retrospective_ref: R-00000001")
            path.write_text(text, encoding="utf-8")
            (root / ".stage/work/retrospectives/R-00000001.md").write_text(
                "---\nid: R-00000001\nwork_item: W-00000001\n---\n", encoding="utf-8"
            )

            proc = run(
                CLOSE,
                root,
                "W-00000001",
                "--check",
                python_command("print('ok')"),
                "--promotion",
                "not_applicable",
            )
            card = path.read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", card)

    def test_a_maintenance_card_asks_only_what_broke_and_when_it_stands_again(self):
        tmp, root = self.make()
        with tmp:
            proc = register(root, "--maintenance")
            card = self.card(root, "current")

        self.assertEqual(0, proc.returncode, proc.stderr)
        found = headings(card)
        for heading in (*ACHIEVEMENT_ONLY, *RETROSPECTIVE_COPIES):
            self.assertNotIn(heading, found)
        self.assertEqual(
            ["## Purpose", "## Actions", "## Scope", "## Success criteria", "## Sessions",
             "## Progress", "## Verification"],
            found,
        )
        self.assertIn("\nmaintenance: true\n", card)
        self.assertIn("The export command fails on empty input", card)
        self.assertIn("- The export command writes an empty file for empty input", card)

    def test_a_planned_maintenance_card_stays_short_after_it_starts(self):
        tmp, root = self.make()
        with tmp:
            captured = register(root, "--maintenance", "--backlog")
            planned = self.card(root, "planned")
            started = run(START, root, "W-00000001", "--scope", "src/")
            current = self.card(root, "current")

        self.assertEqual(0, captured.returncode, captured.stderr)
        self.assertEqual(0, started.returncode, started.stderr)
        self.assertEqual(
            ["## Purpose", "## Actions", "## Scope", "## Success criteria"], headings(planned)
        )
        self.assertEqual(
            ["## Purpose", "## Actions", "## Scope", "## Success criteria", "## Sessions",
             "## Progress", "## Verification"],
            headings(current),
        )
        self.assertIn("\nmaintenance: true\n", current)

    def test_an_ordinary_card_carries_no_maintenance_field(self):
        tmp, root = self.make()
        with tmp:
            register(root)
            card = self.card(root, "current")

        self.assertNotIn("maintenance:", card)

    def test_maintenance_is_refused_with_a_milestone(self):
        tmp, root = self.make()
        with tmp:
            proc = register(root, "--maintenance", "--milestone", "M-00000001")
            created = (root / ".stage/work/current/W-00000001").exists()

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("--maintenance", proc.stderr)
        self.assertIn("milestone", proc.stderr)
        self.assertFalse(created)

    def test_maintenance_is_refused_for_an_epic(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                REGISTER,
                root,
                "--scale",
                "epic",
                "--title",
                "Sample",
                "--kind",
                "fix",
                "--scope",
                "src/",
                "--purpose",
                "Something broke",
                "--success-criterion",
                "It works again",
                "--maintenance",
            )
            created = (root / ".stage/work/current/W-00000001").exists()

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("--maintenance", proc.stderr)
        self.assertFalse(created)

    def test_the_skill_states_the_maintenance_test_and_its_two_questions(self):
        skill = SKILL.read_text(encoding="utf-8")

        self.assertIn("--maintenance", skill)
        self.assertIn("When this work is done, does the product do something it could not do", skill)
        self.assertIn("What broke?", skill)
        self.assertIn("How will you know it stands again?", skill)


if __name__ == "__main__":
    unittest.main()
