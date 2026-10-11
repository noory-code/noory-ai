"""Run the frozen fictional pair that names two different speakers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reference_lab import SCHEMA, SYSTEM, checked_case, encoded, model_input, run_batch

ROOT = Path(__file__).resolve().parent
PREFIX = '팀장님은 보고서를 한 장으로 하래요. 동료는 두 장으로 하래요. '


def checked_colleague_pair(fixture: dict[str, Any]) -> None:
    if fixture.get('synthetic') is not True or len(fixture.get('cases', [])) != 2:
        raise ValueError('Only the two fixed fictional cases are accepted.')
    hp, hc = fixture['cases']
    if (hp.get('case_id') != 'HP' or hc.get('case_id') != 'HC'
            or hp['messages'] != [{'id': 'H-m1', 'author': 'user',
                                   'text': PREFIX + '이번에는 팀장님 말대로 맞춰 주세요.'}]
            or hc['messages'] != [{'id': 'H-m1', 'author': 'user',
                                   'text': PREFIX + '이번에는 동료 말대로 맞춰 주세요.'}]
            or hp['targets'][:2] != hc['targets'][:2]
            or [target['id'] for target in hp['targets']] != ['H1', 'H2', 'H3']
            or [target['id'] for target in hc['targets']] != ['H1', 'H2', 'H3']
            or hp['targets'][2]['expected'] !=
            {'act': 'request_apply_constraint', 'constraint_ref': 'H1'}
            or hc['targets'][2]['expected'] !=
            {'act': 'request_apply_constraint', 'constraint_ref': 'H2'}):
        raise ValueError('The controlled pair or its fixed expectations changed.')
    for case in (hp, hc):
        checked_case(case)


def colleague_model_input(case: dict[str, Any]) -> dict[str, Any]:
    return model_input(case)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / 'reference-colleague-fixture.json').read_text(
        encoding='utf-8'))
    checked_colleague_pair(fixture)
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / 'reference-colleague-plan.md').read_text(encoding='utf-8'),
        'fixtures': fixture,
        'colleague_source': Path(__file__).read_text(encoding='utf-8'),
        'reference_source': (ROOT / 'reference_lab.py').read_text(encoding='utf-8'),
        'summary_source': (ROOT / 'summarize_reference_lab.py').read_text(
            encoding='utf-8'),
        'system': SYSTEM, 'schema': SCHEMA,
    }), encoding='utf-8')
    failures = run_batch(out, fixture['cases'])
    if failures:
        raise SystemExit(f'{len(failures)} runs failed; inspect each recorded process.')


if __name__ == '__main__':
    main()
