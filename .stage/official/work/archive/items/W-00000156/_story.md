---
id: W-00000156
title: 문서 규칙에 독자와 수준을 적는다
kind: documentation
venue: claude
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000156
promotion: not_applicable
review: not_required
scope: stage/operations/documentation.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000156 문서 규칙에 독자와 수준을 적는다

## Purpose

문서 규칙에는 조항이 넷 있다. 넷 다 무엇을 쓰지 말라는 말이다 — 지나간 일을 쓰지 마라, 동기는
커밋에 남겨라, 섹션 이름은 본질로 지어라, 자기를 무효로 만드는 문장을 쓰지 마라. **누가 읽는지를
말하는 조항이 하나도 없다.**

그래서 쓰는 사람이 독자를 스스로 고른다. 이 세션에서 제가 고른 독자는 "이 코드를 이미 읽은
사람"이었고, 사용자가 자기 프로젝트의 문서를 읽고 뜻을 알 수 없었다. 어떤 조항도 그것을 막지
않았다.

같은 자리에서 낱말 문제도 드러났다. 영어 낱말을 한 조각씩 옮겨 만든 말("배선", "카드를 세운다")
을 썼다. 한국어를 쓰는 사람은 그런 말을 하지 않는다. 이것도 지금 규칙이 못 잡는다.

## Actions

- 규칙 파일 앞에 독자를 밝히는 절을 넣는다. 문서를 누가 읽는지, 그 독자가 무엇을 알고 무엇을
  모르는지 함께 적는다.
- 수준을 사람으로 못 박는다. 특성화고에서 프로그래밍이나 경영을 배웠고 이 코드베이스는 한 번도
  열어 본 적 없는 고등학생.
- 조항 다섯을 더한다. 넷은 얼마나 자세히 쓰는지에 대한 것이고, 하나는 어떤 낱말을 쓰는지에 대한
  것이다.
- 예외를 명시한다. 원칙 이름, 기록 번호, 경로는 뜻을 다른 곳이 소유하므로 본문이 다시 설명하지
  않는다. 안 적으면 "다른 파일을 열어야 하면 실패"라는 조항이 결정 기록의 원칙 인용을 스스로
  위반한다.

## Scope

바꾸는 것은 규칙 파일 하나와 릴리스 노트다. 규칙 파일은 플러그인이 소유하고 모든 프로젝트가 같은
것을 읽으므로, 번역본이 따로 없다.

바꾸지 않는 것: 카드 작성 규칙. 독자 규칙을 문서 규칙 한 곳에만 두기로 정했다. 카드도 문서이므로
그 규칙을 함께 받는다.

## Success criteria

- 규칙 파일이 독자가 누구인지, 그 독자가 무엇을 알고 무엇을 모르는지 밝힌다.
- 조항이 어떤 낱말을 쓰는지까지 다룬다.
- 원칙 이름·기록 번호·경로 예외가 적혀 있어서, 조항끼리 부딪히지 않는다.
- 사람이 겪는 결과: 사용자가 이 카드 본문을 읽고 무엇을 왜 하는지 다시 묻지 않는다.
- 시험 852개와 감사가 통과한다. 산문의 좋고 나쁨을 판정하는 검사는 없다 — 이 셋은 다른 것이
  깨지지 않았다는 확인일 뿐이다.

## Related truth

- 문서 규칙: `stage/operations/documentation.md`
- 사용자 대면 응답 규칙은 따로다: `stage/operations/output.md`
- 원칙 카탈로그가 문서 규칙의 주인을 지목한다: `official/canon/principles.md`

## Progress

## Verification

### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (203 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785413234
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785413234. Human review + merge required; the base branch was not modified.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 507 tests in 77.612s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.061s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
