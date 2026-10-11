"""Check the fixed fictional two-candidate permutation."""
import json
from pathlib import Path
import unittest

from reference_lab import checked_case, model_input

ROOT = Path(__file__).resolve().parent


class TwoCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads((ROOT / 'two-candidate-fixture.json').read_text(
            encoding='utf-8'))

    def test_only_two_prior_message_order_changes(self) -> None:
        self.assertTrue(self.fixture['synthetic'])
        z, zr = self.fixture['cases']
        self.assertEqual((z['case_id'], zr['case_id']), ('Z', 'ZR'))
        self.assertEqual(z['messages'][:2], list(reversed(zr['messages'][:2])))
        self.assertEqual(z['messages'][2], zr['messages'][2])
        self.assertEqual(z['targets'][2], zr['targets'][2])
        for case in (z, zr):
            checked_case(case)
            self.assertEqual(case['targets'][2]['expected']['constraint_ref'], 'Z1')

    def test_gold_is_not_in_model_input(self) -> None:
        for case in self.fixture['cases']:
            self.assertTrue(all('expected' not in target
                                for target in model_input(case)['targets']))


if __name__ == '__main__':
    unittest.main()
