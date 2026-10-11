"""Protect attribution and original text before testing model interpretation."""
import copy
import json
from pathlib import Path
import unittest

from split_profile_lab import preserve_records, validate_split

ROOT = Path(__file__).resolve().parent


class SplitLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = json.loads((ROOT / "split-fixtures.json").read_text())["bundles"][3]

    def test_mixed_owner_is_rejected_before_analysis(self) -> None:
        self.bundle["records"][0]["owner_id"] = "fictional-L"
        with self.assertRaisesRegex(ValueError, "owner"):
            preserve_records(self.bundle)

    def test_quote_and_unknown_speaker_remain_distinct(self) -> None:
        records = preserve_records(self.bundle)
        self.assertEqual(records[1]["speaker"], "quoted_colleague")
        self.assertEqual(records[2]["speaker"], "unknown")
        self.assertEqual(records, self.bundle["records"])
        self.bundle["records"][2]["speaker"] = "user"
        self.assertEqual(records[2]["speaker"], "unknown")

    def test_duplicate_ids_and_unrecognized_speakers_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.bundle)
        duplicate["records"][1]["id"] = duplicate["records"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            preserve_records(duplicate)
        self.bundle["records"][0]["speaker"] = "maybe-user"
        with self.assertRaisesRegex(ValueError, "speaker"):
            preserve_records(self.bundle)

    def test_original_whitespace_and_quotes_are_not_rewritten(self) -> None:
        original = '  "그렇게 하죠"\n두 번째 줄\t끝  '
        self.bundle["records"][0]["text"] = original
        self.assertEqual(preserve_records(self.bundle)[0]["text"], original)

    def test_unknown_or_other_owner_reference_fails(self) -> None:
        card = {"owner_id": "fictional-P", "language": "ko",
                "interpretation": {"text": "범위를 살펴봐요.", "evidence_ids": ["L1"]},
                "alternative": "다른 조건도 있을 수 있어요.", "limitation": "다음 결정은 몰라요."}
        self.assertTrue(validate_split(card, self.bundle))
        card["interpretation"]["evidence_ids"] = ["P1", "P4"]
        self.assertEqual(validate_split(card, self.bundle), [])


if __name__ == "__main__":
    unittest.main()
