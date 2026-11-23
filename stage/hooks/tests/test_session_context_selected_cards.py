"""Session-start view of selected planned cards, and the day an observation's age counts from."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_context  # noqa: E402


V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"


def card(record_id: str, title: str, status: str, priority: str = "") -> str:
    return (
        f"---\nid: {record_id}\ntitle: {title}\nkind: fix\nstatus: {status}\n"
        f"priority: {priority}\n---\n# {record_id} {title}\n"
    )


class SelectedPlannedCardViewTest(unittest.TestCase):
    def make_fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")
        return tmp, root

    def test_selected_story_and_epic_folder_cards_are_listed(self):
        tmp, root = self.make_fixture()
        with tmp:
            stage_root = root / ".stage"
            planned = stage_root / "work" / "planned"
            story = planned / "W-00000002" / "_story.md"
            epic = planned / "W-00000003" / "_epic.md"
            captured = planned / "W-00000004" / "_story.md"
            for path, text in (
                (story, card("W-00000002", "Selected story", "selected", "4")),
                (epic, card("W-00000003", "Selected epic", "selected")),
                (captured, card("W-00000004", "Captured story", "captured")),
            ):
                path.parent.mkdir(parents=True)
                path.write_text(text, encoding="utf-8")

            lines = stage_context.selected_backlog_lines(stage_root)
            context = stage_context.session_context(root)

        self.assertEqual(
            lines,
            [
                "- W-00000002 Selected story (priority: 4)",
                "- W-00000003 Selected epic",
            ],
        )
        self.assertIn("### Selected backlog", context)
        self.assertIn("W-00000002 Selected story", context)
        self.assertNotIn("Captured story", context)

    def test_the_card_template_at_the_planned_root_is_never_listed(self):
        tmp, root = self.make_fixture()
        with tmp:
            stage_root = root / ".stage"
            planned = stage_root / "work" / "planned"
            (planned / "_template.md").write_text(
                card("W-NNNNNNNN", "Template", "selected"), encoding="utf-8"
            )

            lines = stage_context.selected_backlog_lines(stage_root)

        self.assertEqual(lines, [])


class ObservationAgeDayTest(unittest.TestCase):
    def test_today_is_the_local_date_not_the_utc_date(self):
        # 08:30 on 21 November in Seoul is still 20 November in UTC.
        now = datetime(2026, 11, 20, 23, 30, tzinfo=timezone.utc)
        seoul = timezone(timedelta(hours=9))

        self.assertEqual(stage_context.local_today(now, seoul), date(2026, 11, 21))

    def test_an_observation_opened_today_locally_reads_as_open_zero_days(self):
        tmp = tempfile.TemporaryDirectory()
        with tmp:
            root = Path(tmp.name)
            shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")
            stage_root = root / ".stage"
            (stage_root / "state" / "observations" / "O-00000001.md").write_text(
                "---\nid: O-00000001\nopened: 2026-11-21\ntitle: Opened this morning\n"
                "work_items:\n---\n# O-00000001 Opened this morning\n",
                encoding="utf-8",
            )
            with mock.patch.object(
                stage_context, "local_today", return_value=date(2026, 11, 21)
            ) as local_today:
                lines = stage_context.open_observation_lines(stage_root)

        local_today.assert_called_once_with()
        self.assertEqual(lines, ["- O-00000001 Opened this morning (open 0d)"])


if __name__ == "__main__":
    unittest.main()
