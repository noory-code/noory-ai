---
id: W-00000293
title: 계획 카드 등록도 겹친 번호의 브랜치 이름을 보여 준다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000293
promotion: not_applicable
review: passed
scope: stage/skills/stage-work/register_work.py, stage/scripts/tests/test_register_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000293 계획 카드 등록도 겹친 번호의 브랜치 이름을 보여 준다

## Purpose

계획 카드를 등록할 때도 다른 브랜치가 이미 쓴 번호면 어느 브랜치인지 알려 주어 사람이 바로 고를 수 있게 한다.

## Actions

- 지금 동작: `register_work.py` 는 현재 카드 등록에서는 다른 브랜치가 쓴 번호를 브랜치 이름과 함께
  거절하지만, `--backlog` 등록에서는 "id is already used" 만 보여 준다(W-00000291 닫기 리뷰, R-00000291).
- `--backlog` 경로도 다른 브랜치의 번호면 그 브랜치 이름을 함께 보여 준다. 지금 체크아웃에서 쓰인 번호는
  지금처럼 거절한다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 다른 브랜치가 이미 쓴 번호로 계획 카드를 등록하면 그 브랜치 이름과 함께 거절된다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: register_backlog_card() now appends `on branch <refs>` to its already-used refusal when the id comes from another local or remote-tracking branch, and keeps the plain refusal for an id used in this checkout; the existing branch test now asserts the branch name on both the current and planned paths.
Why: W-00000293 - a person refused on a planned card should see which branch holds the id, as on the current-card path.
Decisions made: Reuse branch_record_numbers() from stage_record_ids.py rather than a second lookup, and append the branch only when the id actually comes from another branch.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `6c027354` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 47 tests in 6.375s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793450578
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793450578. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmplhsjv09a/unattended/W-00000001-1793450578
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
Ran 701 tests in 138.084s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000293.md
Criteria:
- PASS: 다른 브랜치가 이미 쓴 번호로 계획 카드를 등록하면 그 브랜치 이름과 함께 거절된다는 것을 테스트가 확인한다
  Reason: test_explicit_id_used_on_another_branch_is_refused now asserts 'on branch origin/parallel' and exit 1 for the --backlog subtest too, and register_backlog_card() appends the branch from branch_record_numbers(); the change stays in the three scoped paths and the report's Decisions made matches the diff.
```

## Retrospective

[R-00000293](../../retrospectives/R-00000293.md).

## Promotion decision
