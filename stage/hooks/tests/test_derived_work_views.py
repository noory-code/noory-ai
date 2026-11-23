"""The active and review work views come from card status, not list files (DE-00000091)."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[1]
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import stage_context  # noqa: E402
import stage_topology  # noqa: E402
import stage_work  # noqa: E402


def write_card(stage_root: Path, item_id: str, title: str, status: str) -> None:
    path = stage_root / "work" / "current" / item_id / "_story.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"id: {item_id}\n"
        f"title: {title}\n"
        "kind: development\n"
        "venue: claude\n"
        f"status: {status}\n"
        "verification: pending\n"
        "retrospective: pending\n"
        "promotion: pending\n"
        "---\n\n"
        f"# {item_id} {title}\n",
        encoding="utf-8",
    )


def section(context: str, title: str) -> str:
    marker = f"### {title}\n"
    if marker not in context:
        return ""
    return context.split(marker, 1)[1].split("\n### ", 1)[0]


class DerivedWorkViewTest(unittest.TestCase):
    def make_stage(self) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage_root = root / ".stage"
        stage_root.mkdir()
        (stage_root / "settings.json").write_text(
            '{"schema_version": 5}\n', encoding="utf-8"
        )
        return tmp, root, stage_root

    def test_session_start_views_come_from_card_status_without_list_files(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            write_card(stage_root, "W-00000001", "Running card", "active")
            write_card(stage_root, "W-00000002", "Stuck card", "blocked")
            write_card(stage_root, "W-00000003", "Closed card", "completed")
            write_card(stage_root, "W-00000004", "Declined card", "rejected")
            context = stage_context.session_context(root)
            listed = [
                relative
                for relative in stage_topology.RETIRED_WORK_LISTS
                if (stage_root / relative).exists()
            ]

        self.assertEqual(listed, [])
        active = section(context, "Active work")
        review = section(context, "Review candidates")
        self.assertIn("W-00000001", active)
        self.assertIn("W-00000002", active)
        self.assertNotIn("W-00000003", active)
        self.assertIn("work/current/W-00000001/_story.md", active)
        self.assertIn("W-00000003", review)
        self.assertIn("W-00000004", review)
        self.assertNotIn("W-00000001", review)

    def test_a_stale_list_file_does_not_reach_the_session(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            write_card(stage_root, "W-00000001", "Running card", "active")
            stale = stage_root / "work" / "active.md"
            stale.write_text(
                "| W-00000099 | development | claude | Closed long ago | active |\n",
                encoding="utf-8",
            )
            context = stage_context.session_context(root)

        self.assertNotIn("W-00000099", context)
        self.assertIn("W-00000001", section(context, "Active work"))

    def test_no_view_section_when_no_card_qualifies(self):
        tmp, root, _stage_root = self.make_stage()
        with tmp:
            context = stage_context.session_context(root)

        self.assertNotIn("### Active work", context)
        self.assertNotIn("### Review candidates", context)

    def test_a_card_without_parent_or_child_is_carried_once(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            write_card(stage_root, "W-00000001", "Running card", "active")
            write_card(stage_root, "W-00000003", "Closed card", "completed")
            context = stage_context.session_context(root)

        self.assertEqual(context.count("Running card"), 1)
        self.assertEqual(context.count("Closed card"), 1)
        self.assertEqual(context.count("W-00000001 "), 1)
        self.assertNotIn("### Current work hierarchy", context)

    def test_a_tree_names_its_cards_by_id_and_the_tables_carry_the_titles(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            epic = stage_root / "work" / "current" / "W-00000001"
            (epic / "W-00000002").mkdir(parents=True)
            for path, item_id, title in (
                (epic / "_epic.md", "W-00000001", "The epic"),
                (epic / "W-00000002" / "_story.md", "W-00000002", "The story"),
            ):
                path.write_text(
                    f"---\nid: {item_id}\ntitle: {title}\nkind: development\n"
                    "venue: claude\nstatus: active\nverification: pending\n"
                    "retrospective: pending\npromotion: pending\n---\n",
                    encoding="utf-8",
                )
            write_card(stage_root, "W-00000005", "Alone", "active")
            context = stage_context.session_context(root)

        hierarchy = section(context, "Current work hierarchy")
        self.assertIn("- W-00000001 [active]\n  - W-00000002 [active]", hierarchy)
        self.assertNotIn("W-00000005", hierarchy)
        for title in ("The epic", "The story", "Alone"):
            self.assertEqual(context.count(title), 1, title)
        self.assertIn("The story", section(context, "Active work"))

    def test_the_tree_alone_still_names_every_card_with_its_title(self):
        tmp, _root, stage_root = self.make_stage()
        with tmp:
            write_card(stage_root, "W-00000001", "Running card", "active")
            hierarchy = stage_context.work_hierarchy_view(stage_root)

        self.assertIn("- W-00000001 Running card [active]", hierarchy)

    def test_a_pipe_in_a_title_does_not_break_the_table(self):
        tmp, _root, stage_root = self.make_stage()
        with tmp:
            write_card(stage_root, "W-00000001", "a | b", "active")
            view = stage_context.derived_work_view(
                stage_root, stage_work.ACTIVE_VIEW_STATUSES, review=False
            )

        row = view.splitlines()[-1]
        self.assertIn("a \\| b", row)
        cells = re.split(r"(?<!\\)\|", row.strip())[1:-1]
        self.assertEqual(len(cells), 6, row)


class RetiredListGateTest(unittest.TestCase):
    def test_a_stale_list_row_without_cards_does_not_block_completion(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            stage_root = root / ".stage"
            (stage_root / "work").mkdir(parents=True)
            (stage_root / "settings.json").write_text(
                '{"schema_version": 5}\n', encoding="utf-8"
            )
            (stage_root / "work" / "active.md").write_text(
                "| Work | Status |\n|---|---|\n| W-00000001 | active |\n",
                encoding="utf-8",
            )
            (stage_root / "work" / "review.md").write_text(
                "| Work | Status |\n|---|---|\n| W-00000002 | completed |\n",
                encoding="utf-8",
            )

            blockers = stage_work.stage_completion_blockers(root)

        self.assertEqual(blockers, [])

    def test_a_legacy_v3_list_row_without_cards_still_blocks(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            work = root / ".stage" / "present" / "work"
            work.mkdir(parents=True)
            (work / "active.md").write_text(
                "| Work | Status |\n|---|---|\n| W-00000001 | active |\n",
                encoding="utf-8",
            )

            blockers = stage_work.stage_completion_blockers(root)

        self.assertTrue(any("active.md" in blocker for blocker in blockers), blockers)


if __name__ == "__main__":
    unittest.main()
