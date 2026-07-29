from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[1]
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

import stage_work  # noqa: E402


def write_card(
    stage_root: Path,
    zone: str,
    item_id: str,
    status: str,
    *,
    parent: str = "",
    scale: str = "story",
) -> None:
    if parent:
        path = stage_root / zone / parent / item_id / "_story.md"
    else:
        record_name = "_epic.md" if scale == "epic" else "_story.md"
        path = stage_root / zone / item_id / record_name
    path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle = ""
    if status == "completed":
        lifecycle = (
            "verification: passed\n"
            "retrospective: completed\n"
            "promotion: not_applicable\n"
        )
    path.write_text(
        f"---\nid: {item_id}\nstatus: {status}\n{lifecycle}---\n",
        encoding="utf-8",
    )


class ParentCompletionTest(unittest.TestCase):
    def make_stage(self) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage_root = root / ".stage"
        stage_root.mkdir()
        (stage_root / "settings.json").write_text(
            '{"schema_version": 5}\n', encoding="utf-8"
        )
        write_card(
            stage_root,
            "work/current",
            "W-00000001",
            "completed",
            scale="epic",
        )
        return tmp, root, stage_root

    def test_active_child_blocks_parent_completion(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            write_card(
                stage_root,
                "work/current",
                "W-00000002",
                "active",
                parent="W-00000001",
            )

            blockers = stage_work.stage_completion_blockers(root)

        self.assertTrue(any("W-00000002" in blocker for blocker in blockers), blockers)
        self.assertTrue(any("active" in blocker for blocker in blockers), blockers)

    def test_planned_child_blocks_planned_parent_completion(self):
        tmp, _, stage_root = self.make_stage()
        with tmp:
            write_card(
                stage_root,
                "work/planned",
                "W-00000010",
                "selected",
                scale="epic",
            )
            write_card(
                stage_root,
                "work/planned",
                "W-00000011",
                "captured",
                parent="W-00000010",
            )
            items = stage_work.load_all_work_items(stage_root)
            blockers = stage_work.parent_completion_blockers("W-00000010", items)

        self.assertTrue(any("W-00000011" in blocker for blocker in blockers), blockers)
        self.assertTrue(any("captured" in blocker for blocker in blockers), blockers)

    def test_hierarchical_planned_child_blocks_parent_completion_without_parent_field(self):
        tmp, _, stage_root = self.make_stage()
        with tmp:
            parent_dir = stage_root / "work/planned/W-00000010"
            parent_dir.mkdir(parents=True)
            (parent_dir / "_epic.md").write_text(
                "---\nid: W-00000010\nstatus: selected\n---\n",
                encoding="utf-8",
            )
            story_dir = stage_root / "work/planned/W-00000010/W-00000011"
            story_dir.mkdir(parents=True)
            (story_dir / "_story.md").write_text(
                "---\nid: W-00000011\nstatus: captured\n---\n",
                encoding="utf-8",
            )

            items = stage_work.load_all_work_items(stage_root)
            blockers = stage_work.parent_completion_blockers("W-00000010", items)

        self.assertTrue(any("W-00000011" in blocker for blocker in blockers), blockers)
        self.assertTrue(any("captured" in blocker for blocker in blockers), blockers)

    def test_archived_and_rejected_children_are_terminal(self):
        tmp, _, stage_root = self.make_stage()
        with tmp:
            write_card(
                stage_root,
                "work/current",
                "W-00000002",
                "completed",
                parent="W-00000001",
            )
            write_card(
                stage_root,
                "work/current",
                "W-00000003",
                "rejected",
                parent="W-00000001",
            )
            items = stage_work.load_all_work_items(stage_root)

            self.assertTrue(stage_work.children_are_terminal("W-00000001", items))
            self.assertEqual(
                stage_work.non_terminal_children("W-00000001", items), []
            )

    def test_rejected_planned_child_is_terminal(self):
        tmp, _, stage_root = self.make_stage()
        with tmp:
            write_card(
                stage_root,
                "work/planned",
                "W-00000010",
                "selected",
                scale="epic",
            )
            write_card(
                stage_root,
                "work/planned",
                "W-00000011",
                "rejected",
                parent="W-00000010",
            )
            items = stage_work.load_all_work_items(stage_root)

            self.assertTrue(stage_work.children_are_terminal("W-00000010", items))

    def test_leaf_item_is_unaffected(self):
        tmp, root, stage_root = self.make_stage()
        with tmp:
            items = stage_work.load_all_work_items(stage_root)

            self.assertTrue(stage_work.children_are_terminal("W-00000001", items))
            self.assertEqual(stage_work.stage_completion_blockers(root), [])

    def test_planned_index_is_not_loaded_as_a_work_item(self):
        tmp, _, stage_root = self.make_stage()
        with tmp:
            index = stage_root / "work/planned/index.md"
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_text("# Planned work\n", encoding="utf-8")

            items = stage_work.load_all_work_items(stage_root)

        self.assertNotIn("index", {item.item_id for item in items})


if __name__ == "__main__":
    unittest.main()
