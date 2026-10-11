"""Exercise the research wrapper through real public CLIs on synthetic stores."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fixture_avatar_batch import run_batch

AVATAR = Path('/Users/woogis/.codex/worktrees/criteria-integration/noory-ai/avatar/scripts/avatar.py')
STATEMENT = 'Choose an explicit error contract that callers can predict.'


class FixtureBatchTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / '.data').mkdir()
        self.origin = {'kind': 'user_statement', 'actor': 'user',
                       'source_ref': 'session:test/fixture/1',
                       'recorded_by': {'host': 'test', 'session_id': 'fixture', 'via': 'cli'},
                       'quote': '[Synthetic test statement] Callers should predict errors.'}
        self.confirm = {**self.origin, 'quote': '[Synthetic test statement] I confirm this synthetic personal criterion: ' + STATEMENT}
        self.config = {'synthetic_only': True, 'label': 'unit-fixture', 'project_key': 'test/demo-app',
                       'statement': STATEMENT, 'avatar_argv': [sys.executable, str(AVATAR)],
                       'distill_argv': [sys.executable, '-m', 'distill', 'criteria']}
        for name, value in [('recording-fixture.json', self.config), ('choice-origin.json', self.origin),
                            ('confirm-personal.json', {'origin': self.confirm})]:
            self.write(name, value)

    def write(self, name, value):
        (self.root / '.data' / name).write_text(json.dumps(value), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_replay_preserves_choice_and_confirmed_ref(self):
        first = run_batch(self.root, 'ConfigError', [])
        second = run_batch(self.root, 'ConfigError', [])
        self.assertEqual(first, second)
        shown = json.loads((self.root / '.data/avatar-show.json').read_text())
        self.assertEqual(len(shown['choices']), 1)
        self.assertEqual(shown['choices'][0]['chosen'], 'ConfigError')
        self.assertEqual([v['version'] for v in shown['criteria'][0]['versions']], [1, 2])
        self.assertTrue(first['confirmed_ref'].endswith('@2'))

    def test_missing_or_mismatched_confirmation_fails_before_writing(self):
        for quote in ('', 'I confirm some other criterion.'):
            self.write('confirm-personal.json', {'origin': {**self.confirm, 'quote': quote}})
            with self.subTest(quote=quote), self.assertRaises(ValueError):
                run_batch(self.root, 'None', [])
            self.assertFalse((self.root / '.data/avatar').exists())

    def test_ref_must_have_an_eligible_receipt(self):
        ref = 'distill:CR-aaaaaaaaaaaa@1'
        self.write('receiver-check.json', {'results': [{'ref': ref, 'status': 'unknown'}]})
        with self.assertRaises(ValueError):
            run_batch(self.root, 'ConfigError', [ref])
        self.assertFalse((self.root / '.data/avatar').exists())

    def test_changed_choice_cannot_reuse_the_same_key(self):
        run_batch(self.root, 'ConfigError', [])
        with self.assertRaisesRegex(ValueError, 'E_IDEMPOTENCY_CONFLICT'):
            run_batch(self.root, 'None', [])
        shown = subprocess.check_output([sys.executable, str(AVATAR), '--home',
                                        str(self.root / '.data/avatar'), 'show', '--json'], text=True)
        self.assertEqual(json.loads(shown)['choices'][0]['chosen'], 'ConfigError')

    def test_later_cli_failure_keeps_receipts_and_stops_before_show(self):
        ref = 'distill:CR-aaaaaaaaaaaa@1'
        self.write('receiver-check.json', {'results': [{'ref': ref, 'status': 'eligible_current'}]})
        self.config['distill_argv'] = [sys.executable, '-c',
                                      'import sys; print("source unavailable"); sys.exit(2)']
        self.write('recording-fixture.json', self.config)
        with self.assertRaisesRegex(ValueError, 'history-0 failed'):
            run_batch(self.root, 'ConfigError', [ref])
        calls = [json.loads(line) for line in (self.root / '.data/batch-calls.jsonl').read_text().splitlines()]
        self.assertEqual([call['label'] for call in calls], ['choice', 'propose', 'confirm', 'history-0'])
        self.assertEqual(calls[-1]['exit'], 2)
        self.assertFalse((self.root / '.data/batch-result.json').exists())
        self.assertFalse((self.root / '.data/avatar-show.json').exists())


if __name__ == '__main__':
    unittest.main()
