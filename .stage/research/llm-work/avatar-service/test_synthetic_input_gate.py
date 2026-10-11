"""Protect the local-only, fictional input gate from role confusion."""
import json
from pathlib import Path
import unittest

from synthetic_input_gate import parse_lines, read_selected_synthetic

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / 'fixtures/avatar-conversation-synthetic-1.jsonl'


class SyntheticInputGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = [json.loads(line) for line in FIXTURE.read_text(
            encoding='utf-8').splitlines()]

    def encoded(self, lines: list[dict]) -> str:
        return '\n'.join(json.dumps(line, ensure_ascii=False) for line in lines) + '\n'

    def test_role_user_tool_and_mixed_blocks_are_not_human_input(self) -> None:
        summary = parse_lines(self.encoded(self.lines))
        self.assertEqual(summary['total_messages'], 7)
        self.assertEqual(summary['human_input_ids'], ['U1', 'U3'])
        self.assertEqual(summary['excluded']['T1'], 'not_human_input')
        self.assertEqual(summary['excluded']['U2'], 'mixed_content')
        self.assertEqual(summary['excluded']['M1'], 'meta_message')
        self.assertEqual(summary['excluded']['X1'], 'unknown_origin')

    def test_summary_never_contains_message_text_or_source_path(self) -> None:
        summary = read_selected_synthetic(FIXTURE)
        output = json.dumps(summary, ensure_ascii=False)
        for message in self.lines[1:]:
            for block in message['content']:
                self.assertNotIn(block['text'], output)
        self.assertNotIn(self.lines[0]['session_id'], output)
        self.assertNotIn(str(FIXTURE), output)

    def test_duplicate_json_keys_cannot_change_tool_origin(self) -> None:
        raw = FIXTURE.read_text(encoding='utf-8')
        tampered = raw.replace('"origin":"tool_result","is_meta":false',
                               '"origin":"tool_result","origin":"human_input",'
                               '"is_meta":false', 1)
        self.assertNotEqual(raw, tampered)
        with self.assertRaises(ValueError):
            parse_lines(tampered)

    def test_deep_json_and_line_separator_fail_cleanly(self) -> None:
        header = json.dumps(self.lines[0])
        with self.assertRaises(ValueError):
            parse_lines(header + '\n' + '[' * 1500 + '0' + ']' * 1500 + '\n')
        with_separator = [dict(item) for item in self.lines]
        with_separator[1]['content'] = [{'kind': 'text', 'text': 'line\u2028break'}]
        self.assertEqual(parse_lines(self.encoded(with_separator))['total_messages'], 7)

    def test_missing_origin_duplicate_id_or_false_synthetic_flag_fails_closed(self) -> None:
        no_origin = [dict(item) for item in self.lines]
        no_origin[3].pop('origin')
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(no_origin))
        duplicate = [dict(item) for item in self.lines]
        duplicate[3]['id'] = 'U1'
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(duplicate))
        not_synthetic = [dict(item) for item in self.lines]
        not_synthetic[0]['synthetic'] = False
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(not_synthetic))

    def test_wrong_field_types_fail_with_a_controlled_error(self) -> None:
        bad_role = [dict(item) for item in self.lines]
        bad_role[1]['role'] = []
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(bad_role))
        bad_kind = [dict(item) for item in self.lines]
        bad_kind[1]['content'] = [{'kind': [], 'text': 'fictional'}]
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(bad_kind))
        bad_id = [dict(item) for item in self.lines]
        bad_id[1]['id'] = 'private report text'
        with self.assertRaises(ValueError):
            parse_lines(self.encoded(bad_id))

    def test_only_explicit_fixture_path_is_allowed(self) -> None:
        with self.assertRaises(ValueError):
            read_selected_synthetic(ROOT / 'local-input-gate-plan.md')
        with self.assertRaises(ValueError):
            read_selected_synthetic(FIXTURE.parent / '../indirect-attribution-fixtures.json')


if __name__ == '__main__':
    unittest.main()
