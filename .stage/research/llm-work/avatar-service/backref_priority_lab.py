"""Run the fixed fictional ID pair after prioritizing earlier references."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from id_swap_lab import checked_pair
from reference_lab import SCHEMA, SYSTEM, encoded, run_batch

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    fixture = json.loads((ROOT / 'id-swap-fixture.json').read_text(encoding='utf-8'))
    checked_pair(fixture)
    out = ROOT / 'evidence' / options.batch
    out.mkdir(parents=True, exist_ok=False)
    (out / 'preregistered.json').write_text(encoded({
        'plan': (ROOT / 'backref-priority-plan.md').read_text(encoding='utf-8'),
        'fixtures': fixture, 'repeats': 4,
        'runner_source': Path(__file__).read_text(encoding='utf-8'),
        'reference_source': (ROOT / 'reference_lab.py').read_text(encoding='utf-8'),
        'summary_source': (ROOT / 'summarize_reference_lab.py').read_text(
            encoding='utf-8'),
        'system': SYSTEM, 'schema': SCHEMA,
    }), encoding='utf-8')
    failures = run_batch(out, fixture['cases'], repeats=(1, 2, 3, 4))
    if failures:
        raise SystemExit(f'{len(failures)} runs failed; inspect each recorded process.')


if __name__ == '__main__':
    main()
