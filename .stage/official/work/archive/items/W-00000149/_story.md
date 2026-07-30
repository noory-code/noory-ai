---
id: W-00000149
title: 드라이버가 부르는 명령에 모델 이름을 적는다
kind: fix
venue: codex
milestone:
priority: 2
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000149
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/templates/, stage/docs/, stage/CHANGELOG.md, .stage/settings.json
promotes:
decision_refs:
---

# W-00000149 드라이버가 부르는 명령에 모델 이름을 적는다

## Purpose

작업을 대신 실행하고 판정하는 명령들이 **어떤 모델로 도는지 프로젝트 어디에도 안 적혀 있다.**
명령이 모델을 안 지정하므로, 각 도구가 자기 기본값을 쓴다. 그 기본값은 실행하는 사람의 홈
디렉터리 설정에 있다.

그래서 두 가지가 생긴다. 사람이 자기 기본 모델을 바꾸면 이 프로젝트의 실행이 조용히 다른 모델로
돌고, 아무 데도 안 남는다. 그리고 카드가 왜 세 번 실패하고 막혔는지 나중에 되짚을 때 "어느 모델이
돌았나"를 못 고정한다.

지금 도는 값은 확인했다 — 사람이 만드는 쪽은 Anthropic 의 Opus(긴 맥락 판), 검토하는 쪽으로 쓰는
다른 도구는 GPT 계열 최신판이다. 이 카드는 **그 값을 바꾸지 않는다.** 값이 적히는 자리만 홈
디렉터리에서 프로젝트 설정으로 옮긴다.

## Actions

- 실행 명령과 판정 명령이 모델을 직접 지정하게 한다. 각 도구가 모델을 받는 방식이 다르므로
  **명령 문자열 안에서** 지정한다. 드라이버가 도구별 문법을 알게 만들지 않는다 — 실행 창이 늘 때마다
  드라이버를 고쳐야 하기 때문이다.
- 고칠 자리는 여덟이다: 실행 명령 두 벌, 판정 명령 두 벌, 판정 강도별 명령 네 벌.
  **한 벌이라도 빠지면 그 자리만 옛 방식으로 돈다.**
- 새 프로젝트가 받는 설정 견본에도 같은 자리를 만든다. 다만 모델 이름을 견본에 박을지, 자리만 두고
  주석으로 안내할지는 구현이 정한다 — 박아 두면 그 모델이 사라질 때 새 프로젝트가 깨진다.
- 한 바퀴가 끝날 때 **어느 명령으로 돌았는지 작업 로그에 남긴다.** 이 기록이 쌓여야 나중에
  "모델 때문에 막힌 카드가 있나"를 셀 수 있다. 지금은 그 근거가 없다.
- 설명 문서에 모델이 명령에 적힌다는 것을 반영하고, 변경 이력에 한 줄 더한다. 매니페스트 버전은
  안 건드린다.

## User value

실행 결과를 되짚을 때 모델이 변수에서 빠진다. 지금은 같은 카드를 다른 사람이 돌리면 다른 모델이
붙을 수 있고, 그 사실이 어디에도 안 남는다.

## Scope

### Included

`.stage/settings.json`, `stage/scripts/drive.py`, `stage/scripts/tests/`, `stage/templates/`,
`stage/docs/`, `stage/CHANGELOG.md`.

### Excluded

- **시도가 오를 때 모델을 바꾸는 장치는 안 만든다.** 두 실행 창이 이미 각자 최상급을 쓰고 있어
  올릴 자리가 없고, 내리는 쪽은 어느 카드가 싼 등급으로 되는지 가를 근거가 없다.
- 모델 값 자체를 바꾸는 일. 지금 값을 그대로 적는다.

## Risks

여덟 자리 중 일부만 고치면 나머지가 옛 방식으로 돈다. 그 상태는 겉으로 안 드러난다 — 결과가
나오기 때문이다. **시험이 여덟 자리를 다 세야 한다.**


## Success criteria

- 실행 명령 두 벌, 판정 명령 두 벌, 강도별 명령 네 벌 — **여덟 자리 모두**가 모델을 직접 지정한다.
  시험이 여덟을 세어 확인한다. 한 자리라도 빠지면 실패다.
- 새 프로젝트가 받는 설정 견본에도 같은 자리가 있다.
- 한 바퀴를 돌린 뒤 작업 로그를 열면 **어느 명령으로 돌았는지 사람이 읽을 수 있다.** 카드 한 장을
  실제로 돌려 그 줄이 로그에 남는 것을 확인한다 — 코드에 그런 코드가 있다는 것만으로는 안 된다.
- 모델 값은 지금 도는 것과 같다. 이 카드는 값을 안 바꾼다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 통과한다.
- 변경 이력에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

두 바퀴 걸렸다. 첫 바퀴는 명령 여덟 자리에 모델을 박았지만 어느 명령으로 돌았는지 남기는 기록을
감독 모드에만 붙여서, 무인 모드는 아무것도 안 남겼다. 판정이 그 기준 하나를 실패로 냈고 두 번째
바퀴가 무인 경로에도 붙였다.

## Verification

- 병합 결과에서 `stage/scripts/tests` 497개, `stage/hooks/tests` 347개 통과.
- 명령 여덟 자리(실행 둘, 판정 둘, 강도 넷) 전부가 모델을 직접 지정한다. 시험이 개수 여덟과 각
  모델 문자열을 확인한다.
- 새 프로젝트가 받는 설정 견본에 같은 여덟 자리가 있고, 주석이 각 명령에 모델을 적으라고 안내한다.
- 모델 값은 지금 도는 것과 같다 — 사람이 만드는 쪽은 Opus 긴 맥락 판, 검토 쪽은 GPT 계열 최신판.
- 어느 명령으로 돌았는지 감독·무인 두 경로 모두 작업 로그에 남는다.
- **판정이 좁혀서 돌았다**: 두 번째 바퀴 판정 파일에 기준 여섯이 다 있고 셋은 첫 바퀴 판정을
  이어받았다. 이 카드가 그 기능의 첫 실전이다.

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
[W-00000001] completed on stage/driver/W-00000001-1785401886
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785401886. Human review + merge required; the base branch was not modified.
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
Ran 497 tests in 78.884s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.098s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.136s

OK

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
[W-00000001] completed on stage/driver/W-00000001-1785401968
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785401968. Human review + merge required; the base branch was not modified.
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
Ran 497 tests in 78.949s

OK
```

## Retrospective

[R-00000149](../../retrospectives/R-00000149.md) — 사람이 겪는 결과를 기준에 넣었더니 그 기준이
구멍을 잡았다.

## Promotion decision

FINAL: not_applicable. 플러그인 코드·설정·문서 변경이고 승격할 산출물이 없다.
