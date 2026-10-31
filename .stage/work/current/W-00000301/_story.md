---
id: W-00000301
title: 보관한 뒤 대기 결정 목록을 옮겨진 카드에 맞춘다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000301
promotion: not_applicable
review: passed
scope: stage/skills/stage-archive/archive_work.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000301 보관한 뒤 대기 결정 목록을 옮겨진 카드에 맞춘다

## Purpose

결정을 소유한 카드를 보관해도 대기 결정 목록이 옮겨진 카드를 가리켜 보관 직후 감사가 깨지지 않게 한다.

## Actions

- 지금 동작: `archive_work.py` 는 소진되는 venue 예외가 있을 때만 대기 결정 목록을 다시 그리고, 그것도 카드를 옮기기
  전에 그린다. 그래서 정책 결정처럼 소진되지 않는 대기 결정을 소유한 카드를 보관하면, 목록이 예전 경로를 가리키고
  감사가 DECISION004 를 낸다(2026-10-31 W-00000292 와 DE-00000082 보관에서 실제로 일어났다).
- 보관이 끝난 뒤 대기 결정 목록을 한 번 다시 그린다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 소진되지 않는 대기 결정을 소유한 카드를 보관하면 대기 결정 목록이 보관된 카드의 경로와 상태를 가리키고 감사가 통과한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: archive_one() re-renders the pending-decision index through refresh_decision_index.refresh_index() after the cards, retrospectives, and consumed decisions have moved, and reports an error naming the refresh command if that render fails; a test archives a card owning a pending policy decision, with and without a consumed venue exception beside it, and checks that the pending row points at the archived card with status archived, the consumed exception left the index, and the audit reports errors=0.
Why: W-00000301 - archiving a card that owns a decision it does not consume must not leave the audit failing on a stale index.
Decisions made: Refresh once after every archive instead of patching the pre-move render, because the post-move state is the only one the index must match; keep the consumed-decision plan's own render so its prevalidation still refuses a malformed index before anything moves; skip the refresh when the project has no pending-decision index.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `a43334a9` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 25 tests in 3.745s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793455301
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793455301. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpv7oisoz3/unattended/W-00000001-1793455301
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
Ran 712 tests in 134.205s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000301.md
Criteria:
- PASS: 소진되지 않는 대기 결정을 소유한 카드를 보관하면 대기 결정 목록이 보관된 카드의 경로와 상태를 가리키고 감사가 통과한다는 것을 테스트가 확인한다
  Reason: test_v5_archive_points_the_pending_index_at_the_archived_owner archives a card owning a non-consumed pending policy decision (with and without a consumed venue exception) and asserts the index row names official/work/archive/items/W-00000001/_story.md with status archived, no DECISION004, and audit errors=0; archive_one now refreshes the index after the move, the acceptance suite passes (25 tests OK), changed paths stay within scope, and the executor's Decisions made stay within the stated purpose.
```

## Retrospective

[R-00000301](../../retrospectives/R-00000301.md).

## Promotion decision
