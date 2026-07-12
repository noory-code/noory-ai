# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stage_paths = load_module("stage_paths", HOOKS_DIR / "stage_paths.py")
stage_context = load_module("stage_context", HOOKS_DIR / "stage_context.py")


class LoadLanguageTest(unittest.TestCase):
    def make_stage(self, settings) -> Path:
        tmp = Path(tempfile.mkdtemp())
        stage_root = tmp / ".stage"
        stage_root.mkdir()
        if settings is not None:
            (stage_root / "settings.json").write_text(
                json.dumps(settings) if not isinstance(settings, str) else settings,
                encoding="utf-8",
            )
        return stage_root

    def test_missing_settings_falls_back_to_english(self):
        self.assertEqual("en", stage_paths.load_language(self.make_stage(None)))

    def test_missing_key_falls_back_to_english(self):
        self.assertEqual("en", stage_paths.load_language(self.make_stage({"schema_version": 2})))

    def test_valid_tag_is_returned(self):
        self.assertEqual("ko", stage_paths.load_language(self.make_stage({"language": "ko"})))
        self.assertEqual(
            "pt-br", stage_paths.load_language(self.make_stage({"language": "pt-br"}))
        )

    def test_malformed_values_fall_open_to_english(self):
        for bad in ("KO", "toolongprimarysubtag", "ko_KR", "", 3, True, ["ko"]):
            with self.subTest(value=bad):
                self.assertEqual(
                    "en", stage_paths.load_language(self.make_stage({"language": bad}))
                )

    def test_unreadable_settings_falls_back_to_english(self):
        self.assertEqual("en", stage_paths.load_language(self.make_stage("{not json")))


class SummaryLanguageTest(unittest.TestCase):
    def make_project(self, language) -> Path:
        tmp = Path(tempfile.mkdtemp())
        stage_root = tmp / ".stage"
        (stage_root / "present" / "work" / "items").mkdir(parents=True)
        settings = {"schema_version": 2}
        if language is not None:
            settings["language"] = language
        (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        return stage_root

    def test_english_summary_by_default(self):
        summary = stage_context.summarize_stage(self.make_project(None))
        self.assertIn("# Stage Session Summary", summary)
        self.assertIn("Open work: none", summary)

    def test_korean_summary_labels(self):
        summary = stage_context.summarize_stage(self.make_project("ko"))
        self.assertIn("# Stage 세션 요약", summary)
        self.assertIn("진행 중 작업: 없음", summary)
        self.assertNotIn("Open work", summary)

    def test_unknown_tag_falls_back_to_english_labels(self):
        summary = stage_context.summarize_stage(self.make_project("fr"))
        self.assertIn("# Stage Session Summary", summary)


class ContextDirectiveTest(unittest.TestCase):
    def make_workspace(self, language) -> Path:
        tmp = Path(tempfile.mkdtemp())
        stage_root = tmp / ".stage"
        (stage_root / "present" / "work" / "items").mkdir(parents=True)
        settings = {"schema_version": 2}
        if language is not None:
            settings["language"] = language
        (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        return tmp

    def test_non_english_language_injects_directive(self):
        context = stage_context.session_context(self.make_workspace("ko"))
        self.assertIn("Stage document language: `ko`", context)
        self.assertIn("frontmatter keys and enum values", context)

    def test_english_injects_no_directive(self):
        context = stage_context.session_context(self.make_workspace(None))
        self.assertNotIn("Stage document language", context)
        context = stage_context.session_context(self.make_workspace("en"))
        self.assertNotIn("Stage document language", context)


if __name__ == "__main__":
    unittest.main()
