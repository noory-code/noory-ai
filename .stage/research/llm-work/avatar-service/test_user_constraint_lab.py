"""Check fictional user-owned and cross-message constraint references."""
import copy
import json
from pathlib import Path
import unittest

from reference_lab import checked_case, merge_labels, model_input

ROOT = Path(__file__).resolve().parent


class UserConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = json.loads((ROOT / 'user-constraint-fixture.json').read_text(
            encoding='utf-8'))
        self.cases = {case['case_id']: case for case in fixture['cases']}

    def test_four_fixed_fictional_cases(self) -> None:
        self.assertEqual(set(self.cases), {'U', 'V', 'Y', 'X'})

    def test_fixed_gold_handles_user_owned_and_prior_message(self) -> None:
        for case in self.cases.values():
            checked_case(case)
            labels = [{'id': target['id'], **target['expected']}
                      for target in case['targets']]
            result = merge_labels(case, labels)
            self.assertTrue(all(item['confirmed_personal_rule'] is False
                                for item in result['items']))
            self.assertTrue(all('expected' not in target
                                for target in model_input(case)['targets']))

    def test_reference_order_comes_from_messages_not_target_array(self) -> None:
        case = copy.deepcopy(self.cases['V'])
        case['targets'].reverse()
        checked_case(case)

    def test_future_reference_is_rejected(self) -> None:
        case = copy.deepcopy(self.cases['V'])
        case['targets'][0]['expected'] = {
            'act': 'request_apply_constraint', 'constraint_ref': 'V2'}
        with self.assertRaises(ValueError):
            checked_case(case)


if __name__ == '__main__':
    unittest.main()
