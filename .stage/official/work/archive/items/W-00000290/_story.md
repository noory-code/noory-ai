---
id: W-00000290
title: 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구를 둔다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_import_executor_report.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000290
promotion: not_applicable
review: passed
scope: stage/scripts/import_executor_report.py, stage/scripts/tests/test_import_executor_report.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000080
---

# W-00000290 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구를 둔다

## Purpose

작업 로그가 없는 자리에서 커밋 본문에 쓴 실행 보고를 손으로 옮기다 칸이 잘리거나 틀리는 일을 막는다.

## Actions

- 지금 동작: DE-00000075 의 실행 계약은 작업 로그가 없는 클라우드 세션에게 `### Executor report` 를 커밋
  메시지 본문에 쓰게 하고, 로컬이 그 보고를 작업 로그로 옮긴다. 옮기는 도구가 없어 손으로 한다. 커밋
  본문은 보통 72열에서 줄을 바꾸므로 "한 줄" 칸이 여러 줄로 나뉜다. 그대로 옮기면 닫기가 카드의
  Progress 에 첫 줄만 옮긴다(R-00000287).
- `stage/scripts/import_executor_report.py` 가 커밋 하나의 본문에서 실행 보고를 찾아, 나뉜 칸을 한 줄로
  잇고, 계약 순서로 다시 쓴 뒤, `close_work.executor_report_error()` 로 검증하고 작업 로그에 덧붙인다.
  주장한 변경 경로는 그 커밋이 바꾼 경로와 대조한다. 검증에 실패하면 로그를 바꾸지 않는다.
- `stage/skills/stage-retrospective/SKILL.md` 의 닫기 절에 이 도구를 언제 쓰는지 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

클라우드 세션의 결과를 로컬에서 닫을 때 실행 보고를 손으로 옮기지 않아도 되고, 칸이 잘린 채 카드에
남는 일이 없다.

## Scope

### Included


### Excluded

- DE-00000075 의 실행 계약 문장 자체를 바꾸는 일.
- 리뷰 판정이나 리뷰 보고를 커밋에서 옮기는 일.

## Risks


## Success criteria

- 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구가 여러 줄로 나뉜 칸을 한 줄로 이어 붙여 옮긴다는 것을 테스트가 확인한다
- 옮긴 보고가 실행 보고 계약 검증을 통과하지 못하면 도구가 작업 로그를 바꾸지 않고 거절한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Added stage/scripts/import_executor_report.py, which reads one commit's message, takes the last `### Executor report` section, joins each field's wrapped continuation lines with spaces, ends the report at the first line that is neither a field nor a continuation (or at a trailer such as Co-Authored-By), rewrites the fields in contract order, validates them with close_work.executor_report_error() against the paths that commit changed, and appends to the work log only when that passes; the close section of the stage-retrospective skill says when to run it; tests cover wrapped fields with blank lines between them, appending after an existing log, and refusals with the log unchanged for a missing judgment field, claimed paths that differ from the commit, a commit without a report, and a repeated field.
Why: W-00000290 - a commit-body report must reach the work log intact so close copies whole fields onto the card.
Decisions made: Fix this with a tool rather than only a stricter contract sentence, because a tool accepts both wrapped and unwrapped bodies while a sentence can be missed again; validate claimed paths against the commit's own changed paths because a cloud session's report describes exactly one commit; reuse close_work's report parser pieces and validator instead of a second copy; build the log preamble in memory and create the log only after validation passes, so a refusal leaves no file behind.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `7fe78155` 의 worktree 로 닫았다. 실행 보고는 이 카드의 도구
(`import_executor_report.py`)로 그 커밋 본문에서 작업 로그로 옮겼다. 이 세션에는 codex 가 없어,
`STAGE_CODEX_COMPANION` 을 `claude -p` 로 같은 프롬프트를 돌리는 대역 스크립트로 두고 이 프로젝트의
`implementation` 리뷰 명령을 설정 변경 없이 썼다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_import_executor_report.py -q
[exit 0]
----------------------------------------------------------------------
Ran 3 tests in 1.339s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793434491
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793434491. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp46u0qvdp/unattended/W-00000001-1793434491
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
Ran 687 tests in 125.239s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000290.md
Criteria:
- PASS: 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구가 여러 줄로 나뉜 칸을 한 줄로 이어 붙여 옮긴다는 것을 테스트가 확인한다
  Reason: test_joins_wrapped_fields_onto_one_line_each commits a body whose What changed, Why, Decisions made, Changed paths, and Review request fields wrap across lines with blank lines between them, then asserts the log holds each field on one joined line in contract order, excludes trailing prose and trailers, and that close_work.latest_executor_report_lines returns the four full joined lines.
- PASS: 옮긴 보고가 실행 보고 계약 검증을 통과하지 못하면 도구가 작업 로그를 바꾸지 않고 거절한다는 것을 테스트가 확인한다
  Reason: test_refuses_reports_that_fail_the_contract_and_leaves_the_log_alone covers a missing Decisions made field and claimed paths that differ from the commit (both rejected by close_work.executor_report_error), plus a missing report and a repeated field, asserting exit 1, the contract error in stderr, 'work log unchanged', and an identical log before and after; the tool validates before ensure_work_log so no file is created on refusal.
- PASS: Purpose and scope-boundary reporting contract (Decisions made / Work not done)
  Reason: Decisions made gives four concrete choices with reasons that serve the card purpose (tool over contract wording, per-commit path check, reuse of close_work validator, no file on refusal); Work not done: None is accurate since changed paths equal the card scope exactly and neither excluded item (changing the DE-00000075 contract text, importing review verdicts) was touched.
```

## Retrospective

[R-00000290](../../retrospectives/R-00000290.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000080)뿐이므로 `not_applicable`이다.
