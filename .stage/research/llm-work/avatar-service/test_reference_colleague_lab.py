"""Keep the fictional speaker-name pair controlled and its gold hidden."""
import json
from pathlib import Path
import unittest

from reference_colleague_lab import checked_colleague_pair, colleague_model_input

ROOT = Path(__file__).resolve().parent


class ReferenceColleagueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads((ROOT / 'reference-colleague-fixture.json').read_text(
            encoding='utf-8'))

    def test_only_last_sentence_changes_and_gold_flips(self) -> None:
        checked_colleague_pair(self.fixture)
        hp, hc = self.fixture['cases']
        self.assertEqual(hp['targets'][:2], hc['targets'][:2])
        self.assertEqual(hp['targets'][2]['expected']['constraint_ref'], 'H1')
        self.assertEqual(hc['targets'][2]['expected']['constraint_ref'], 'H2')

    def test_gold_is_withheld(self) -> None:
        checked_colleague_pair(self.fixture)
        for case in self.fixture['cases']:
            self.assertNotIn('expected', json.dumps(colleague_model_input(case),
                                                    ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
