"""Dormant schema-v4 template tree contract."""

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
V3_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
V4_ROOT = PLUGIN_ROOT / "templates" / "v4" / "project-stage"
V4_LOCALE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "locales" / "ko"

EXTRA_V4_FILES = {
    Path("decisions/index.md"),
    Path("roadmap/milestones/index.md"),
    Path("roadmap/themes/index.md"),
}


def v4_path(relative: Path) -> Path:
    """Map one schema-v3 template path to its schema-v4 destination."""
    value = relative.as_posix()
    relocations = (
        ("past/canon", "official/canon"),
        ("past/model", "official/model"),
        ("past/decisions", "official/decisions"),
        ("past/work/archive", "official/work/archive"),
        ("present/work/items", "work/current"),
        ("present/work/decisions", "decisions/pending"),
        ("present/work/retrospectives", "work/retrospectives"),
        ("present/work/active.md", "work/active.md"),
        ("present/work/review.md", "work/review.md"),
        ("present/state", "state"),
        ("future/backlog/items", "work/planned"),
        ("future/backlog/index.md", "work/planned/index.md"),
        ("future/backlog/views", "work/views"),
        ("future/proposals", "proposals"),
        ("future/roadmap", "roadmap"),
    )
    for source, destination in relocations:
        if value == source or value.startswith(f"{source}/"):
            return Path(f"{destination}{value[len(source):]}")
    return relative


def frontmatter_keys(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return []
    keys = []
    for line in lines[1:]:
        if line == "---":
            break
        keys.append(line.split(":", 1)[0])
    return keys


class TemplateV4Test(unittest.TestCase):
    def files_under(self, root: Path) -> set[Path]:
        return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}

    def test_v4_tree_mirrors_v3_file_set_under_renamed_roots(self):
        expected = {v4_path(path) for path in self.files_under(V3_ROOT)} | EXTRA_V4_FILES
        self.assertEqual(expected, self.files_under(V4_ROOT))

    def test_v4_tree_is_dormant_and_v3_operations_are_verbatim(self):
        from stage.scripts import init_stage

        self.assertEqual(V3_ROOT, init_stage.TEMPLATE_ROOT)
        self.assertNotEqual(V4_ROOT, init_stage.TEMPLATE_ROOT)
        self.assertFalse(V4_ROOT.is_relative_to(init_stage.TEMPLATE_ROOT))
        self.assertEqual(
            (V3_ROOT / "operations/verification.md").read_bytes(),
            (V4_ROOT / "operations/verification.md").read_bytes(),
        )

    def test_v4_settings_marker_is_bundled_without_cutting_over_init(self):
        settings = json.loads((V4_ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(4, settings["schema_version"])
        v3_settings = json.loads((V3_ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(3, v3_settings["schema_version"])

    def test_roadmap_templates_have_computed_status_contract(self):
        theme = V4_ROOT / "roadmap/themes/_template.md"
        milestone = V4_ROOT / "roadmap/milestones/_template.md"
        self.assertEqual(["id", "decision_refs"], frontmatter_keys(theme))
        self.assertEqual(["id", "theme", "decision_refs"], frontmatter_keys(milestone))
        self.assertIn("id: TH-00000000", theme.read_text(encoding="utf-8"))
        self.assertIn("id: M-00000000", milestone.read_text(encoding="utf-8"))
        for template in (theme, milestone):
            text = template.read_text(encoding="utf-8")
            self.assertNotIn("status:", text.lower())
            self.assertNotIn("## Status", text)

    def test_roadmap_families_and_pending_decisions_have_indexes(self):
        for relative in EXTRA_V4_FILES:
            with self.subTest(file=str(relative)):
                self.assertTrue((V4_ROOT / relative).is_file())
                self.assertTrue((V4_LOCALE_ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
