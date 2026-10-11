"""입력을 줄여도 연결된 함수와 전역값의 동작을 유지하는지 확인합니다."""

import unittest

from selector import select_source


SOURCE = '''FACTOR = 3

def compute(value):
    return helper(value) + FACTOR

def helper(value):
    return leaf(value) * 2

def leaf(value):
    return value + 1

def unused():
    return "IRRELEVANT_SENTINEL"
'''


class SelectorTests(unittest.TestCase):
    def test_trim_preserves_transitive_calls_and_global_values(self):
        selected = select_source(SOURCE, "compute")
        original_scope, selected_scope = {}, {}
        exec(SOURCE, original_scope)
        exec(selected["source"], selected_scope)
        for value in (-2, 0, 7):
            self.assertEqual(original_scope["compute"](value), selected_scope["compute"](value))
        self.assertNotIn("IRRELEVANT_SENTINEL", selected["source"])

    def test_changed_helper_is_used_when_entry_is_unchanged(self):
        changed = SOURCE.replace("return value + 1", "return value - 5")
        a, b = {}, {}
        exec(select_source(SOURCE, "compute")["source"], a)
        exec(select_source(changed, "compute")["source"], b)
        self.assertEqual(a["compute"](3), 11)
        self.assertEqual(b["compute"](3), -1)

    def test_recursive_dependencies_terminate_and_keep_behavior(self):
        source = "def total(n):\n    return n + total(n - 1) if n else 0\n\ndef unused():\n    return 99\n"
        selected = select_source(source, "total")
        scope = {}
        exec(selected["source"], scope)
        self.assertEqual(scope["total"](4), 10)
        self.assertNotIn("unused", selected["source"])

    def test_missing_entry_returns_identical_source(self):
        self.assertEqual(select_source(SOURCE, "missing")["source"], SOURCE)

    def test_syntax_error_returns_identical_source(self):
        source = "def incomplete(\n"
        self.assertEqual(select_source(source, "incomplete")["source"], source)

    def test_dynamic_lookup_keeps_possible_target(self):
        source = "def entry():\n    return globals()['hidden']()\n\ndef hidden():\n    return 42\n"
        self.assertEqual(select_source(source, "entry")["source"], source)

    def test_decorator_side_effects_keep_full_module(self):
        source = "def entry():\n    return 1\n\n@register\ndef effect():\n    return 2\n"
        self.assertEqual(select_source(source, "entry")["source"], source)

    def test_duplicate_name_keeps_full_module(self):
        source = "def entry():\n    return 1\n\ndef entry():\n    return 2\n"
        self.assertEqual(select_source(source, "entry")["source"], source)


if __name__ == "__main__":
    unittest.main()
