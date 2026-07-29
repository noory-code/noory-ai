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
    def test_record_paths_scan_nested_markdown_records_in_sorted_order(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "W-00000002.md").write_text("", encoding="utf-8")
            (root / "W-00000001.md").write_text("", encoding="utf-8")
            (root / "ignored.txt").write_text("", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            story = nested / "_story.md"
            story.write_text("---\nid: W-00000003\n---\n", encoding="utf-8")

            self.assertEqual(
                [
                    root / "W-00000001.md",
                    root / "W-00000002.md",
                    story,
                ],
                list(stage_record_paths.record_paths(root)),
            )
            self.assertEqual(
                [
                    root / "W-00000001.md",
                    root / "W-00000002.md",
                    story,
                ],
                list(stage_record_paths.record_paths(root, pattern="W-*.md")),
            )
            self.assertEqual([], list(stage_record_paths.record_paths(root / "missing")))

    def test_record_paths_recursion_is_boundary_policy_not_a_caller_choice(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        with self.assertRaises(TypeError):
            stage_record_paths.record_paths(Path("work/current"), recursive=True)

    def test_record_path_finds_flat_and_hierarchical_records_by_frontmatter_id(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            flat = root / "W-00000001.md"
            story = root / "S-01-story"
            story.mkdir()
            nested = story / "_story.md"
            flat.write_text("---\nid: W-00000001\n---\n", encoding="utf-8")
            nested.write_text("---\nid: W-00000002\n---\n", encoding="utf-8")

            self.assertEqual(flat, stage_record_paths.record_path(root, "W-00000001"))
            self.assertEqual(nested, stage_record_paths.record_path(root, "W-00000002"))
            self.assertEqual(
                root / "W-00000003.md",
                stage_record_paths.record_path(root, "W-00000003"),
            )

    def test_top_level_item_path_keeps_a_hierarchy_together(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        root = Path("work/current")
        action = root / "E-01-epic/S-01-story/A-01-action.md"
        self.assertEqual(
            root / "E-01-epic",
            stage_record_paths.top_level_item_path(root, action),
        )
        flat = root / "W-00000001.md"
        self.assertEqual(flat, stage_record_paths.top_level_item_path(root, flat))

    def test_work_record_scale_rejects_the_retired_flat_shape(self):
        stage_record_paths = importlib.import_module("stage_record_paths")
        root = Path("work/current")
        with self.assertRaisesRegex(ValueError, "no valid epic/story/action"):
            stage_record_paths.work_record_scale(root, root / "W-00000001.md")

    def test_record_path_consumers_do_not_own_markdown_record_scans(self):
        production_roots = (HOOKS, STAGE / "scripts", STAGE / "skills")
        consumers = sorted(
            path
            for source_root in production_roots
            for path in source_root.rglob("*.py")
            if "tests" not in path.parts
            and path.name != "stage_record_paths.py"
        )
        direct_scan = re.compile(
            r"\.(?:r?glob)\((?:f)?[\"'][^\"']*\.md[\"']\)"
        )
        temporary_non_work_exceptions = {
            HOOKS / "stage_runtime.py": {
                '.glob("*.md")',
            },
            STAGE / "scripts" / "guidance_docs.py": {
                '.rglob("*.md")',
            },
            STAGE / "scripts" / "migrate_stage.py": {
                '.glob("*.md")',
                '.glob("B-*.md")',
            },
            STAGE / "scripts" / "stage_schema_v4_migration.py": {
                '.glob("*/index.md")',
            },
            STAGE / "scripts" / "stage_schema_v5_migration.py": {
                '.glob("W-*.md")',
            },
        }
        for path in consumers:
            with self.subTest(path=path):
                matches = {
                    match.group(0)
                    for match in direct_scan.finditer(path.read_text(encoding="utf-8"))
                }
                self.assertEqual(
                    temporary_non_work_exceptions.get(path, set()),
                    matches,
                    f"{path} owns a Markdown record scan outside the filesystem boundary",
                )


if __name__ == "__main__":
    unittest.main()
