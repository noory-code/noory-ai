---
id: W-00000157
title: 드라이버 시험이 물려받은 환경 변수에 흔들리지 않게 한다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000157
promotion: not_applicable
review: not_required
scope: stage/scripts/tests/
promotes:
decision_refs:
---

# W-00000157 드라이버 시험이 물려받은 환경 변수에 흔들리지 않게 한다

## Purpose

드라이버는 판정하는 쪽에 환경 변수 몇 개를 넘긴다 — 이전 판정 파일이 어디 있는지, 어느 기준이
떨어졌는지 같은 것. 그 변수가 깔린 창 안에서 시험을 돌리면 드라이버 시험 둘이 거짓으로 실패한다.
시험이 자기 값을 직접 넣는 대신 그 창에 이미 있는 값을 읽기 때문이다.

두 번째 바퀴부터만 드러난다. 첫 바퀴에는 이전 판정 파일이 없어서 변수가 안 실린다.

**이 카드가 만든 문제가 아니다.** 판정한 쪽이 바뀐 파일을 되돌린 사본에서도 똑같이 실패하는 것을
확인했다(2026-07-30, W-00000155 두 번째 바퀴).

실패하는 시험 둘:

- `test_second_review_only_rechecks_failures_and_changed_segment` — 오류로 끝난다.
- `test_missing_previous_verdict_falls_back_to_full_review` — 이전 판정이 없다고 봐야 하는데
  있다고 본다.

## Actions

- 시험이 물려받은 환경을 지우고 자기 값만 쓰게 한다. 지울 변수 일곱 개:
  `STAGE_CHANGED_PATHS_FILE`, `STAGE_PREVIOUS_REVIEW_VERDICT_FILE`,
  `STAGE_REVIEW_FAILED_CRITERIA_FILE`, `STAGE_REVIEW_MODE`, `STAGE_REVIEW_VERDICT_FILE`,
  `STAGE_WORK_ITEM_PATH`, `STAGE_WORK_LOG_PATH`.
- 시험 둘만 고치지 말고 시험 묶음 전체가 같은 보호를 받게 한다. 지금 실패하는 둘만 고치면 다음에
  변수 하나가 늘 때 같은 일이 또 생긴다.

## User value

드라이버가 도는 중에 시험을 돌려도 결과를 믿을 수 있다. 지금은 거짓 실패를 만나면 사람이 원인이
자기 변경인지 환경인지 가려내야 하고, 이번에 판정하는 쪽이 그 확인에 한 번의 리허설을 썼다.

## Scope

### Included

- 드라이버 시험 묶음의 환경 격리.

### Excluded

- 드라이버 자체. 검사 명령은 이 문제에 안 걸린다 — 판정용 변수는 판정하는 쪽에만 실리고, 검사는
  드라이버 자신의 환경으로 돈다. 드라이버를 판정 창 안에서 다시 띄우는 경우만 예외다.

## Risks

- 환경을 통째로 지우면 시험이 실제로 필요한 값까지 사라질 수 있다. 지울 변수를 이름으로 집는다.

## Success criteria

- 일곱 변수가 깔린 창에서 시험 묶음을 돌려도 통과한다.
- 그 변수가 없는 평소 창에서도 그대로 통과한다.
- 사람이 겪는 결과: 드라이버 두 번째 바퀴 뒤에 시험을 돌려도 거짓 실패가 안 나온다.

## Next action

일곱 변수를 깔고 시험 묶음을 돌려 실패를 재현한다.

## Progress

## Verification

### Executed at close — 2026-07-31

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
[W-00000001] completed on stage/driver/W-00000001-1785471001
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785471001. Human review + merge required; the base branch was not modified.
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
Ran 512 tests in 78.804s

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
[W-00000001] completed on stage/driver/W-00000001-1785471080
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785471080. Human review + merge required; the base branch was not modified.
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
Ran 512 tests in 78.675s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.160s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
