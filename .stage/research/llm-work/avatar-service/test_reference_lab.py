"""Check fixed-span, within-message constraint references in fictional cases."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from reference_lab import (checked_case, compare_gold, merge_labels,
                           model_input, run_batch, run_one)
from summarize_reference_lab import summarize_batch

ROOT = Path(__file__).resolve().parent


class ReferenceLabTests(unittest.TestCase):
    def setUp(self) -> None:
        cases = json.loads((ROOT / 'reference-fixtures.json').read_text(
            encoding='utf-8'))['cases']
        self.f, self.g, self.h = cases

    def labels(self, case: dict) -> list[dict]:
        return [{'id': target['id'], **target['expected']} for target in case['targets']]

    def test_model_input_keeps_source_and_withholds_gold(self) -> None:
        source = model_input(self.f)
        self.assertEqual(source['messages'], self.f['messages'])
        self.assertEqual(source['targets'][0]['exact_text'], '보고서는 한 장으로')
        self.assertNotIn('expected', source['targets'][0])

    def test_valid_reference_and_abstention_keep_personal_rules_unconfirmed(self) -> None:
        f = merge_labels(self.f, self.labels(self.f))
        h = merge_labels(self.h, self.labels(self.h))
        self.assertEqual(f['items'][1]['constraint_ref'], 'F1')
        self.assertEqual(h['items'][2]['constraint_ref'], 'unresolved')
        self.assertTrue(all(item['confirmed_personal_rule'] is False
                            for item in f['items'] + h['items']))
        self.assertEqual(compare_gold(self.f, f), [])

    def test_wrong_but_valid_reference_is_a_semantic_mismatch(self) -> None:
        labels = self.labels(self.h)
        labels[2]['constraint_ref'] = 'H2'
        result = merge_labels(self.h, labels)
        self.assertEqual(compare_gold(self.h, result), ['H3'])

    def test_missing_duplicate_self_or_unknown_reference_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            merge_labels(self.f, self.labels(self.f)[:1])
        labels = self.labels(self.f)
        labels[1]['constraint_ref'] = 'F2'
        with self.assertRaises(ValueError):
            merge_labels(self.f, labels)
        labels[1]['constraint_ref'] = 'Z9'
        with self.assertRaises(ValueError):
            merge_labels(self.f, labels)
        wrong = copy.deepcopy(self.f)
        wrong['targets'][1]['id'] = 'F1'
        with self.assertRaises(ValueError):
            checked_case(wrong)

    def test_batch_records_later_runs_after_one_fails(self) -> None:
        seen = []

        def fake_run(out: Path, case: dict, repeat: int) -> bool:
            seen.append((case['case_id'], repeat))
            return repeat != 1

        failures = run_batch(Path('unused'), [self.f, self.g],
                             repeats=(1, 2), run=fake_run)
        self.assertEqual(failures, ['F-1', 'G-1'])
        self.assertEqual(seen, [('F', 1), ('G', 1), ('F', 2), ('G', 2)])

    def test_explicit_system_is_sent_and_saved_for_a_run(self) -> None:
        sent = []

        def fake_cli(args: list[str], **kwargs: object) -> SimpleNamespace:
            sent.append(args[args.index('--system-prompt') + 1])
            kwargs['stdout'].write(json.dumps({
                'structured_output': {'items': self.labels(self.f)},
                'total_cost_usd': 0.01,
            }))
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with patch('reference_lab.subprocess.run', side_effect=fake_cli):
                accepted = run_one(folder, self.f, 1, system='fixed prior prompt')
            saved = (folder / 'F-1' / 'system.txt').read_text(encoding='utf-8')
        self.assertTrue(accepted)
        self.assertEqual(sent, ['fixed prior prompt'])
        self.assertEqual(saved, 'fixed prior prompt')

    def test_run_records_preregistered_hash_before_model_call(self) -> None:
        def fake_cli(*args: object, **kwargs: object) -> SimpleNamespace:
            kwargs['stdout'].write(json.dumps({
                'structured_output': {'items': self.labels(self.f)}}))
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text('{"fixed":true}\n',
                                                       encoding='utf-8')
            with patch('reference_lab.subprocess.run', side_effect=fake_cli):
                self.assertTrue(run_one(folder, self.f, 1))
            process = json.loads((folder / 'F-1' / 'process.json').read_text(
                encoding='utf-8'))
        self.assertEqual(process['preregistered_sha256'],
                         hashlib.sha256(b'{"fixed":true}\n').hexdigest())

    def test_summary_counts_failed_run_as_unscored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': {'cases': [self.h]}}), encoding='utf-8')
            for repeat, status in ((1, 'accepted_structure'), (2, 'failed')):
                run = folder / f'H-{repeat}'
                run.mkdir()
                (run / 'process.json').write_text(json.dumps({
                    'status': status, 'seconds': 2.0,
                    'reported_list_cost_usd': 0.01,
                    'error': 'invalid output' if repeat == 2 else None,
                }), encoding='utf-8')
                if repeat == 1:
                    (run / 'result.json').write_text(json.dumps(
                        merge_labels(self.h, self.labels(self.h))), encoding='utf-8')
            summary = summarize_batch(folder)
        self.assertEqual(summary['runs'], 2)
        self.assertEqual(summary['accepted_runs'], 1)
        self.assertEqual(summary['failed_runs'], [
            {'run': 'H-2', 'status': 'failed', 'error': 'invalid output'}])
        self.assertEqual(summary['target_labels'], 6)
        self.assertEqual(summary['scored_labels'], 3)
        self.assertEqual(summary['matches'], 3)
        self.assertEqual(summary['model_seconds'], 4.0)

    def test_null_cli_envelope_does_not_stop_remaining_runs(self) -> None:
        fixture = json.loads((ROOT / 'reference-colleague-fixture.json').read_text(
            encoding='utf-8'))

        def null_cli(*args: object, **kwargs: object) -> SimpleNamespace:
            kwargs['stdout'].write('null')
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': fixture}), encoding='utf-8')
            with patch('reference_lab.subprocess.run', side_effect=null_cli):
                failures = run_batch(folder, fixture['cases'])
            self.assertEqual(failures, ['HP-1', 'HC-1', 'HP-2', 'HC-2'])
            summary = summarize_batch(folder)
            self.assertEqual(summary['runs'], 4)
            self.assertEqual(summary['accepted_runs'], 0)
            self.assertEqual(summary['target_labels'], 12)
            self.assertEqual(summary['scored_labels'], 0)
            self.assertEqual(len(summary['failed_runs']), 4)
            self.assertTrue(all(item['error'] for item in summary['failed_runs']))

    def test_invalid_reference_is_scored_from_raw_model_labels(self) -> None:
        labels = self.labels(self.h)
        labels[0]['act'] = 'request_action'
        labels[2]['constraint_ref'] = 'H1'

        def invalid_reference_cli(*args: object, **kwargs: object) -> SimpleNamespace:
            kwargs['stdout'].write(json.dumps({'structured_output': {'items': labels}}))
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': {'cases': [self.h]}}), encoding='utf-8')
            with patch('reference_lab.subprocess.run', side_effect=invalid_reference_cli):
                failures = run_batch(folder, [self.h])
            self.assertEqual(failures, ['H-1', 'H-2'])
            self.assertTrue(all((folder / f'H-{repeat}' / 'model-comparison.json').exists()
                                for repeat in (1, 2)))
            summary = summarize_batch(folder)
            self.assertEqual(summary['accepted_runs'], 0)
            self.assertEqual(summary['scored_labels'], 6)
            self.assertEqual(summary['matches'], 2)
            self.assertEqual(len(summary['mismatches']), 4)
            self.assertTrue(all(run['status'] == 'invalid_reference'
                                for run in summary['failed_runs']))

    def test_json_parser_recursion_error_does_not_stop_remaining_runs(self) -> None:
        def deep_cli(*args: object, **kwargs: object) -> SimpleNamespace:
            kwargs['stdout'].write('[' * 2000 + '0' + ']' * 2000)
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': {'cases': [self.f, self.h]}}), encoding='utf-8')
            with (patch('reference_lab.subprocess.run', side_effect=deep_cli),
                  patch('reference_lab.json.loads',
                        side_effect=RecursionError('parser depth exceeded'))):
                failures = run_batch(folder, [self.f, self.h])
            self.assertEqual(failures, ['F-1', 'H-1', 'F-2', 'H-2'])
            summary = summarize_batch(folder)
            self.assertEqual(summary['runs'], 4)
            self.assertEqual(summary['accepted_runs'], 0)
            self.assertEqual(len(summary['failed_runs']), 4)

    def test_non_numeric_cli_cost_is_reported_as_unavailable(self) -> None:
        labels = self.labels(self.f)

        def bad_cost_cli(*args: object, **kwargs: object) -> SimpleNamespace:
            kwargs['stdout'].write(json.dumps({
                'structured_output': {'items': labels}, 'total_cost_usd': 'wrong'}))
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': {'cases': [self.f]}}), encoding='utf-8')
            with patch('reference_lab.subprocess.run', side_effect=bad_cost_cli):
                failures = run_batch(folder, [self.f])
            self.assertEqual(failures, [])
            invoked = json.loads((folder / 'F-1' / 'process.json').read_text(
                encoding='utf-8'))['cli_args']
            self.assertEqual(invoked[invoked.index('--model') + 1], 'sonnet')
            self.assertEqual(invoked[invoked.index('--effort') + 1], 'low')
            summary = summarize_batch(folder)
            self.assertEqual(summary['matches'], 4)
            self.assertIsNone(summary['reported_list_cost_usd'])
            self.assertEqual(summary['cost_unavailable_runs'], ['F-1', 'F-2'])

    def test_summary_uses_preregistered_four_repeats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'preregistered.json').write_text(json.dumps({
                'fixtures': {'cases': [self.f]}, 'repeats': 4}), encoding='utf-8')
            for repeat in (1, 2, 3, 4):
                run = folder / f'F-{repeat}'
                run.mkdir()
                (run / 'process.json').write_text(json.dumps({
                    'status': 'accepted_structure', 'seconds': 1.0,
                    'reported_list_cost_usd': 0.01,
                }), encoding='utf-8')
                (run / 'result.json').write_text(json.dumps(
                    merge_labels(self.f, self.labels(self.f))), encoding='utf-8')
            summary = summarize_batch(folder)
        self.assertEqual(summary['runs'], 4)
        self.assertEqual(summary['target_labels'], 8)
        self.assertEqual(summary['matches'], 8)


if __name__ == '__main__':
    unittest.main()
