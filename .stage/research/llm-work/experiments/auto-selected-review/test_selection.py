"""함수 목록에 원문 전체나 정답을 섞지 않고 잘못 고르면 원문을 유지합니다."""

import unittest

from common import choose_source, function_index

SOURCE = '''FACTOR = 3
def entry(value):
    """값을 계산합니다."""
    return helper(value) + FACTOR
def helper(value):
    return value * 2
def irrelevant():
    return "BODY_SECRET_SENTINEL"
'''


class SelectionTests(unittest.TestCase):
    def test_index_contains_references_but_not_function_body(self) -> None:
        index = function_index(SOURCE)
        self.assertEqual(index[0]["same_file_references"], ["helper"])
        self.assertNotIn("BODY_SECRET_SENTINEL", str(index))

    def test_valid_selection_preserves_behavior_and_removes_irrelevant_function(self) -> None:
        chosen = choose_source(SOURCE, {"action": "select_entry", "targets": ["entry"], "reason": ""})
        scope = {}
        exec(chosen["source"], scope)
        self.assertEqual(scope["entry"](7), 17)
        self.assertNotIn("BODY_SECRET_SENTINEL", chosen["source"])

    def test_unknown_name_does_not_cut_source(self) -> None:
        chosen = choose_source(SOURCE, {"action": "select_entry", "targets": ["unknown"]})
        self.assertEqual(chosen["source"], SOURCE)

    def test_unrecognized_action_does_not_cut_source(self) -> None:
        chosen = choose_source(SOURCE, {"action": "approve", "targets": ["entry"]})
        self.assertEqual(chosen["source"], SOURCE)

    def test_multiple_or_empty_names_do_not_cut_source(self) -> None:
        for targets in ([], ["entry", "helper"], "entry"):
            chosen = choose_source(SOURCE, {"action": "select_entry", "targets": targets})
            self.assertEqual(chosen["source"], SOURCE)

    def test_explicit_full_request_keeps_source(self) -> None:
        self.assertEqual(choose_source(SOURCE, {"action": "use_full", "targets": []})["source"], SOURCE)


if __name__ == "__main__":
    unittest.main()
