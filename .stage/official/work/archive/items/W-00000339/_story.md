---
id: W-00000339
title: 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000339
promotion: not_applicable
review: passed
scope: stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000339 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다

## Purpose

열린 관찰·질문·제안 기록에 목록 줄이 없거나 목록 줄이 없는 기록을 가리킬 때 감사가 알려, 닫기 도구가 막히기 전에 어긋남을 찾게 한다

## Actions

없음 — 감사 검사 하나와 테스트를 더하는 일이라 나누지 않는다.

## User value

열린 관찰이나 질문이 목록과 어긋나면 감사가 그 자리에서 알린다. 2026-11-16 에 관찰 12개가 목록
줄만 지워진 채 열린 폴더에 남아 있었는데, 감사는 오류 0개로 통과했고 세션 시작 글은 그 12개를
계속 열린 관찰로 실었다.

## Scope

### Included

- 열린 관찰(`state/observations`)과 질문(`state/questions`)이 각자의 목록(`state/current.md`,
  `state/questions.md`)과 맞는지 양쪽으로 본다. 맞지 않으면 경고(`RECORD_LIVE001`, `RECORD_LIVE002`).

### Excluded

- 제안은 넣지 않는다. 제안 목록은 `PROPOSAL001`/`PROPOSAL002` 가 이미 양쪽으로 본다. 카드 목적에
  "제안"이 들어 있지만 겹치지 않게 뺐다.
- 오류가 아니라 경고로 둔다. 이 어긋남이 있는 다른 프로젝트의 닫기가 갑자기 막히지 않게 한다.

## Risks

- 감사를 바꾸는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).

## Success criteria

- 열린 기록에 목록 줄이 없으면 감사가 기록 이름과 함께 경고한다
- 목록 줄이 가리키는 열린 기록이 없으면 감사가 경고한다
- 목록과 기록이 맞으면 아무것도 알리지 않는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action

닫기 리뷰를 받고 사용자 확인 뒤에 닫는다.

## Related truth

- 2026-11-16 PR #41 — 목록 줄만 지워진 관찰 12개를 닫기 도구로 정리했다.
- `close_record.py` — 목록 줄이 있어야 기록을 닫는다. 이 검사는 그 도구의 기록 묶음 정의를 쓴다.

## Progress

- 2026-11-16: `audit_stage.py` 에 `audit_live_state_indexes` 를 더했다. `close_record.FAMILIES` 의 O 와
  Q 묶음에서 열린 폴더의 기록과 목록의 줄(목록 항목의 `[O-…]` 링크, 표의 첫 칸)을 맞춰 본다.
- 테스트 `test_live_record_indexes_match_their_records`: 목록 줄이 없는 관찰, 기록이 없는 목록 줄,
  목록 줄이 없는 질문, 둘이 맞는 경우.
- 코드 커밋 `b32be111`.
- 전체 테스트에서 세 건이 깨져 `86c2a80e` 로 고쳤다. 기록 파일을 직접 훑던 것을 감사가 이미 모아 둔
  기록 목록(`graph.state`)을 쓰게 바꿨다. 기록 파일 찾기는 `stage_record_paths` 한 곳에서만 하도록
  테스트로 묶여 있다. 또 두 테스트의 준비 데이터가 열린 질문을 만들면서 목록 줄은 넣지 않아 새 검사에
  걸렸으므로, 준비 데이터에 목록 줄을 넣었다.
- 범위를 넘은 경로: `stage/scripts/tests/test_audit_link_pin.py`, `stage/scripts/tests/test_schema_v4_consumers.py`.
  위 준비 데이터를 고치느라 넘었다.

## Verification

- 판별 확인: 고치기 전에 새 테스트에서 경고가 나와야 할 경우들이 깨졌다. 둘이 맞는 경우는 고치기
  전에도 통과했다(바뀌면 안 되는 경우다).
- 실제 사례로 확인: 오늘 정리하기 전의 `.stage`(`956f5566`)에 새 감사를 돌리자 `RECORD_LIVE001`
  경고가 정확히 그 12개(O-00000020, 36, 42, 45, 47, 50, 51, 52, 53, 54, 55, 56)에만 나왔다.
- 지금 저장소에는 새 경고가 없다(감사 errors=0, warnings=32 그대로).
- 세 카드(W-00000338~340)의 변경을 모두 넣고 처음 돌린 전체 테스트는 실패했다(hooks 1건, scripts
  2건, 모두 이 카드의 감사 검사 때문). `86c2a80e` 로 고친 뒤 hooks 446건, scripts 758건(2건
  건너뜀)이 통과했다. 정리 전 `.stage` 에서 12개를 잡는 것도 고친 뒤 다시 확인했다. 이 줄은 처음에
  실행 전에 "통과"로 적었다가 실제 결과로 고쳤다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).
- 사용자 확인 — 2026-11-16: 감사를 바꾼 카드라 닫은 결과를 본 가지에 옮기기 전에 사용자에게
  보였다(DE-00000087). 보인 것은 세 카드(W-00000338~340)의 바뀐 경로와 요약, 범위 밖 테스트 파일
  두 개, 기준별 리뷰 판정과 리뷰어가 실행한 것, 실행 없이 판정한 기준이 없다는 것, 같은 모델의
  리뷰라는 것, 테스트 결과를 미리 적었다가 고친 일이다. 사용자가 "확인, 닫기"로 답했다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q
[exit 0]
----------------------------------------------------------------------
Ran 143 tests in 6.153s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 446 tests in 5.261s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794821645
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794821645. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpsq35_0dp/unattended/W-00000001-1794821645
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
Ran 758 tests in 141.909s

OK (skipped=2)
```

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000339.md
Criteria:
- PASS: 열린 기록에 목록 줄이 없으면 감사가 기록 이름과 함께 경고한다
  Reason: audit_live_state_indexes 가 목록 줄이 없는 열린 O·Q 기록마다 기록 ID 를 담은 RECORD_LIVE001 경고를 낸다; 새 테스트의 관찰·질문 경우가 통과하고, 정리 전 .stage(956f5566)에 python3 stage/scripts/audit_stage.py --project-root <복사본> 을 돌리니 O-00000020·36·42·45·47·50~56 열두 건에만 RECORD_LIVE001 이 나왔다
- PASS: 목록 줄이 가리키는 열린 기록이 없으면 감사가 경고한다
  Reason: 목록에만 있는 ID 마다 RECORD_LIVE002 경고를 내며, 새 테스트의 'index line without a record' 경우(state/current.md 에 O-0002 줄만 추가)가 RECORD_LIVE002 한 건을 확인하고 통과했다
- PASS: 목록과 기록이 맞으면 아무것도 알리지 않는다
  Reason: 새 테스트의 'record and line agree' 경우가 RECORD_LIVE001·002 가 없음을 확인하고 통과했고, 지금 저장소에 python3 stage/scripts/audit_stage.py --project-root . 를 돌리니 RECORD_LIVE 경고 없이 errors=0, warnings=32 였다
- PASS: 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
  Reason: python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q 가 143건 OK 였고, 스크래치 복사본에서 audit_stage.py 만 b32be111^ 판으로 되돌려 새 테스트를 돌리니 경고가 나와야 할 세 하위 사례가 실패하고 맞는 경우만 통과했다
```

## Retrospective

[R-00000339](../../retrospectives/R-00000339.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
