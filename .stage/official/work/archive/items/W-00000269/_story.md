---
id: W-00000269
title: 닫기 전 리뷰의 기준별 판정을 카드에 적는다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000269
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/operations/review.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000076
---

# W-00000269 닫기 전 리뷰의 기준별 판정을 카드에 적는다

## Purpose

코드 카드가 리뷰를 통과했다는 표시만이 아니라 무엇을 보고 통과시켰는지가 카드에 오래 남게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰가 통과하면 카드의 Verification 에 기준마다 판정과 까닭이 적힌다는 것을 테스트가 확인한다
- operations/review.md 가 닫기 도구가 카드에 무엇을 적는지 코드와 같게 적는다

## Next action


## Related truth


## Progress

- 2026-10-31 Claude Code 클라우드 세션이 `claude/w268-cloud` 에서 이 카드를 실행했다(커밋
  `40063650`). 실행 보고는 사용자의 직접 지시에 따랐다고 적었다. 이 카드의 Actions 가 비어 있어
  표시 형식(기존 코드 블록 안의 `- PASS: <criterion>` 줄과 들여 쓴 `Reason:` 줄)은 실행자가 정했다.
  venue 예외는 실행 뒤에 DE-00000076 으로 기록했다.
- 실행 보고는 커밋 메시지에서 `.stage/.runtime/driver/logs/W-00000269.md` 로 옮겼다. 보고는
  작업 로그 머리말의 책임 경계 변경(닫기 리뷰의 기준별 판정은 카드가 소유한다)을 리뷰가 확인해
  달라고 요청했다.
- 닫기는 HEAD `40063650` 을 대상으로 한다. `.stage/` 는 `04e83116` 상태로, 리뷰 명령과 모델 고정
  시험은 W-00000286 커밋 `1ab2fdf5` 상태로 커밋하지 않고 덮어 썼다.


## Verification


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 60 tests in 7.659s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 60 tests in 7.221s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793425133
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793425133. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmphauxie0l/unattended/W-00000001-1793425133
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
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
Ran 665 tests in 111.317s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.744s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000269.md
Criteria:
- PASS: 리뷰가 통과하면 카드의 Verification 에 기준마다 판정과 까닭이 적힌다는 것을 테스트가 확인한다
  Reason: test_close_work.py 60개가 통과했습니다. 일반 리뷰와 autonomous 독립 리뷰 모두 카드에 기준별 판정과 사유를 남기며, 백틱 처리도 확인합니다. 긴 한글 사유를 포함한 기준 60개도 잘리지 않았습니다. Decisions made와 Work not done은 형식 선택, 실행 주체 예외, 로컬 후속 작업을 밝힙니다. 변경 경로 네 개는 모두 선언 범위 안이며 scope는 바뀌지 않아 목적과 범위 보고 계약을 따랐습니다.
- PASS: operations/review.md 가 닫기 도구가 카드에 무엇을 적는지 코드와 같게 적는다
  Reason: operations/review.md의 상태 필드, 검증 및 리뷰 제목, 로그 경로, 기준별 판정과 사유 형식, 기준을 자르지 않는다는 설명이 close_work.py와 일치합니다. 최종 판정은 카드에 남기고 시도별 기록은 로그에 두므로 드라이버의 역할과도 충돌하지 않습니다. 전체 스크립트 시험 665개와 훅 시험 378개가 통과했고 감사 오류는 0건입니다.
```

## Retrospective

[R-00000269](../../retrospectives/R-00000269.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000076)뿐이므로 `not_applicable`이다.
