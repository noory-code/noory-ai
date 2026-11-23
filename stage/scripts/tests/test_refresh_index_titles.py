"""`refresh_index_titles.py`: the one command that fills index titles after a plugin update."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

STAGE = Path(__file__).resolve().parents[2]
SCRIPTS = STAGE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import refresh_index_titles  # noqa: E402

CLI = SCRIPTS / "refresh_index_titles.py"
AUDIT = SCRIPTS / "audit_stage.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
WORK_INDEX = Path(".stage/official/work/archive/index.md")
OFFICIAL_INDEX = Path(".stage/official/decisions/index.md")

CARD = """---
id: {item_id}
{title_line}kind: chore
venue: claude
scope: src/
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000001
promotion: not_applicable
---

{heading}
"""


def row(item_id: str, *more: str) -> str:
    link = f"items/{item_id}/_story.md"
    cells = [item_id, "completed", f"[{link}]({link})", *more]
    return "| " + " | ".join(cells) + " |\n"


class RenderWorkArchiveIndexTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def card(self, item_id: str, title: str = "", heading: str = "") -> Path:
        path = self.dir / f"{item_id}.md"
        path.write_text(
            CARD.format(
                item_id=item_id,
                title_line=f"title: {title}\n" if title else "",
                heading=heading,
            ),
            encoding="utf-8",
        )
        return path

    def test_rows_without_a_title_are_filled_and_titled_rows_are_kept(self):
        cards = {
            "W-00000001": self.card("W-00000001", "Old three-cell row"),
            "W-00000002": self.card("W-00000002", "Row with a dash"),
            "W-00000003": self.card("W-00000003", "The card's title"),
            "W-00000004": self.card("W-00000004", heading="# W-00000004 From the | heading"),
        }
        existing = (
            "# Work Archive\n\nProse.\n\n| Work | Final status | Item | Title |\n|---|---|---|---|\n"
            + row("W-00000001")
            + row("W-00000002", "—")
            + row("W-00000003", "A title written by hand")
            + row("W-00000004", "")
            + "\nAfter the table.\n"
        )

        text, filled, untitled = refresh_index_titles.render_work_archive_index(existing, cards)

        self.assertEqual((3, 0), (filled, untitled))
        self.assertIn(row("W-00000001", "Old three-cell row"), text)
        self.assertIn(row("W-00000002", "Row with a dash"), text)
        self.assertIn(row("W-00000003", "A title written by hand"), text)
        self.assertIn(row("W-00000004", "From the \\| heading"), text)
        self.assertTrue(text.startswith("# Work Archive\n\nProse.\n\n| Work | Final status |"))
        self.assertTrue(text.endswith("\nAfter the table.\n"))
        again = refresh_index_titles.render_work_archive_index(text, cards)
        self.assertEqual((text, 0, 0), again)

    def test_a_three_column_header_gains_the_title_cell_in_its_language(self):
        cards = {"W-00000001": self.card("W-00000001", "제목이 있는 카드")}
        existing = "| 작업 | Final status | 항목 |\n|---|---|---|\n" + row("W-00000001")

        text, filled, _untitled = refresh_index_titles.render_work_archive_index(existing, cards)

        self.assertEqual(1, filled)
        self.assertEqual(
            "| 작업 | Final status | 항목 | 제목 |\n|---|---|---|---|\n"
            + row("W-00000001", "제목이 있는 카드"),
            text,
        )

    def test_a_row_with_no_card_keeps_its_bytes_and_is_counted(self):
        cards = {"W-00000002": self.card("W-00000002")}  # neither title nor heading
        existing = (
            "| Work | Final status | Item | Title |\n|---|---|---|---|\n"
            + row("W-00000001")
            + row("W-00000002")
        )

        text, filled, untitled = refresh_index_titles.render_work_archive_index(existing, cards)

        self.assertEqual((0, 2), (filled, untitled))
        self.assertIn(row("W-00000001"), text)
        self.assertIn(row("W-00000002", "—"), text)

    def test_windows_line_endings_are_kept(self):
        cards = {"W-00000001": self.card("W-00000001", "Titled")}
        existing = (
            "| Work | Final status | Item |\r\n|---|---|---|\r\n" + row("W-00000001")[:-1] + "\r\n"
        )

        text, _filled, _untitled = refresh_index_titles.render_work_archive_index(existing, cards)

        self.assertEqual(3, text.count("\r\n"))
        self.assertNotIn("\n", text.replace("\r\n", ""))
        self.assertIn("| Titled |\r\n", text)

    def test_text_without_a_work_table_is_returned_unchanged(self):
        existing = "# Notes\n\n| Decision | Link |\n|---|---|\n| DE-00000001 | x |\n"

        self.assertEqual(
            (existing, 0, 0), refresh_index_titles.render_work_archive_index(existing, {})
        )


class UpgradeCommandTest(unittest.TestCase):
    """A project made by an earlier Stage: neither index names its records by title."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, stage)
        (stage / "settings.jsonc").unlink()
        (stage / "settings.json").write_text(json.dumps({"schema_version": 5}), encoding="utf-8")
        retro = stage / "official/work/archive/retrospectives/R-00000001.md"
        retro.parent.mkdir(parents=True, exist_ok=True)
        retro.write_text("---\nid: R-00000001\nwork_item: W-00000001\n---\n", encoding="utf-8")
        for number, title in ((1, "First archived story"), (2, "Second archived story")):
            card = stage / f"official/work/archive/items/W-{number:08d}/_story.md"
            card.parent.mkdir(parents=True)
            card.write_text(
                CARD.format(
                    item_id=f"W-{number:08d}",
                    title_line=f"title: {title}\n",
                    heading=f"# W-{number:08d} {title}",
                ),
                encoding="utf-8",
            )
        (self.root / WORK_INDEX).write_text(
            "# Work Archive\n\n| Work | Final status | Item | Title |\n|---|---|---|---|\n"
            + row("W-00000001")
            + row("W-00000002", "—"),
            encoding="utf-8",
        )
        record = stage / "official/decisions/records/DE-00000001.md"
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(
            "---\nid: DE-00000001\nstatus: promoted\n---\n\n# DE-00000001 Where rules live\n",
            encoding="utf-8",
        )
        (self.root / OFFICIAL_INDEX).write_text(
            "# Decisions\n\n| Decision | Status | Owner | Link |\n|---|---|---|---|\n"
            "| DE-00000001 | promoted | user | [records/DE-00000001.md](records/DE-00000001.md) |\n",
            encoding="utf-8",
        )

    def run_script(self, script: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), "--project-root", str(self.root)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def upgrade_findings(self) -> list[str]:
        out = self.run_script(AUDIT).stdout
        return [
            line for line in out.splitlines() if " DECISION005 " in line or " ARCHIVE005 " in line
        ]

    def test_the_audit_names_the_command_and_one_run_fills_both_indexes(self):
        before = self.upgrade_findings()

        proc = self.run_script(CLI)
        after = self.upgrade_findings()
        work_index = (self.root / WORK_INDEX).read_text(encoding="utf-8")
        official_index = (self.root / OFFICIAL_INDEX).read_text(encoding="utf-8")

        self.assertEqual(2, len(before), before)
        self.assertTrue(before[0].startswith("ERROR DECISION005 [.stage/official/decisions/index.md]"))
        self.assertTrue(
            before[1].startswith("WARNING ARCHIVE005 [.stage/official/work/archive/index.md]")
        )
        self.assertIn("2 row(s) without a title", before[1])
        for line in before:
            self.assertIn("`python3 stage/scripts/refresh_index_titles.py --project-root .`", line)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            [
                "Pending-decision index already current: .stage/decisions/index.md",
                "Official decision titles refreshed: .stage/official/decisions/index.md",
                "Work archive titles refreshed: .stage/official/work/archive/index.md",
            ],
            proc.stdout.strip().splitlines(),
        )
        self.assertIn(row("W-00000001", "First archived story"), work_index)
        self.assertIn(row("W-00000002", "Second archived story"), work_index)
        self.assertIn("| DE-00000001 | Where rules live | promoted | user |", official_index)
        self.assertEqual([], after)

    def test_a_second_run_changes_nothing(self):
        self.run_script(CLI)
        first = [(self.root / path).read_bytes() for path in (WORK_INDEX, OFFICIAL_INDEX)]

        proc = self.run_script(CLI)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(
            first, [(self.root / path).read_bytes() for path in (WORK_INDEX, OFFICIAL_INDEX)]
        )
        self.assertEqual(3, proc.stdout.count("already current"))

    def test_a_row_the_command_cannot_title_is_said_and_not_reported_as_fillable(self):
        index = self.root / WORK_INDEX
        index.write_text(
            index.read_text(encoding="utf-8") + row("W-00000009"), encoding="utf-8"
        )

        proc = self.run_script(CLI)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("1 work archive row(s) still have no title", proc.stdout)
        self.assertIn(row("W-00000009"), index.read_text(encoding="utf-8"))
        self.assertEqual([], self.upgrade_findings())

    def test_a_project_without_stage_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(CLI), "--project-root", tmp],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        self.assertEqual(2, proc.returncode)
        self.assertIn("Cannot refresh index titles", proc.stderr)


if __name__ == "__main__":
    unittest.main()
