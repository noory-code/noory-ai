---
id: W-00000294
title: 닫기 도구가 감사와 같은 승격 기록 검사를 쓴다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000294
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/audit_stage.py, stage/scripts/tests/test_close_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000294 닫기 도구가 감사와 같은 승격 기록 검사를 쓴다

## Purpose

닫기 도구가 감사가 거부할 승격 선택으로 카드를 닫아 닫은 직후 감사가 깨지는 일을 막는다.

## Actions

- 지금 동작: `close_work.py` 는 승격 선택이 최종값인지만 본다. 감사는 닫힌 카드의 `approved` 를 늘 거부하고,
  `promoted` 는 `promotes:` 경로가 있고 그 파일이 있어야 받아들인다(WORK027). 그래서 W-00000292 는 `approved`
  로 닫힌 직후 감사 오류 2개를 냈다.
- 감사의 WORK027 검사를 함수 하나로 꺼내 감사와 닫기 도구가 함께 쓴다. 닫기 도구는 검사를 돌리기 전에 그
  함수로 거절하고 카드를 바꾸지 않는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 감사가 WORK027 로 거부할 승격 선택으로 닫으려 하면 닫기 도구가 카드를 바꾸지 않고 같은 이유로 거절한다는 것을 테스트가 확인한다
- 닫기 도구와 감사가 승격 기록 검사를 한 곳에서 공유한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: The audit's WORK027 rule moved into audit_stage.completed_promotion_errors(), which the audit now calls for completed present cards and close_work.py calls before running any check, refusing with the same messages, a hint to close as deferred until the promotion is written, and the card unchanged; the existing test that closed with approved for a governing decision now closes with deferred, and new tests cover refusing approved with and without paths and promoted without paths or before its path exists, and closing as promoted once every path exists.
Why: W-00000294 - a close must never produce a card the audit then rejects.
Decisions made: Keep the shared function in audit_stage.py because close_work.py already imports that module and the audit owns the rule; refuse before the checks run so a refused close spends no check time and writes nothing; change the existing approved-close test to deferred because its purpose is a final choice for a linked governing decision, and approved is exactly the value the audit rejects on a completed card.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `c3e702d6` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 70 tests in 20.031s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793451020
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793451020. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpsg9rqs5t/unattended/W-00000001-1793451020
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
Ran 703 tests in 136.271s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000294.md
Criteria:
- PASS: 감사가 WORK027 로 거부할 승격 선택으로 닫으려 하면 닫기 도구가 카드를 바꾸지 않고 같은 이유로 거절한다는 것을 테스트가 확인한다
  Reason: test_refuses_promotion_records_the_audit_rejects covers all four WORK027 rejection kinds (approved without paths, approved with an existing path, promoted without paths, promoted before its path exists), asserting exit 1, the shared WORK027 message, 'work item unchanged', and byte-identical card text; a promoted-with-existing-path close still succeeds.
- PASS: 닫기 도구와 감사가 승격 기록 검사를 한 곳에서 공유한다
  Reason: The inline WORK027 logic in Audit was replaced by audit_stage.completed_promotion_errors(), which close_work.py calls (via its existing audit_stage import) before any check runs, so both use one implementation and identical messages.
- PASS: Executor report purpose and scope-boundary reporting contract
  Reason: Decisions made explains the function's location, refusing before checks, and the out-of-the-ordinary change of the existing approved-close test to deferred; Work not done is None, matching the diff, which stays within the card's four scope paths and adds the Unreleased CHANGELOG note.
```

## Retrospective

[R-00000294](../../retrospectives/R-00000294.md).

## Promotion decision
