"""Summarize the fixed synthetic attribution batch without changing its raw outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    folder = ROOT / 'evidence' / options.batch
    if (folder / 'summary.json').exists():
        raise FileExistsError('Use a new batch; a summary is never overwritten.')
    fixture = json.loads((folder / 'preregistered.json').read_text(encoding='utf-8'))['fixtures']
    cases = fixture['cases']
    rows = []
    for repeat in (1, 2):
        for case in cases:
            run = folder / f"{case['case_id']}-{repeat}"
            process = json.loads((run / 'process.json').read_text(encoding='utf-8'))
            if process['status'] != 'accepted_structure':
                raise ValueError(f"{run.name} did not pass structure validation.")
            result = json.loads((run / 'result.json').read_text(encoding='utf-8'))
            by_id = {target['id']: target for target in case['targets']}
            if set(item['id'] for item in result['items']) != set(by_id):
                raise ValueError(f"{run.name} omitted or added a source target.")
            for item in result['items']:
                expected = by_id[item['id']]['expected']
                rows.append({'run': run.name, 'target': item['id'],
                             'expected': expected, 'actual': item['label'],
                             'match': expected == item['label'],
                             'model_called': process['model_called']})
    processes = [json.loads((folder / f"{case['case_id']}-{repeat}" / 'process.json')
                          .read_text(encoding='utf-8'))
                 for repeat in (1, 2) for case in cases]
    summary = {'runs': len(processes),
               'model_calls': sum(item['model_called'] for item in processes),
               'code_only_runs': sum(not item['model_called'] for item in processes),
               'target_labels': len(rows), 'matches': sum(item['match'] for item in rows),
               'mismatches': [item for item in rows if not item['match']],
               'all_rows': rows,
               'model_seconds': round(sum(item['seconds'] for item in processes
                                          if item['model_called']), 2),
               'reported_list_cost_usd': round(sum(item.get('reported_list_cost_usd') or 0
                                                  for item in processes), 8)}
    (folder / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)
                                          + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'all_rows'},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
