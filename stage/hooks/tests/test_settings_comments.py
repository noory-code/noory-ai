from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))
SPEC = importlib.util.spec_from_file_location(
    "settings_comments_stage_paths", HOOKS_DIR / "stage_paths.py"
)
stage_paths = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage_paths)


class SettingsCommentsTest(unittest.TestCase):
    def test_jsonc_comments_are_removed_without_touching_comment_markers_in_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp)
            settings_path = stage_root / "settings.jsonc"
            settings_path.write_text(
                """
{
  // This comment describes the schema marker.
  "schema_version": 4,
  /* Comment markers inside strings are data, not comments. */
  "url": "https://example.com/stage/*/settings",
  "path": "C://stage//settings"
}
""".lstrip(),
                encoding="utf-8",
            )

            resolved_path, settings, error = stage_paths.read_settings(stage_root)

        self.assertEqual(settings_path, resolved_path)
        self.assertIsNone(error)
        self.assertEqual("https://example.com/stage/*/settings", settings["url"])
        self.assertEqual("C://stage//settings", settings["path"])

    def test_legacy_settings_json_remains_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp)
            settings_path = stage_root / "settings.json"
            settings_path.write_text('{"schema_version": 4}\n', encoding="utf-8")

            resolved_path, settings, error = stage_paths.read_settings(stage_root)

        self.assertEqual(settings_path, resolved_path)
        self.assertIsNone(error)
        self.assertEqual({"schema_version": 4}, settings)

    def test_both_settings_names_fail_instead_of_selecting_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp)
            (stage_root / "settings.json").write_text(
                '{"schema_version": 4}\n', encoding="utf-8"
            )
            (stage_root / "settings.jsonc").write_text(
                '{"schema_version": 4}\n', encoding="utf-8"
            )

            _resolved_path, settings, error = stage_paths.read_settings(stage_root)

        self.assertIsNone(settings)
        self.assertIsInstance(error, FileExistsError)
        self.assertIn("settings.json", str(error))
        self.assertIn("settings.jsonc", str(error))


if __name__ == "__main__":
    unittest.main()
