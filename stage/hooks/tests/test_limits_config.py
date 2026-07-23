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
_SPEC = importlib.util.spec_from_file_location("limits_stage_paths", _PATHS)
stage_paths = importlib.util.module_from_spec(_SPEC)
sys.modules["limits_stage_paths"] = stage_paths
assert _SPEC.loader is not None
_SPEC.loader.exec_module(stage_paths)


class LoadLimitsConfigTest(unittest.TestCase):
    def write_settings(self, stage_root: Path, data: object) -> None:
        stage_root.mkdir(parents=True)
        (stage_root / "settings.json").write_text(json.dumps(data), encoding="utf-8")

    def test_valid_limits_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp) / ".stage"
            limits = {
                "max_attempts_per_item": 3,
                "max_iterations": 100,
                "max_wall_clock_seconds": 3600,
            }
            self.write_settings(stage_root, {"schema_version": 4, "limits": limits})

            self.assertEqual(stage_paths.load_limits_config(stage_root), (limits, ""))

    def test_malformed_limits_fail_closed(self):
        malformed = (
            "unlimited",
            {"max_attempts_per_item": 0, "max_iterations": 100, "max_wall_clock_seconds": 3600},
            {"max_attempts_per_item": 3, "max_iterations": True, "max_wall_clock_seconds": 3600},
            {"max_attempts_per_item": 3, "max_iterations": 100},
            {
                "max_attempts_per_item": 3,
                "max_iterations": 100,
                "max_wall_clock_seconds": 3600,
                "max_tokens": 1000,
            },
        )
        for limits in malformed:
            with self.subTest(limits=limits), tempfile.TemporaryDirectory() as tmp:
                stage_root = Path(tmp) / ".stage"
                self.write_settings(stage_root, {"schema_version": 4, "limits": limits})

                parsed, error = stage_paths.load_limits_config(stage_root)

                self.assertIsNone(parsed)
                self.assertTrue(error)


if __name__ == "__main__":
    unittest.main()
