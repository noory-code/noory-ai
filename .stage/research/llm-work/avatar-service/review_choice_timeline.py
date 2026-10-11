"""Send only Avatar product source to Claude for an independent timeline review."""

import argparse
import subprocess
from pathlib import Path


EVIDENCE = Path(__file__).parent / 'evidence'
FILES = (
    'avatar/web/timeline.mjs',
    'avatar/tests/timeline.test.mjs',
    'avatar/web/app.mjs',
    'avatar/web/index.html',
    'avatar/web/style.css',
    'avatar/scripts/avatar_web.py',
    'avatar/tests/test_avatar_web.py',
    'avatar/scripts/avatar_public.py',
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', type=int, choices=(1, 2), default=1)
    parser.add_argument('--repo', type=Path, required=True)
    options = parser.parse_args()
    review_name = '2026-10-09-choice-timeline-review'
    output = EVIDENCE / (review_name if options.round == 1 else review_name + '-2')
    output.mkdir(parents=True, exist_ok=True)
    sections = []
    for file_name in FILES:
        lines = (options.repo / file_name).read_text(encoding='utf-8').splitlines()
        numbered = '\n'.join(f'{index:4}: {line}' for index, line in enumerate(lines, 1))
        sections.append(f'FILE {file_name}\n{numbered}')
    previous = ''
    if options.round == 2:
        previous = (EVIDENCE / review_name / 'response.txt').read_text(encoding='utf-8')
    prompt = (
        'Review the local Avatar choice timeline change using only the supplied source. '
        'It groups explicitly recorded choices by the viewing computer time zone. '
        'Find concrete correctness, security, privacy, or accessibility regressions. '
        'Especially check date parsing, server module reachability, source labels, empty cases, '
        'and small screens. This is a read-only review; do not claim to have run tests. '
        'Report each actionable finding with file and line, impact, and a minimal fix. '
        'If no actionable finding, say PASS. Use concise Korean.\n\n'
        + ('Check whether these earlier findings are fixed, and report any remaining defects:\n'
           + previous + '\n\n' if previous else '')
        + '\n\n'.join(sections)
    )
    (output / 'prompt.txt').write_text(prompt, encoding='utf-8')
    try:
        review = subprocess.run(
            ['claude', '-p', '--safe-mode', '--tools', '', '--no-session-persistence',
             '--model', 'opus', '--max-turns', '1', '--max-budget-usd', '1'],
            input=prompt, text=True, capture_output=True, timeout=180,
            cwd=options.repo, check=False,
        )
    except subprocess.TimeoutExpired:
        print('Review timed out after 180 seconds.')
        return
    (output / 'response.txt').write_text(review.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(review.stderr, encoding='utf-8')
    print('Review exit: ' + str(review.returncode))
    print(review.stdout[:12000])
    print('Review stderr: ' + review.stderr[:1000])


if __name__ == '__main__':
    main()
