"""Run fixed fictional user-owned and cross-message reference cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reference_lab import SCHEMA, SYSTEM, checked_case, encoded, run_batch

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / 'user-constraint-fixture.json').read_text(
        encoding='utf-8'))
    cases = fixture.get('cases')
    if (fixture.get('synthetic') is not True or not isinstance(cases, list)
            or [case.get('case_id') for case in cases] != ['U', 'V', 'Y', 'X']):
        raise SystemExit('Expected the four fixed fictional cases.')
    for case in cases:
        checked_case(case)
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / 'user-constraint-plan.md').read_text(encoding='utf-8'),
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
