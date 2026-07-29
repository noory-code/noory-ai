from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


_PATHS = Path(__file__).resolve().parents[1] / "stage_paths.py"
if str(_PATHS.parent) not in sys.path:
    sys.path.insert(0, str(_PATHS.parent))
_SPEC = importlib.util.spec_from_file_location("executor_stage_paths", _PATHS)
stage_paths = importlib.util.module_from_spec(_SPEC)
sys.modules["executor_stage_paths"] = stage_paths
assert _SPEC.loader is not None
_SPEC.loader.exec_module(stage_paths)


class ExecutorConfigTest(unittest.TestCase):
    def test_loads_review_sibling_executors_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp) / ".stage"
            stage_root.mkdir()
            (stage_root / "settings.json").write_text(
                json.dumps(
                    {
                        "schema_version": 5,
                        "review": {"reviewers": {"claude": "echo APPROVED"}},
                        "executors": {"codex": "true"},
                    }
                ),
                encoding="utf-8",
            )

            executors = stage_paths.load_executors_config(stage_root)

        self.assertEqual({"codex": "true"}, executors)

    def test_resolves_executor_for_item_venue(self):
        self.assertEqual(
            ("run-codex", ""),
            stage_paths.resolve_executor_command({"codex": "run-codex"}, "codex"),
        )

    def test_missing_executor_fails_closed(self):
        command, error = stage_paths.resolve_executor_command(
            {"claude": "run-claude"}, "codex"
        )

        self.assertIsNone(command)
        self.assertIn("executors.codex", error)

    def test_malformed_executors_fail_closed(self):
        for executors in (None, "codex", {"codex": ""}, {"codex": 5}):
            with self.subTest(executors=executors):
                command, error = stage_paths.resolve_executor_command(
                    executors, "codex"
                )
                self.assertIsNone(command)
                self.assertTrue(error)


if __name__ == "__main__":
    unittest.main()
