---
id: W-00000135
title: 병렬 정리가 도는 역할을 짐작하지 않고 기록에서 읽는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000134
promotion: not_applicable
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/test_drive_parallel.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000135 병렬 정리가 도는 역할을 짐작하지 않고 기록에서 읽는다

## Purpose

시간이 다 됐을 때 무엇이 돌던 중인지 drive_parallel 이 작업 로그 제목으로 짐작한다. 실행자가 보고를 쓰고도 계속 돌면 리뷰어로 오분류돼 엉뚱한 venue 를 거둔다(O-00000010). W-00000118 이 시도 기록에 running_role 을 적기 시작했으므로 읽는 쪽을 그 기록으로 바꾼다. 기록이 없는 옛 상태에서는 지금의 짐작으로 물러나고 그 사실을 출력에 말한다.

## Actions

- 시간 초과 시 거둘 venue 를 시도 기록의 `running_role` 에서 정한다. 로그 제목 짐작을 걷는다.
- `running_role` 이 없는 옛 기록에서는 기존 짐작으로 물러나고, 물러났다는 사실을 출력에
  말한다.

## Scope

`stage/scripts/drive_parallel.py` 와 그 테스트, CHANGELOG 미출시 절. `drive.py` 는 안
건드린다 — 기록을 만드는 쪽은 이미 끝났다(W-00000118).

## Success criteria

- 시간 초과 시 거둘 venue 가 시도 기록의 `running_role` 에서 나온다. 테스트가 고정한다.
- 실행자가 보고를 쓰고도 계속 도는 상황(로그에 보고 있음 + `running_role` 이 executor)에서
  실행자 venue 를 거둔다 — 짐작이 틀리던 그 경우를 테스트가 고정한다.
- `running_role` 이 없는 옛 기록에서는 기존 짐작으로 물러나고 그 사실이 출력에 남는다.
  테스트가 고정한다.
- 스크립트 스위트가 통과한다. CHANGELOG 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- [O-00000010](../../state/observations/O-00000010.md) — 이 카드가 닫는 관측


## Progress

병렬 2차 페어로 자기 트리에서 실행, 2026-07-30. 실행자(codex)는 한 바퀴에 완성.

## Verification

스텝의 리뷰어(claude)가 세션 한도로 못 떠서 판정 파일이 없었고 — 인프라 실패로 분류돼
**시도는 안 깎였다**(W-00000133 의 규칙이 자기를 지킨 첫 사례). 완료된 일에 스텝을 다시 걸면
"변경 없음"으로 시도만 태우므로, 감독자가 직접 검증하고 수동으로 닫는다: diff 판독(기록 읽기,
애매하면 거절, 옛 기록 물러남 공지 — 카드 요구 그대로), 트리에서 전체 스위트 484 통과, 병합
후 본 체크아웃에서 재확인. **독립 LLM 리뷰는 없었다** — 사실로 남긴다.

### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (197 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785374495
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785374495. Human review + merge required; the base branch was not modified.
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
Ran 484 tests in 69.738s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (197 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785374564
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785374564. Human review + merge required; the base branch was not modified.
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
Ran 484 tests in 68.488s

OK
```

## Retrospective

[R-00000134](../../retrospectives/R-00000134.md)

## Promotion decision

not_applicable — 플러그인 소스 수정.
