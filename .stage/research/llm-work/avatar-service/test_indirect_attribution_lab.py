"""Check the synthetic indirect-speech contract before model calls."""
import copy
import json
from pathlib import Path
import unittest

from indirect_attribution_lab import checked_case, merge_labels, model_input

ROOT = Path(__file__).resolve().parent


class IndirectAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        cases = json.loads((ROOT / 'indirect-attribution-fixtures.json').read_text(
            encoding='utf-8'))['cases']
        self.f, self.g = cases

    def test_model_input_withholds_gold_and_keeps_exact_source(self) -> None:
        source = model_input(self.f)
        self.assertEqual(source['messages'], self.f['messages'])
        self.assertEqual(source['targets'][0]['exact_text'], '보고서는 한 장으로')
        self.assertNotIn('expected', source['targets'][0])

    def test_accepts_fixed_labels_without_promoting_rules(self) -> None:
        labels = [{'id': target['id'], **target['expected']} for target in self.g['targets']]
        result = merge_labels(self.g, labels)
        self.assertEqual(len(result['items']), 3)
        self.assertTrue(all(item['confirmed_personal_rule'] is False
                            for item in result['items']))
        self.assertEqual(result['items'][0]['exact_text'], '모든 파일을 공개하세요')

    def test_rejects_untrusted_or_ambiguous_source(self) -> None:
        wrong = copy.deepcopy(self.f)
        wrong['messages'][0]['author'] = 'unknown'
        with self.assertRaises(ValueError):
            checked_case(wrong)
        wrong = copy.deepcopy(self.f)
        wrong['messages'][0]['text'] += ' 보고서는 한 장으로'
        with self.assertRaises(ValueError):
            checked_case(wrong)

    def test_rejects_missing_id_or_invalid_field_combination(self) -> None:
        labels = [{'id': target['id'], **target['expected']} for target in self.f['targets']]
        with self.assertRaises(ValueError):
            merge_labels(self.f, labels[:1])
        labels[0]['applies_to'] = 'this_task'
        with self.assertRaises(ValueError):
            merge_labels(self.f, labels)


if __name__ == '__main__':
    unittest.main()
