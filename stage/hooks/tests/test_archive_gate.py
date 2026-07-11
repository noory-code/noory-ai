# Locks the one-gate archive contract: `.stage/past/work/archive` writes are
# authorized by an archive intent alone. `.stage/` is excluded from
# is_source_path, so the registration and commit gates never fire on it — no
# work item is required to archive. Regression guard for the false "two gates"
# belief that once spawned a spurious archive work item.
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)

ARCHIVE_PATHS = [
    ".stage/past/work/archive/items/W-00000001.md",
    ".stage/past/work/archive/retrospectives/R-00000001.md",
    ".stage/past/work/archive/index.md",
]


class ArchiveGateTest(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage").mkdir()
        return tmp, root

    def test_archive_targets_are_not_source(self):
        tmp, root = self.make_root()
        with tmp:
            for path in ARCHIVE_PATHS:
                self.assertFalse(
                    stage_guard.is_source_path(path, root, True),
                    f"{path} must not be governed source",
                )
                self.assertFalse(stage_guard.is_source_path(path, root, False), path)

    def test_no_registration_gate_on_archive_without_work_item(self):
        tmp, root = self.make_root()
        with tmp:
            # No work items exist at all — the registration gate must still pass.
            self.assertEqual(stage_guard.source_registration_blocker(root, ARCHIVE_PATHS, True), "")
            self.assertEqual(stage_guard.commit_blocker(root, ARCHIVE_PATHS), "")


if __name__ == "__main__":
    unittest.main()
