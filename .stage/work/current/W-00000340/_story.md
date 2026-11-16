---
id: W-00000340
title: 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000340
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000340 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다

## Purpose

승격을 나중에 쓰는 카드가 닫기 도구의 안내만 따라도 승격 게이트에 막히지 않게 실제로 통하는 순서를 알려 준다

## Actions

없음 — 안내 문구 두 곳과 테스트를 고치는 일이라 나누지 않는다.

## User value

결정을 나중에 공식 기록으로 올리는 사람이 닫기 도구의 안내만 따라도 승격 게이트에 막히지 않는다.
2026-11-16 에 DE-00000082 를 올릴 때 안내대로 `deferred` 로 닫았다가 게이트에 막혔다.

## Scope

### Included

- `close_work.py` 가 승격을 거절할 때 내는 안내에 실제로 통하는 순서를 적는다. `deferred` 로 닫기,
  `approved` 로 바꾸기, intent 만들기, 쓰기, `promoted` 로 기록하기.
- `stage-retrospective` 스킬의 Promotion intent 절에 같은 순서를 적는다.

### Excluded

- 동작은 바꾸지 않는다. 게이트가 `deferred` 를 받게 하거나 감사가 `approved` 를 받게 하는 것은
  게이트·감사 규칙을 바꾸는 결정이라 이 카드에서 하지 않는다.

## Risks

- 닫기 도구를 고치는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).
- `approved` 가 잠깐 남아 있는 동안 감사가 WORK027 오류를 낸다. 안내에 그 상태가 쓰는 동안만이라고
  적었다.

## Success criteria

- 닫기 도구가 deferred 로 닫은 뒤 approved 로 바꾸고 intent 를 만들어 쓰고 promoted 로 기록하는 순서를 안내한다
- 닫기 도구와 게이트와 감사의 동작은 바뀌지 않는다
- 안내 문구를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action

닫기 리뷰를 받고 사용자 확인 뒤에 닫는다.

## Related truth

- W-00000337 — DE-00000082 를 올리다 이 어긋남을 처음 겪은 카드(보관됨).
- `stage/hooks/stage_runtime.py` — 승격 게이트가 `approved`·`promoted` 만 받는 자리.
- `stage/scripts/audit_stage.py` 의 `completed_promotion_errors` — 닫힌 카드의 `approved` 를 WORK027
  오류로 보는 자리.

## Progress

- 2026-11-16: `close_work.py` 의 거절 안내와 `stage-retrospective/SKILL.md` 의 Promotion intent 절에
  순서를 적었다. 같은 날 W-00000337(DE-00000082)과 W-00000265(DE-00000073)를 이 순서로 올렸다.
- 테스트: `test_refuses_promotion_records_the_audit_rejects` 에 안내 문구 확인 세 줄을 더했다.
- 코드 커밋 `617e9ac6`.

## Verification

- 판별 확인: 고치기 전에 그 테스트의 네 경우가 모두 새 확인에서 깨졌다. 고친 뒤 close_work 테스트
  74건이 통과한다.
- 동작이 바뀌지 않았다: `close_work.py` 에서 바뀐 것은 거절 메시지 문자열뿐이다. 게이트와 감사
  파일은 이 카드의 커밋에 없다.
- 세 카드(W-00000338~340)의 변경을 모두 넣고 처음 돌린 전체 테스트는 실패했다(hooks 1건, scripts
  2건, 모두 W-00000339 의 감사 검사 때문). `86c2a80e` 로 고친 뒤 hooks 446건, scripts 758건(2건
  건너뜀)이 통과했고 감사는 errors=0 이다. 이 줄은 처음에 실행 전에 "통과"로 적었다가 실제 결과로
  고쳤다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).
- 사용자 확인 — 2026-11-16: 닫기 도구를 바꾼 카드라 닫은 결과를 본 가지에 옮기기 전에 사용자에게
  보였다(DE-00000087). 보인 것은 세 카드(W-00000338~340)의 바뀐 경로와 요약, 기준별 리뷰 판정과
  리뷰어가 실행한 것, 바뀐 것이 안내 문구뿐이라는 것, 같은 모델의 리뷰라는 것이다. 사용자가
  "확인, 닫기"로 답했다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 74 tests in 19.506s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 446 tests in 5.277s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794821921
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794821921. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpr01_fwzb/unattended/W-00000001-1794821921
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
Ran 758 tests in 187.961s

OK (skipped=2)
```

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000340.md
Criteria:
- PASS: 닫기 도구가 deferred 로 닫은 뒤 approved 로 바꾸고 intent 를 만들어 쓰고 promoted 로 기록하는 순서를 안내한다
  Reason: Commit 617e9ac6 changes the close_work.py WORK027 refusal to say close with `deferred`, set `promotion: approved` with the `promotes:` paths, create each intent with stage/scripts/promote_intent.py, write the paths, then record `promoted`, and stage-retrospective/SKILL.md gives the same order; this matches stage_runtime.py:557 admitting only approved/promoted and audit_stage.py completed_promotion_errors rejecting a completed `approved`.
- PASS: 닫기 도구와 게이트와 감사의 동작은 바뀌지 않는다
  Reason: git show --stat 617e9ac6 lists only CHANGELOG.md, test_close_work.py, SKILL.md and close_work.py, and the close_work.py hunk changes only the stderr message string; the later audit_stage.py change in this range comes from 86c2a80e for W-00000339, not this card.
- PASS: 안내 문구를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
  Reason: I ran python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q at HEAD and it ran 74 tests OK; in a scratch worktree at 617e9ac6 with close_work.py restored from 617e9ac6~1 the same command showed FAILED (failures=4).
```

## Retrospective

[R-00000340](../../retrospectives/R-00000340.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
