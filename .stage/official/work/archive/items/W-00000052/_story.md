---
id: W-00000052
title: CLAUDE.md 언어 규칙에 .stage/ 예외 명시
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000051
promotion: not_applicable
review: not_required
scope: CLAUDE.md
promotes:
decision_refs:
---

# W-00000052 CLAUDE.md 언어 규칙에 .stage/ 예외 명시

## Purpose

리포 전체 영어 규칙과 .stage/ 문서의 한국어 사용이 충돌해 보이는 문제를 없앤다

## Scope

루트 `CLAUDE.md`의 `## Language` 절만 바꾼다. `AGENTS.md`는 `CLAUDE.md`를 SSOT로 가리키기만 하므로
건드리지 않는다.

## Success criteria

- `.stage/` 문서가 영어 규칙의 예외임이 명시되고, 그 언어의 출처가 `.stage/settings.json`의
  `language` 태그임을 밝힌다.
- 기계 토큰(ID, 경로, frontmatter 키·열거값, work kind, venue·원칙 이름, 기록 섹션 제목)은 태그와
  무관하게 영어라는 점을 함께 적는다.
- 특정 시점의 값("현재 한국어")을 본문에 박지 않는다.

## Related truth

- 이 예외가 없어서 작업 중 Stage 문서를 영어로 바꾸려 한 오판이 있었다 (R-00000049).
- `AGENTS.md`는 "SSOT는 CLAUDE.md이며 내용을 복제하지 말 것"을 선언하고 있다.

## Progress

- `## Language` 절에 `.stage/` 예외 항목을 추가하고, 언어의 출처를 `.stage/settings.json`의
  `language` 태그로 가리켰다.


## Verification


### Executed at close — 2026-07-24

```
$ python3 -c "import json,pathlib; s=json.loads(pathlib.Path('.stage/settings.json').read_text()); c=pathlib.Path('CLAUDE.md').read_text(); assert 'language' in s; assert '.stage/settings.json' in c; print('CLAUDE.md points at the settings language tag:', s['language'])"
[exit 0]
CLAUDE.md points at the settings language tag: ko
```

## Retrospective


## Promotion decision
