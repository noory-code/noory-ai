"""Check the fixed fictional pair that changes IDs but not source text."""
import copy
import json
from pathlib import Path
import unittest

from reference_lab import checked_case, model_input
from id_swap_lab import checked_pair

ROOT = Path(__file__).resolve().parent


class IdSwapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads((ROOT / 'id-swap-fixture.json').read_text(
            encoding='utf-8'))

    def test_source_text_and_order_stay_the_same(self) -> None:
        a, b = self.fixture['cases']
        self.assertEqual((a['case_id'], b['case_id']), ('A', 'B'))
        self.assertEqual([message['text'] for message in a['messages']],
                         [message['text'] for message in b['messages']])
        self.assertEqual([target['exact_text'] for target in a['targets']],
                         [target['exact_text'] for target in b['targets']])
        self.assertEqual(a['targets'][2]['expected']['constraint_ref'], 'Z1')
        self.assertEqual(b['targets'][2]['expected']['constraint_ref'], 'Z2')
        for case in (a, b):
            checked_case(case)

    def test_gold_is_withheld(self) -> None:
        for case in self.fixture['cases']:
            self.assertTrue(all('expected' not in target
                                for target in model_input(case)['targets']))

    def test_runner_rejects_changed_text_or_wrong_swapped_gold(self) -> None:
        checked_pair(self.fixture)
        changed_text = copy.deepcopy(self.fixture)
        changed_text['cases'][1]['messages'][0]['text'] = '다른 문장'
        with self.assertRaises(ValueError):
            checked_pair(changed_text)
        changed_gold = copy.deepcopy(self.fixture)
        changed_gold['cases'][1]['targets'][2]['expected']['constraint_ref'] = 'Z1'
        with self.assertRaises(ValueError):
            checked_pair(changed_gold)


if __name__ == '__main__':
    unittest.main()
