"""Run the fixed fictional pair with swapped target and message IDs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reference_lab import SCHEMA, SYSTEM, checked_case, encoded, run_batch

ROOT = Path(__file__).resolve().parent


def checked_pair(fixture: dict[str, Any]) -> None:
    cases = fixture.get('cases')
    if (fixture.get('synthetic') is not True or not isinstance(cases, list)
            or len(cases) != 2 or [case.get('case_id') for case in cases] != ['A', 'B']):
        raise ValueError('Expected the fixed fictional ID pair.')
    a, b = cases
    swap = {'Z1': 'Z2', 'Z2': 'Z1', 'Z3': 'Z3',
            'Z-m1': 'Z-m2', 'Z-m2': 'Z-m1', 'Z-m3': 'Z-m3'}
    if (len(a['messages']) != 3 or len(b['messages']) != 3
            or len(a['targets']) != 3 or len(b['targets']) != 3
            or [item['text'] for item in a['messages']] !=
            [item['text'] for item in b['messages']]
            or any(b_message['id'] != swap.get(a_message['id'])
                   for a_message, b_message in zip(a['messages'], b['messages']))):
        raise ValueError('Source sentences must stay ordered while IDs swap.')
    for left, right in zip(a['targets'], b['targets']):
        expected = dict(left['expected'])
        expected['constraint_ref'] = swap.get(expected['constraint_ref'],
                                              expected['constraint_ref'])
        if (right['id'] != swap.get(left['id'])
                or right['message_id'] != swap.get(left['message_id'])
                or right['exact_text'] != left['exact_text']
                or right['expected'] != expected):
            raise ValueError('Target IDs and gold must change together.')
    for case in cases:
        checked_case(case)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / 'id-swap-fixture.json').read_text(
        encoding='utf-8'))
    checked_pair(fixture)
    cases = fixture['cases']
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / 'id-swap-plan.md').read_text(encoding='utf-8'),
        'fixtures': fixture,
        'runner_source': Path(__file__).read_text(encoding='utf-8'),
        'reference_source': (ROOT / 'reference_lab.py').read_text(encoding='utf-8'),
        'summary_source': (ROOT / 'summarize_reference_lab.py').read_text(
            encoding='utf-8'),
        'system': SYSTEM, 'schema': SCHEMA,
    }), encoding='utf-8')
    failures = run_batch(out, cases)
    if failures:
        raise SystemExit(f'{len(failures)} runs failed; inspect each recorded process.')


if __name__ == '__main__':
    main()
