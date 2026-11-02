---
id: W-00000318
title: 실행을 요구하는 기준의 판정에 실제로 돌렸는지를 남긴다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000318
promotion: not_applicable
review: passed
scope: .stage/settings.json, stage/templates/v4/project-stage/settings.jsonc, stage/scripts/tests/test_template_v4.py, .stage/state/observations/O-00000055.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000318 실행을 요구하는 기준의 판정에 실제로 돌렸는지를 남긴다

## Purpose

리뷰어가 실행을 요구하는 기준을 돌리지 않고 통과시켜도, 판정 사유만 보고 그 사실을 알 수 있게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 리뷰 명령 여섯 개와 v4 템플릿 안내가 모두, 실행이나 동작 관찰을 요구하는 기준이면 실제로 돌린 명령과 결과 또는 돌리지 않았다는 사실을 판정 사유에 적으라고 요구한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: each of the six project review commands in .stage/settings.json (reviewers.claude, reviewers.codex, and the light, standard, deep, and red-team strengths) now adds, after the instruction to name the kind of failing input, that for a criterion asking for a command to be run or behavior to be observed the reason must say which command the reviewer ran and what it showed, or that it did not run it; the v4 template's review guidance carries the same sentence; a test checks all six commands and the template; O-00000055 is closed and leaves the current-observation index; the CHANGELOG has a line.
Why: W-00000318 - a reader of a verdict must be able to tell whether a criterion that needs a run was actually run.
Decisions made: Require disclosure rather than a FAIL for unrun criteria, because reviewers may run only python3 -m unittest and a FAIL rule would block legitimate closes whose checks run elsewhere; take the prompt route O-00000055 listed first rather than adding an evidence-kind field to the verdict format, which the audit would have to learn; fix it now although O-00000055 waited for a recurrence, because the user asked on 2026-11-02 to fix every discovered bug; out-of-scope paths changed: none.
Work not done: The audit does not check that a reason states whether a command ran.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `399dd982` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 25 tests in 0.093s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793634943
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793634943. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpa48g604p/unattended/W-00000001-1793634943
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
Ran 735 tests in 157.658s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000318.md
Criteria:
- PASS: 프로젝트의 리뷰 명령 여섯 개와 v4 템플릿 안내가 모두, 실행이나 동작 관찰을 요구하는 기준이면 실제로 돌린 명령과 결과 또는 돌리지 않았다는 사실을 판정 사유에 적으라고 요구한다는 것을 테스트가 확인한다
  Reason: All six commands in .stage/settings.json (reviewers.claude, reviewers.codex, light, standard, deep, red-team) and stage/templates/v4/project-stage/settings.jsonc carry the run-disclosure sentence; the new test_reviewers_must_say_whether_they_ran_a_criterion_that_asks_for_a_run asserts exactly six commands each contain it plus the comment-joined template; I ran python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q and it showed Ran 25 tests OK; the executor's Decisions made and Work not done fields are non-empty, state purpose-driven choices, report no out-of-scope paths, and every changed path is within the card scope.
```

## Retrospective


## Promotion decision
