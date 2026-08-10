"""Venue execution directions in the session-start context."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parents[1]
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

import stage_context  # noqa: E402


class SessionContextVenueTest(unittest.TestCase):
    def test_routing_line_tells_each_venue_how_to_run_and_names_the_procedure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = root / ".stage"
            (stage_root / "present" / "work" / "items").mkdir(parents=True)
            (stage_root / "settings.json").write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "venue_routing": {
                            "design": "claude",
                            "development": "codex",
                        },
                    }
                ),
                encoding="utf-8",
            )

            context = stage_context.session_context(root)

        routing_line = next(
            line for line in context.splitlines() if line.startswith("- Venue routing")
        )
        self.assertIn("spawn a teammate agent for `claude`-venue work", routing_line)
        self.assertIn("hand `codex`-venue work to the driver", routing_line)
        self.assertIn("read `.stage/operations/claude-venue.md`", routing_line)


if __name__ == "__main__":
    unittest.main()
