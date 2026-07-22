from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOOKS))
import stage_work  # noqa: E402


class WorkAcceptanceTest(unittest.TestCase):
    def test_parser_reads_autonomous_and_acceptance_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "W-00000001.md"
            path.write_text(
                "---\n"
                "id: W-00000001\n"
                "venue: codex\n"
                "autonomous: true\n"
                "acceptance:\n"
                '  - "python3 -c \\"print(1)\\""\n'
                "  - 'python3 -m unittest discover -s tests -q'\n"
                "---\n",
                encoding="utf-8",
            )

            fields = stage_work.parse_frontmatter(path)
            item = stage_work.item_from_fields(
                path, fields, stage_work.GATE_FIELD_DEFAULTS
            )

        self.assertTrue(item.autonomous)
        self.assertEqual("codex", item.venue)
        self.assertEqual(
            (
                'python3 -c "print(1)"',
                "python3 -m unittest discover -s tests -q",
            ),
            item.acceptance,
        )

    def test_absent_fields_default_to_non_autonomous_without_acceptance(self):
        path = Path("W-00000001.md")
        item = stage_work.item_from_fields(
            path, {"id": "W-00000001"}, stage_work.GATE_FIELD_DEFAULTS
        )

        self.assertFalse(item.autonomous)
        self.assertEqual((), item.acceptance)
        self.assertEqual("", item.venue)


if __name__ == "__main__":
    unittest.main()
