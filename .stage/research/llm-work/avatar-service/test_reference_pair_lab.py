"""Keep the paired fictional examples controlled and their gold hidden."""
import json
from pathlib import Path
import unittest

from reference_pair_lab import checked_pair, pair_model_input

ROOT = Path(__file__).resolve().parent


class ReferencePairTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / 'reference-pair-fixture.json').read_text(
            encoding='utf-8'))

    def test_only_last_sentence_changes(self):
        checked_pair(self.fixture)
        h, hp = self.fixture['cases']
        self.assertEqual(h['messages'][0]['text'].split('이번에는 ')[0],
                         hp['messages'][0]['text'].split('이번에는 ')[0])
        self.assertEqual(h['targets'][:2], hp['targets'][:2])
        self.assertEqual(h['targets'][2]['expected']['constraint_ref'], 'unresolved')
        self.assertEqual(hp['targets'][2]['expected']['constraint_ref'], 'H1')

    def test_gold_is_not_model_input(self):
        checked_pair(self.fixture)
        for case in self.fixture['cases']:
            source = pair_model_input(case)
            self.assertNotIn('expected', json.dumps(source, ensure_ascii=False))
            self.assertNotIn('case_id', source)


if __name__ == '__main__':
    unittest.main()
