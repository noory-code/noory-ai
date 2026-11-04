---
id: W-00000316
title: 마일스톤 완료 기준 앞의 목록 기호가 겹치지 않게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_v4.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000316
promotion: not_applicable
review: passed
scope: stage/skills/stage-roadmap/manage_roadmap.py, stage/scripts/tests/test_roadmap_v4.py, .stage/state/observations/O-00000045.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000316 마일스톤 완료 기준 앞의 목록 기호가 겹치지 않게 한다

## Purpose

완료 기준을 목록 기호를 붙여 넘겨도 마일스톤 기록에 기호가 겹쳐 남지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 완료 기준 값이 '- ', '* ', '+ ' 로 시작해도 기록에는 '- 기준' 한 겹만 남고, 기호 없는 값과 하이픈이 내용의 일부인 값('-5% 지연')은 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: create-milestone strips one leading list marker (a hyphen, asterisk, or plus followed by whitespace, after optional leading whitespace) from each completion-criteria value before adding its own "- ", through a module-level LIST_MARKER_RE; a test passes values starting with "- ", "* ", and "+ ", a plain value, and "-5% latency ..." and expects one marker each with the last value kept intact; O-00000045 is closed and leaves the current-observation index; the CHANGELOG has a line.
Why: W-00000316 - a completion criterion passed as a list item must not be recorded with a doubled marker.
Decisions made: Strip only a marker followed by whitespace, so content that begins with a hyphen, such as a negative percentage, stays as written; strip one marker, not repeated ones, to avoid eating intentional text; fix it now although O-00000045 waited for a real occurrence, because the user asked on 2026-11-02 to fix every discovered bug; out-of-scope paths changed: none.
Work not done: None
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `fc5ce50c` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 15 tests in 4.618s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793634240
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793634240. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp2pxb5n2l/unattended/W-00000001-1793634240
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
Ran 732 tests in 151.721s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000316.md
Criteria:
- PASS: 완료 기준 값이 '- ', '* ', '+ ' 로 시작해도 기록에는 '- 기준' 한 겹만 남고, 기호 없는 값과 하이픈이 내용의 일부인 값('-5% 지연')은 그대로라는 것을 테스트가 확인한다
  Reason: test_completion_criteria_passed_as_list_items_keep_one_marker passes '- ', '* ', '+ ' prefixed values, a plain value, and '-5% latency ...' and asserts exactly one '- ' marker each with the hyphen-content value intact; LIST_MARKER_RE requires whitespace after the marker and strips once; test_roadmap_v4.py ran 15 tests OK; Decisions made states the purpose and 'out-of-scope paths changed: none', matching the five changed paths, all of which are in card scope.
```

## Retrospective


## Promotion decision
