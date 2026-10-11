"""Compare two fixed prompts on fictional reference boundaries."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from reference_lab import SCHEMA, SYSTEM, checked_case, encoded, run_one

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT / 'evidence/2026-10-08-id-swap-v1/preregistered.json'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    parser.add_argument('--study', choices=('heldout', 'resolved'), default='heldout')
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / f'{options.study}-reference-fixture.json').read_text(
        encoding='utf-8'))
    expected_ids = ['C', 'D'] if options.study == 'heldout' else ['E', 'F']
    if fixture.get('synthetic') is not True or [case.get('case_id') for case in
                                                  fixture.get('cases', [])] != expected_ids:
        raise ValueError('Expected the fixed fictional pair.')
    for case in fixture['cases']:
        checked_case(case)
    old = json.loads(PRIOR.read_text(encoding='utf-8'))['system']
    if old == SYSTEM:
        raise ValueError('The two recorded prompts must differ.')
    cases = {}
    for original in fixture['cases']:
        for version in ('old', 'new'):
            case = copy.deepcopy(original)
            case['case_id'] = f"{original['case_id']}-{version}"
            cases[case['case_id']] = case
    first, second = expected_ids
    sequence = [
        (f'{first}-old', 1), (f'{first}-new', 1),
        (f'{second}-old', 1), (f'{second}-new', 1),
        (f'{first}-new', 2), (f'{first}-old', 2),
        (f'{second}-new', 2), (f'{second}-old', 2),
    ]
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / f'{options.study}-reference-plan.md').read_text(
            encoding='utf-8'),
        'original_fixtures': fixture,
        'fixtures': {'synthetic': True, 'cases': list(cases.values())},
        'repeats': 2, 'sequence': sequence,
        'systems': {'old': old, 'new': SYSTEM},
        'runner_source': Path(__file__).read_text(encoding='utf-8'),
        'reference_source': (ROOT / 'reference_lab.py').read_text(encoding='utf-8'),
        'summary_source': (ROOT / 'summarize_reference_lab.py').read_text(
            encoding='utf-8'),
        'schema': SCHEMA,
    }), encoding='utf-8')
    failures = []
    for name, repeat in sequence:
        version = name.rsplit('-', 1)[1]
        if not run_one(out, cases[name], repeat, system=old if version == 'old' else SYSTEM):
            failures.append(f'{name}-{repeat}')
    if failures:
        raise SystemExit(f'{len(failures)} runs failed; inspect each recorded process.')


if __name__ == '__main__':
    main()
