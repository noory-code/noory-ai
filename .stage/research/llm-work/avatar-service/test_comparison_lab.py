"""Check attribution before rendering a model-selected comparison."""
import copy
import json
from pathlib import Path
import unittest

from comparison_lab import render_typed, validate_typed

ROOT = Path(__file__).resolve().parent


class ComparisonLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = json.loads((ROOT / "split-fixtures.json").read_text())["bundles"][3]
        self.card = {"owner_id": "fictional-P", "language": "ko", "status": "compare",
                     "target": "requested_action", "relation": "different",
                     "evidence_ids": ["P1", "P4"], "question": "어떤 조건을 더 살펴볼까요?"}

    def test_quoted_and_unknown_authors_cannot_become_user_evidence(self) -> None:
        for source_id in ("P2", "P3"):
            with self.subTest(source_id=source_id):
                self.card["evidence_ids"] = ["P1", source_id]
                self.assertTrue(validate_typed(self.card, self.bundle))
                with self.assertRaises(ValueError):
                    render_typed(self.card, self.bundle)

    def test_wrong_owner_unknown_id_and_duplicate_pair_fail(self) -> None:
        for patch in ({"owner_id": "fictional-R"}, {"evidence_ids": ["P1", "R2"]},
                      {"evidence_ids": ["P1", "P1"]}):
            with self.subTest(patch=patch):
                card = {**self.card, **patch}
                self.assertTrue(validate_typed(card, self.bundle))

    def test_abstention_is_distinct_from_an_empty_comparison(self) -> None:
        card = {**self.card, "status": "insufficient", "target": "none", "relation": "none",
                "evidence_ids": [], "question": ""}
        self.assertEqual(validate_typed(card, self.bundle), [])
        self.assertEqual(render_typed(card, self.bundle)["records"], [])
        card["target"] = "user_wording"
        self.assertTrue(validate_typed(card, self.bundle))

    def test_render_uses_complete_original_text_including_negation(self) -> None:
        display = render_typed(self.card, self.bundle)
        self.assertEqual(display["records"], [self.bundle["records"][0], self.bundle["records"][3]])
        self.assertIn("저장하지 말아", display["records"][1]["text"])
        self.bundle["records"][3]["text"] = "changed"
        self.assertIn("저장하지 말아", display["records"][1]["text"])

    def test_unexpected_model_narrative_is_not_displayed(self) -> None:
        card = copy.deepcopy(self.card)
        card["interpretation"] = "저장을 미뤘어요."
        self.assertTrue(validate_typed(card, self.bundle))


if __name__ == "__main__":
    unittest.main()
