"""Compare the fixed fictional reference batch without rewriting its source runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reference_lab import compare_gold, valid_reported_cost

ROOT = Path(__file__).resolve().parent


def summarize_batch(folder: Path) -> dict:
    preregistered = json.loads((folder / 'preregistered.json').read_text(
        encoding='utf-8'))
    fixture = preregistered['fixtures']
    repeats = preregistered.get('repeats', 2)
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 4:
        raise ValueError('Preregistered repeats must be an integer from 1 to 4.')
    rows = []
    processes = []
    run_names = []
    failed_runs = []
    target_labels = 0
    for repeat in range(1, repeats + 1):
        for case in fixture['cases']:
            run = folder / f"{case['case_id']}-{repeat}"
            process = json.loads((run / 'process.json').read_text(encoding='utf-8'))
            target_labels += len(case['targets'])
            processes.append(process)
            run_names.append(run.name)
            if process['status'] != 'accepted_structure':
                failed_runs.append({'run': run.name, 'status': process['status'],
                                    'error': process.get('error')})
                comparison = run / 'model-comparison.json'
                if comparison.exists():
                    rows.extend({'run': run.name, **item} for item in json.loads(
                        comparison.read_text(encoding='utf-8')))
                continue
            result = json.loads((run / 'result.json').read_text(encoding='utf-8'))
            mismatched = set(compare_gold(case, result))
            for item in result['items']:
                target = next(target for target in case['targets']
                              if target['id'] == item['id'])
                rows.append({'run': run.name, 'id': item['id'],
                             'expected': target['expected'],
                             'actual': {key: item[key] for key in
                                        ('act', 'constraint_ref')},
                             'match': item['id'] not in mismatched})
    cost_unavailable_runs = [run_names[index] for index, process in
                             enumerate(processes) if not valid_reported_cost(
                                 process.get('reported_list_cost_usd'))]
    summary = {
        'runs': len(processes), 'accepted_runs': len(processes) - len(failed_runs),
        'failed_runs': failed_runs, 'target_labels': target_labels,
        'scored_labels': len(rows),
        'matches': sum(row['match'] for row in rows),
        'mismatches': [row for row in rows if not row['match']],
        'model_seconds': round(sum(process['seconds'] for process in processes), 2),
        'reported_list_cost_usd': None if cost_unavailable_runs else round(sum(
            process['reported_list_cost_usd'] for process in processes), 8),
        'cost_unavailable_runs': cost_unavailable_runs,
        'rows': rows,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    options = parser.parse_args()
    if not options.batch.replace('-', '').isalnum():
        parser.error('Invalid batch name.')
    folder = ROOT / 'evidence' / options.batch
    if (folder / 'summary.json').exists():
        raise FileExistsError('Never overwrite a recorded batch summary.')
    summary = summarize_batch(folder)
    (folder / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False,
                                            indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'rows'},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
