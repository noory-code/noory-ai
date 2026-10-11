"""코드 리뷰의 기대값이 모델에 섞이지 않는지 확인합니다."""

import unittest

from run import accepted_shape, prompt_for


class RunnerTests(unittest.TestCase):
    def test_prompt_omits_provenance_and_expected_answers(self) -> None:
        case = {"id": "criterion", "criterion": "모든 값을 보존합니다.",
                "expected": "PRIVATE_EXPECTED", "provenance": "PRIVATE_COMMIT",
                "versions": {"before": {"files": {"module.py": "SOURCE_TEXT"}}}}
        prompt = prompt_for(case, "before")
        self.assertIn("SOURCE_TEXT", prompt)
        self.assertNotIn("PRIVATE_EXPECTED", prompt)
        self.assertNotIn("PRIVATE_COMMIT", prompt)
        self.assertNotIn('"before"', prompt)

    def test_malformed_review_cannot_enter_cache(self) -> None:
        self.assertFalse(accepted_shape({"action": "approve", "targets": ["C"]}, "C"))
        self.assertFalse(accepted_shape({"action": "revise", "targets": []}, "C"))
        self.assertFalse(accepted_shape({"action": "revise", "targets": ["X"]}, "C"))
        self.assertTrue(accepted_shape({"action": "revise", "targets": ["C"]}, "C"))


if __name__ == "__main__":
    unittest.main()
