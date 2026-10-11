"""Check saved publication, CI, source, and actual-host evidence."""
import json
from pathlib import Path

evidence = Path(__file__).resolve().parent / 'evidence/2026-10-07-release'
expected = {'stage': '0.63.3', 'avatar': '0.1.2', 'distill': '1.10.0'}


def read(relative):
    return json.loads((evidence / relative).read_text())


def main():
    for name, count in [('noory', 30), ('distill', 7)]:
        merged = read(name + '-merged.json')
        assert merged['state'] == 'MERGED', name
        checks = read(name + '-ci.json')
        assert len(checks) == count, (name, len(checks))
        assert all(check['state'] == 'SUCCESS' for check in checks), name
    sources = read('merged-source-check.json')
    for name, version in expected.items():
        assert sources['plugins'][name]['version'] == version
        assert sources['plugins'][name]['matches_loaded_source']
        release = read(name + '-release.json')
        assert release['tagName'] == name + '-v' + version
        assert release['isDraft'] is False and release['isPrerelease'] is False
    for host in ('claude', 'codex'):
        assert read('published/' + host + '-load-process.json')['exit'] == 0
    codex = read('published/codex-load-final.txt')
    assert codex['observed_versions'] == expected
    assert not codex['failures']
    claude_events = [json.loads(line) for line in (evidence / 'published/claude-load.jsonl').read_text().splitlines()]
    final = next(event['result'] for event in claude_events if event.get('type') == 'result')
    final_json = json.loads(final[final.index('{'):final.rindex('}') + 1])
    assert final_json['observed_versions'] == expected
    assert not final_json['failures']
    skills = [part['input']['skill'] for event in claude_events
              for part in event.get('message', {}).get('content', [])
              if isinstance(part, dict) and part.get('type') == 'tool_use' and part.get('name') == 'Skill']
    assert skills == ['stage:stage-handoff', 'avatar:avatar', 'distill:distill-criteria']
    cleanup = read('published/codex-test-cleanup.json')
    assert cleanup['config_byte_identical']
    assert all(item['exit'] == 0 for item in cleanup['removals'])
    print('PASS: three published versions, two merged PRs, 37 CI jobs, matching source files, and two actual hosts.')


if __name__ == '__main__':
    main()
