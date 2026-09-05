from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PLUGIN_ROOT / "scripts" / "build_styles.py"


class BuildStylesTest(unittest.TestCase):
    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUILDER), "--check"],
            capture_output=True,
            text=True,
        )

    def test_committed_styles_match_their_sources(self) -> None:
        result = self.run_check()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_reports_a_source_edit_that_never_reached_the_shipped_files(self) -> None:
        # The shipped files are committed rather than composed at load time, so a source edit that
        # nobody rebuilt would ship the old text with no other signal.
        source = PLUGIN_ROOT / "styles" / "fixed-rules.md"
        original = source.read_text(encoding="utf-8")
        try:
            source.write_text(original + "\nAn edit nobody rebuilt.\n", encoding="utf-8")
            result = self.run_check()
        finally:
            source.write_text(original, encoding="utf-8")

        self.assertEqual(result.returncode, 1)
        self.assertIn("stale:", result.stdout)


if __name__ == "__main__":
    unittest.main()
