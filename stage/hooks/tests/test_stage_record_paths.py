import importlib
import re
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[1]
STAGE = HOOKS.parent
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))


class StageRecordPathsTests(unittest.TestCase):
    def test_record_paths_preserve_flat_sorted_markdown_scan(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "W-00000002.md").write_text("", encoding="utf-8")
            (root / "W-00000001.md").write_text("", encoding="utf-8")
            (root / "ignored.txt").write_text("", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "W-00000003.md").write_text("", encoding="utf-8")

            self.assertEqual(
                [root / "W-00000001.md", root / "W-00000002.md"],
                list(stage_record_paths.record_paths(root)),
            )
            self.assertEqual(
                [root / "W-00000001.md", root / "W-00000002.md"],
                list(stage_record_paths.record_paths(root, pattern="W-*.md")),
            )
            self.assertEqual([], list(stage_record_paths.record_paths(root / "missing")))

    def test_record_paths_support_the_existing_recursive_audit_scan(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "nested"
            nested.mkdir()
            top = root / "W-00000001.md"
            child = nested / "W-00000002.md"
            top.write_text("", encoding="utf-8")
            child.write_text("", encoding="utf-8")

            self.assertEqual(
                [top, child],
                list(stage_record_paths.record_paths(root, recursive=True)),
            )

    def test_record_path_preserves_id_to_markdown_path_assembly(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        root = Path("work/current")
        self.assertEqual(
            Path("work/current/W-00000001.md"),
            stage_record_paths.record_path(root, "W-00000001"),
        )

    def test_decision_consumers_do_not_own_flat_markdown_scans(self):
        consumers = (
            HOOKS / "stage_work.py",
            HOOKS / "stage_context.py",
            STAGE / "scripts" / "stage_records.py",
            STAGE / "scripts" / "audit_stage.py",
            STAGE / "skills" / "stage-roadmap" / "manage_roadmap.py",
        )
        direct_scan = re.compile(r"\.(?:r?glob)\([\"']\*\.md[\"']\)")
        for path in consumers:
            with self.subTest(path=path):
                self.assertIsNone(
                    direct_scan.search(path.read_text(encoding="utf-8")),
                    f"{path} owns a Markdown record scan",
                )


if __name__ == "__main__":
    unittest.main()
