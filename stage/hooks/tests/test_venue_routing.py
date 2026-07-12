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


class LoadVenueRoutingTest(unittest.TestCase):
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

    def test_missing_settings_or_key_yields_empty(self):
        self.assertEqual({}, stage_paths.load_venue_routing(self.make_stage(None)))
        self.assertEqual(
            {}, stage_paths.load_venue_routing(self.make_stage({"schema_version": 2}))
        )

    def test_declared_routing_is_returned_normalized(self):
        routing = stage_paths.load_venue_routing(
            self.make_stage({"venue_routing": {"Design": " claude ", "development": "codex"}})
        )
        self.assertEqual({"design": "claude", "development": "codex"}, routing)

    def test_malformed_entries_fall_open_to_empty_or_partial(self):
        self.assertEqual(
            {}, stage_paths.load_venue_routing(self.make_stage({"venue_routing": ["design"]}))
        )
        routing = stage_paths.load_venue_routing(
            self.make_stage({"venue_routing": {"design": "claude", "fix": 3, "": "codex"}})
        )
        self.assertEqual({"design": "claude"}, routing)

    def test_unreadable_settings_yields_empty(self):
        self.assertEqual({}, stage_paths.load_venue_routing(self.make_stage("{not json")))


class ContextRoutingTest(unittest.TestCase):
    def make_workspace(self, routing) -> Path:
        tmp = Path(tempfile.mkdtemp())
        stage_root = tmp / ".stage"
        (stage_root / "present" / "work" / "items").mkdir(parents=True)
        settings = {"schema_version": 2}
        if routing is not None:
            settings["venue_routing"] = routing
        (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        return tmp

    def test_declared_routing_is_injected_with_behavior_rules(self):
        context = stage_context.session_context(
            self.make_workspace({"design": "claude", "development": "codex"})
        )
        self.assertIn("design -> claude", context)
        self.assertIn("development -> codex", context)
        self.assertIn("do not ask the human during normal routing", context)
        self.assertIn("Split mixed design+implementation work", context)

    def test_no_routing_injects_nothing(self):
        context = stage_context.session_context(self.make_workspace(None))
        self.assertNotIn("Venue routing", context)
        context = stage_context.session_context(self.make_workspace({}))
        self.assertNotIn("Venue routing", context)


if __name__ == "__main__":
    unittest.main()
