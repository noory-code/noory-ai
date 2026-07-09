# The CLI must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as the scripts.
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_PATH = Path(__file__).resolve().parents[1] / "promote_intent.py"


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), "--project-root", str(project_root), *args],
        capture_output=True,
        text=True,
        check=True,
    )


class PromoteIntentCliTest(unittest.TestCase):
    def make_stage(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage").mkdir()
        return tmp, root

    def test_writes_one_intent_file_per_path(self):
        tmp, root = self.make_stage()
        with tmp:
            run_cli(
                root,
                "--work-item", "W-0001",
                "--path", ".stage/past/canon/principles.md",
                "--path", ".stage/past/canon/vocabulary.md",
            )

            files = sorted(path.name for path in (root / ".stage/.runtime/intents").glob("*.json"))

        self.assertEqual(len(files), 2)
        self.assertTrue(any("principles" in name for name in files))
        self.assertTrue(any("vocabulary" in name for name in files))

    def test_replanting_same_item_and_path_is_idempotent(self):
        tmp, root = self.make_stage()
        with tmp:
            for _ in range(2):
                run_cli(root, "--work-item", "W-0001", "--path", ".stage/past/canon/principles.md")

            files = list((root / ".stage/.runtime/intents").glob("*.json"))

        self.assertEqual(len(files), 1)

    def test_different_items_covering_same_path_get_distinct_slots(self):
        tmp, root = self.make_stage()
        with tmp:
            run_cli(root, "--work-item", "W-0001", "--path", ".stage/past/canon/principles.md")
            run_cli(root, "--work-item", "W-0002", "--path", ".stage/past/canon/principles.md")

            files = list((root / ".stage/.runtime/intents").glob("*.json"))

        self.assertEqual(len(files), 2)


if __name__ == "__main__":
    unittest.main()
