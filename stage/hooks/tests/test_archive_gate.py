# Locks the one-gate archive contract: `.stage/past/work/archive` writes are
# authorized by an archive intent alone. `.stage/` is excluded from
# is_source_path, so the registration and commit gates never fire on it — no
# work item is required to archive. Regression guard for the false "two gates"
# belief that once spawned a spurious archive work item.
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "v4" / "project-stage"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)
import stage_runtime  # noqa: E402

ARCHIVE_PATHS = [
    ".stage/past/work/archive/items/W-00000001.md",
    ".stage/past/work/archive/retrospectives/R-00000001.md",
    ".stage/past/work/archive/index.md",
    ".stage/official/work/archive/items/W-00000001.md",
    ".stage/official/decisions/archive/DE-00000001.md",
    ".stage/official/proposals/archive/P-00000001.md",
    ".stage/official/state/archive/O-00000001.md",
    ".stage/official/state/archive/Q-00000001.md",
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

    def test_all_official_archive_families_use_the_archive_gate(self):
        expected = [path for path in ARCHIVE_PATHS if path.startswith(".stage/official/")]
        self.assertTrue(expected)
        for path in expected:
            with self.subTest(path=path):
                self.assertTrue(stage_guard.path_targets_stage_archive(path))

    def test_record_archive_intent_is_narrow_to_archive_records_and_indexes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            item = stage / "work/current/W-00000001/_story.md"
            item.parent.mkdir(parents=True)
            item.write_text(
                """---
id: W-00000001
title: Close old records
kind: chore
venue: codex
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000001
promotion: not_applicable
promotes:
decision_refs:
---
""",
                encoding="utf-8",
            )
            intent = {"type": "archive", "work_item": "W-00000001"}
            allowed = (
                ".stage/official/decisions/archive/DE-00000001.md",
                ".stage/official/decisions/archive/index.md",
                ".stage/official/proposals/archive/P-00000001.md",
                ".stage/official/proposals/archive/index.md",
                ".stage/official/state/archive/O-00000001.md",
                ".stage/official/state/archive/Q-00000001.md",
                ".stage/official/state/archive/index.md",
            )
            for target in allowed:
                with self.subTest(target=target):
                    self.assertEqual(
                        "",
                        stage_runtime.intent_validation_blocker(
                            stage,
                            root,
                            stage / ".runtime/intents/test.json",
                            intent,
                            [target],
                            {target},
                        ),
                    )

            denied = ".stage/official/decisions/records/DE-00000001.md"
            error = stage_runtime.intent_validation_blocker(
                stage,
                root,
                stage / ".runtime/intents/test.json",
                intent,
                [denied],
                {denied},
            )
            self.assertIn("may only target", error)


if __name__ == "__main__":
    unittest.main()
