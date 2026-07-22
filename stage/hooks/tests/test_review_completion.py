# A work item that DECLARES review: pending cannot be completed until review:
# passed — item_completion_blockers (which the commit gate + audit run) flags it,
# so hand-editing status: completed without doing the review is blocked. An item
# that never asks for review (absent -> not_required) completes freely.
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest

_HOOKS = Path(__file__).resolve().parents[1]
for _n in ("stage_paths", "stage_shell", "stage_git", "stage_work"):
    _s = importlib.util.spec_from_file_location(_n, _HOOKS / f"{_n}.py")
    _m = importlib.util.module_from_spec(_s)
    sys.modules[_n] = _m
    assert _s.loader is not None
    _s.loader.exec_module(_m)
stage_work = sys.modules["stage_work"]


def item(review: str, *, autonomous: bool = False) -> object:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "W-00000001.md"
        return stage_work.item_from_fields(
            path,
            {
                "id": "W-00000001",
                "status": "completed",
                "verification": "passed",
                "retrospective": "completed",
                "promotion": "not_applicable",
                "review": review,
                "autonomous": autonomous,
            },
            stage_work.AUDIT_FIELD_DEFAULTS,
        )


class ReviewCompletionTest(unittest.TestCase):
    def test_pending_review_blocks_completion(self):
        blockers = stage_work.item_completion_blockers(item("pending"))
        self.assertTrue(any("review" in b for b in blockers), blockers)

    def test_passed_review_allows_completion(self):
        self.assertEqual(stage_work.item_completion_blockers(item("passed")), [])

    def test_not_required_allows_completion(self):
        self.assertEqual(stage_work.item_completion_blockers(item("not_required")), [])

    def test_autonomous_item_requires_passed_independent_review(self):
        blockers = stage_work.item_completion_blockers(
            item("not_required", autonomous=True)
        )

        self.assertTrue(any("independent review" in blocker for blocker in blockers), blockers)

    def test_autonomous_item_with_passed_review_allows_completion(self):
        self.assertEqual(
            stage_work.item_completion_blockers(item("passed", autonomous=True)), []
        )


if __name__ == "__main__":
    unittest.main()
