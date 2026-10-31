---
id: W-00000297
title: 드라이버가 닫을 때도 긴 리뷰 제한 시간을 쓰게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000297
promotion: not_applicable
review: passed
scope: stage/scripts/driver_lifecycle.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000297 드라이버가 닫을 때도 긴 리뷰 제한 시간을 쓰게 한다

## Purpose

드라이버가 close_work 를 timeout+60초에 끊어 더 긴 --review-timeout 을 쓰지 못하는 일을 막고 바깥 제한 시간이 검사와 리뷰를 함께 덮게 한다.

## Actions

- 지금 동작: `stage/scripts/driver_lifecycle.py` 의 `close_via_close_work()` 는 `close_work.py` 를
  `timeout + 60` 초에 끊고, 그 안의 리뷰에 `--review-timeout` 을 `--timeout` 과 같은 값으로 넘긴다.
  그래서 드라이버로 닫을 때는 `close_work.py` 의 리뷰 기본값 3600초를 쓰지 못한다.
- 출처: W-00000270 실행 보고(Work not done)와 R-00000270 "Next changes".

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 드라이버가 close_work 를 부를 때 바깥 제한 시간이 검사 시간과 리뷰 제한 시간을 함께 덮는다는 것을 테스트가 확인한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-10-31

```
What changed: close_via_close_work() takes an optional review_timeout (default: the check timeout, so existing callers keep their behavior), passes it as --review-timeout, and kills close_work only after timeout times the card's acceptance plus extra checks, plus the review budget, plus 60 seconds; the unattended driver's item close passes the larger of 3600 seconds and its per-command timeout, capped by the run's remaining wall clock; operations/review.md describes the new bound; tests cover the outer bound for two acceptance checks, one extra check, and a 3600-second review, and the unattended review budget for a 300-second and a 7200-second wall clock.
Why: W-00000297 - a high-effort review in a driver-run close must get close_work's longer budget instead of failing at the check budget.
Decisions made: Cap the unattended review budget by the remaining wall clock, because the run promises to stop at max_wall_clock_seconds; leave parent closes on the old bound because close_ready_parents has no wall-clock information; keep review_timeout optional so the function stays compatible; out-of-scope paths changed: stage/scripts/driver_unattended.py (the call site that passes the budget), stage/scripts/tests/test_drive_unattended.py (ten close stubs gained the new keyword and one test covers the budget), and stage/operations/review.md (its driver sentence would otherwise be false).
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `0469ab96` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793454411
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793454411. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpa5qu03yb/unattended/W-00000001-1793454411
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
Ran 709 tests in 135.737s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000297.md
Criteria:
- PASS: 드라이버가 close_work 를 부를 때 바깥 제한 시간이 검사 시간과 리뷰 제한 시간을 함께 덮는다는 것을 테스트가 확인한다
  Reason: test_close_outer_bound_covers_every_check_plus_the_review_budget asserts the subprocess timeout equals 30*3 checks (two acceptance plus one extra, matching close_work's checks = acceptance + --check) + 3600 review + 60 and that --review-timeout 3600 is passed; the unattended test confirms the item close receives the longer, wall-clock-capped review budget; full stage scripts (709) and hooks (378) suites pass; the executor report's Decisions made field names its three out-of-scope paths and the parent-close limit, and Work not done is None, so the report follows the purpose and scope-boundary contract
```

## Retrospective

[R-00000297](../../retrospectives/R-00000297.md).

## Promotion decision
