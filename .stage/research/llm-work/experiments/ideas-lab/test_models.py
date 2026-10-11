"""비교 기준이 모델 입력에 섞이지 않는지와 응답 채점을 확인합니다."""

import json
import unittest

from run_models import make_prompt, matches, parse_answer


class ModelRecordTests(unittest.TestCase):
    def test_expected_and_scoring_notes_are_not_sent(self) -> None:
        case = {"task": "가능한 행동을 고르세요.", "baseline": {"value": 1},
                "enhanced": {"value": 1, "check": True},
                "expected": {"action": "SECRET_EXPECTED", "targets": []},
                "scoring_note": "PRIVATE_RUBRIC"}
        for condition in ("baseline", "enhanced"):
            prompt = make_prompt(case, condition)
            self.assertNotIn("SECRET_EXPECTED", prompt)
            self.assertNotIn("PRIVATE_RUBRIC", prompt)
            self.assertIn(json.dumps(case[condition]), prompt)

    def test_invalid_response_is_not_silently_coerced(self) -> None:
        for raw in ('[]', '{"action":true,"targets":[],"reason":"x"}',
                    '{"action":"x","targets":"a","reason":"x"}',
                    '{"action":"x","targets":[1],"reason":"x"}'):
            with self.assertRaises(ValueError):
                parse_answer(raw)

    def test_target_order_is_irrelevant_but_duplicates_are_not(self) -> None:
        expected = {"action": "review", "targets": ["a", "b"]}
        self.assertTrue(matches({"action": "review", "targets": ["b", "a"]}, expected))
        self.assertFalse(matches({"action": "review", "targets": ["a", "a", "b"]}, expected))
        self.assertFalse(matches({"action": "keep", "targets": ["a", "b"]}, expected))

    def test_json_fence_can_be_parsed_without_extracting_arbitrary_text(self) -> None:
        answer = parse_answer('```json\n{"action":"ok","targets":[],"reason":"확인"}\n```')
        self.assertEqual(answer["action"], "ok")
        with self.assertRaises(ValueError):
            parse_answer('설명 {"action":"ok","targets":[],"reason":"확인"}')


if __name__ == "__main__":
    unittest.main()
