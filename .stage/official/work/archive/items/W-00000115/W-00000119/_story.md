---
id: W-00000119
title: 상한 되돌리기가 근거를 남기는 명령이 된다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000132
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/escalate_work.py, stage/skills/stage-drive/SKILL.md, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000119 상한 되돌리기가 근거를 남기는 명령이 된다

## Purpose

DE-00000039 §4. 사람이 카드를 바꾼 뒤 다시 돌릴 때 시도 기록 JSON 세 자리를 손으로 맞추는 대신 명령 하나로 되돌린다(O-00000007). --reason 을 필수로 받아 작업 로그에 남긴다 — 상한은 안전 장치이므로 푸는 일에 근거가 붙는다.

## Actions

액션 셋으로 쪼갰다 — 각각 한 번에 끝날 크기이고, 실행 단위와 시도 계수가 액션에 붙는다
(DE-00000037).

| 액션 | 무엇 |
|---|---|
| W-00000131 | 상한 되돌리기가 `--reason` 을 받는 명령이 된다 (O-00000007) |
| W-00000132 | 점검 없이 돈 시도가 작업 로그에 남는다 (W-118 리뷰 지적) |
| W-00000133 | 감독 경로도 인프라 실패에 시도를 안 쓴다 (O-00000003 의 남은 절반) |

## User value

시도 상한에 닿아 사람에게 올라온 카드를 고친 뒤, JSON 세 자리를 손으로 맞추는 대신 명령
하나로 되돌린다. 되돌린 이유가 로그에 남아 나중에 왜 풀었는지 안다. 카드 잘못이 아닌 실패가
모드와 무관하게 시도를 안 먹는다.

## Scope

### Included


### Excluded


## Risks

- 되돌리기 명령이 실행 중인 카드에 걸리면 도는 시도의 기록을 밑에서 바꾼다. 도는 중이면
  거절한다 — `running_role` 이 이제 기록되므로 알 수 있다.
- 감독 경로의 시도 규칙을 무인과 맞추다 무인 쪽을 깨면 안 된다. 두 모드를 같은 테스트
  묶음에서 고정한다.

## Success criteria

- 액션 셋(W-00000131~133)이 전부 완료된다. 각 액션의 기준은 액션 카드가 쥔다.
- 스토리 수준: O-00000007 이 닫힌다 — 사람이 시도 기록 JSON 을 손으로 고칠 일이 없다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.

## Next action

드라이버를 `W-00000119` 에 걸면 액션을 ID 순서로 하나씩 집는다. 병렬 셋(W-111·120·130)이
끝난 뒤에 돌린다 — 본 체크아웃을 쓰므로.

## Progress

액션 셋(W-00000131~133)이 전부 한 바퀴씩 끝났다, 2026-07-30. 액션 단위 실행의 첫 스토리.

## Verification

세 액션이 각자 실행자·인수 검사·판정 파일 리뷰를 통과하고 닫혔다. 스토리 수준 기준 확인:
O-00000007 닫힘(되돌리기가 명령이 되고 근거가 로그에 남음), 사람이 시도 기록 JSON 을 손으로
고칠 일이 없다. 스크립트 스위트 483개 통과.

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
[W-00000001] completed on stage/driver/W-00000001-1785341792
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785341792. Human review + merge required; the base branch was not modified.
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
Ran 483 tests in 77.834s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000132](../../../retrospectives/R-00000132.md)

## Promotion decision

not_applicable — 플러그인 소스 수정.
