"""Read only explicitly selected fictional lab files without calling a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parent
FIXTURES = (ROOT / 'fixtures').resolve()
MAX_BYTES = 1024 * 1024
ROLES = {'user', 'assistant', 'tool', 'system'}
ORIGINS = {'human_input', 'assistant_output', 'tool_result', 'unknown'}
BLOCK_KINDS = {'text', 'tool_result'}
ID_PATTERN = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,31}\Z')


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate fictional JSON key.')
        result[key] = value
    return result


def parse_lines(content: str) -> dict[str, Any]:
    if not isinstance(content, str) or len(content.encode('utf-8')) > MAX_BYTES:
        raise ValueError('Invalid fictional input size.')
    lines = content.split('\n')
    if lines[-1] == '':
        lines.pop()
    if not 2 <= len(lines) <= 101 or any(not line.strip() for line in lines):
        raise ValueError('A fictional file needs a header and 1-100 messages.')
    try:
        entries = [json.loads(line, object_pairs_hook=unique_object) for line in lines]
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        raise ValueError('Unreadable fictional JSONL.') from error
    header = entries[0]
    if (not isinstance(header, dict)
            or set(header) != {'type', 'format', 'synthetic', 'session_id'}
            or header['type'] != 'lab_header'
            or header['format'] != 'avatar-conversation-lab/1'
            or header['synthetic'] is not True
            or not isinstance(header['session_id'], str)
            or not 0 < len(header['session_id']) <= 100):
        raise ValueError('Not a marked fictional lab file.')
    human_input_ids: list[str] = []
    excluded: dict[str, str] = {}
    seen: set[str] = set()
    for entry in entries[1:]:
        if (not isinstance(entry, dict)
                or set(entry) != {'type', 'id', 'role', 'origin', 'is_meta', 'content'}
                or entry['type'] != 'message'
                or not isinstance(entry['id'], str)
                or ID_PATTERN.fullmatch(entry['id']) is None
                or entry['id'] in seen
                or not isinstance(entry['role'], str)
                or entry['role'] not in ROLES
                or not isinstance(entry['origin'], str)
                or entry['origin'] not in ORIGINS
                or not isinstance(entry['is_meta'], bool)
                or not isinstance(entry['content'], list)
                or not entry['content']):
            raise ValueError('Invalid fictional message envelope.')
        seen.add(entry['id'])
        for block in entry['content']:
            if (not isinstance(block, dict) or set(block) != {'kind', 'text'}
                    or not isinstance(block['kind'], str)
                    or block['kind'] not in BLOCK_KINDS
                    or not isinstance(block['text'], str)
                    or not block['text'].strip()
                    or len(block['text']) > 10000):
                raise ValueError('Invalid fictional content block.')
        if entry['role'] != 'user':
            excluded[entry['id']] = 'non_user_role'
        elif entry['origin'] == 'unknown':
            excluded[entry['id']] = 'unknown_origin'
        elif entry['origin'] != 'human_input':
            excluded[entry['id']] = 'not_human_input'
        elif entry['is_meta']:
            excluded[entry['id']] = 'meta_message'
        elif len(entry['content']) != 1 or entry['content'][0]['kind'] != 'text':
            excluded[entry['id']] = 'mixed_content'
        else:
            human_input_ids.append(entry['id'])
    return {'total_messages': len(seen),
            'human_input_ids': human_input_ids, 'excluded': excluded}


def read_selected_synthetic(path: Path) -> dict[str, Any]:
    selected = Path(path).resolve()
    if (selected.parent != FIXTURES
            or not selected.name.startswith('avatar-conversation-synthetic-')
            or selected.suffix != '.jsonl' or not selected.is_file()):
        raise ValueError('Only one explicitly selected fictional fixture is accepted.')
    if selected.stat().st_size > MAX_BYTES:
        raise ValueError('The fictional fixture is too large.')
    return parse_lines(selected.read_text(encoding='utf-8'))


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect a selected fictional lab file only.')
    parser.add_argument('--file', type=Path, required=True)
    options = parser.parse_args()
    try:
        result = read_selected_synthetic(options.file)
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit('Rejected selected fictional fixture.') from error
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
