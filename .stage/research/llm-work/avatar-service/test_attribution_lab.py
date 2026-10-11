"""Check that the attribution lab cannot relabel trusted message authors."""
import copy
import json
from pathlib import Path
import unittest

from attribution_lab import checked_case, merge_labels, model_input

CASES = json.loads((Path(__file__).parent / 'attribution-fixtures.json').read_text(encoding='utf-8'))['cases']


class AttributionTests(unittest.TestCase):
    def test_fixture_targets_are_exact_unique_spans(self) -> None:
        for case in CASES:
            checked_case(case)

    def test_unknown_and_assistant_authors_never_need_a_model_label(self) -> None:
        self.assertEqual(model_input(CASES[3])['targets'], [])
        self.assertEqual(merge_labels(CASES[3], [])['items'][0]['label'], 'unknown')
        self.assertEqual(merge_labels(CASES[1], [
            {'id': 'B2', 'label': 'direct_report'}, {'id': 'B3', 'label': 'direct_request'},
        ])['items'][0]['label'], 'assistant_content')

    def test_missing_extra_and_duplicate_model_targets_are_rejected(self) -> None:
        case = CASES[0]
        labels = [{'id': target['id'], 'label': target['expected']} for target in case['targets']]
        for bad in (labels[:-1], labels + [{'id': 'X', 'label': 'direct_report'}],
                    labels[:-1] + [labels[0]]):
            with self.assertRaises(ValueError):
                merge_labels(case, bad)

    def test_role_or_source_changes_in_fixture_are_rejected(self) -> None:
        case = copy.deepcopy(CASES[1])
        case['targets'][0]['expected'] = 'direct_report'
        with self.assertRaises(ValueError):
            checked_case(case)
        case = copy.deepcopy(CASES[0])
        case['targets'][1]['exact_text'] = '없는 인용'
        with self.assertRaises(ValueError):
            checked_case(case)


if __name__ == '__main__':
    unittest.main()
