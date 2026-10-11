"""Run a controlled fictional pair with the frozen reference-lab prompt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reference_lab import SCHEMA, SYSTEM, checked_case, encoded, model_input, run_batch

ROOT = Path(__file__).resolve().parent


def checked_pair(fixture: dict[str, Any]) -> None:
    if fixture.get('synthetic') is not True or len(fixture.get('cases', [])) != 2:
        raise ValueError('Only the two fixed fictional cases are accepted.')
    h, hp = fixture['cases']
    if (h.get('case_id') != 'H' or hp.get('case_id') != 'HP'
            or h['messages'][0]['text'] !=
            '팀장님은 보고서를 한 장으로 하래요. 동료는 두 장으로 하래요. 이번에는 그렇게 맞춰 주세요.'
            or hp['messages'][0]['text'] !=
            '팀장님은 보고서를 한 장으로 하래요. 동료는 두 장으로 하래요. 이번에는 팀장님 말대로 맞춰 주세요.'
            or h['targets'][:2] != hp['targets'][:2]
            or [target['id'] for target in h['targets']] != ['H1', 'H2', 'H3']
            or [target['id'] for target in hp['targets']] != ['H1', 'H2', 'H3']
            or h['targets'][2]['expected'] !=
            {'act': 'request_apply_constraint', 'constraint_ref': 'unresolved'}
            or hp['targets'][2]['expected'] !=
            {'act': 'request_apply_constraint', 'constraint_ref': 'H1'}):
        raise ValueError('The controlled pair or its fixed expectations changed.')
    for case in (h, hp):
        checked_case(case)


def pair_model_input(case: dict[str, Any]) -> dict[str, Any]:
    return model_input(case)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / 'reference-pair-fixture.json').read_text(
        encoding='utf-8'))
    checked_pair(fixture)
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / 'reference-pair-plan.md').read_text(encoding='utf-8'),
        'fixtures': fixture,
        'pair_source': Path(__file__).read_text(encoding='utf-8'),
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
