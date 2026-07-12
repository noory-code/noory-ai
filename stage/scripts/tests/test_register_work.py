from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-work" / "register_work.py"

ACTIVE = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
)


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


class RegisterWorkTest(unittest.TestCase):
    def make(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/present/work/items").mkdir(parents=True)
        (root / ".stage/past/work/archive/items").mkdir(parents=True)
        (root / ".stage/present/work/active.md").write_text(ACTIVE, encoding="utf-8")
        return tmp, root

    def test_auto_id_and_link_row(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "--title", "Do a thing", "--kind", "feature", "--scope", "stage/x", "--venue", "claude")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = root / ".stage/present/work/items/W-00000001.md"
            self.assertTrue(item.exists())
            body = item.read_text(encoding="utf-8")
            self.assertIn("id: W-00000001", body)
            self.assertIn("kind: feature", body)
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            self.assertIn("[items/W-00000001.md](items/W-00000001.md)", active)

    def test_increments_past_max_including_archive(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/past/work/archive/items/W-00000005.md").write_text("---\nid: W-00000005\n---\n", encoding="utf-8")
            run(root, "--title", "A", "--kind", "chore", "--scope", "x")
            self.assertTrue((root / ".stage/present/work/items/W-00000006.md").exists())

    def test_reruns_reconcile_index_not_duplicate(self):
        tmp, root = self.make()
        with tmp:
            run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            # Drop the row, then a re-run with same id must re-add exactly one.
            (root / ".stage/present/work/active.md").write_text(ACTIVE, encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            self.assertEqual(active.count("[items/W-00000001.md]"), 1)

    def test_refuses_archived_id(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/past/work/archive/items/W-00000003.md").write_text("---\nid: W-00000003\n---\n", encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000003")
            self.assertEqual(proc.returncode, 1)
            self.assertFalse((root / ".stage/present/work/items/W-00000003.md").exists())


if __name__ == "__main__":
    unittest.main()
