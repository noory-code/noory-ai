---
id: W-00000296
title: claude 리뷰어 권한에서 쓰이지 않는 Write 규칙을 뺀다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000296
promotion: not_applicable
review: passed
scope: .stage/settings.json, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/scripts/tests/test_template_v4.py, stage/templates/v4/project-stage/settings.jsonc, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000296 claude 리뷰어 권한에서 쓰이지 않는 Write 규칙을 뺀다

## Purpose

리뷰 명령이 쓰이지 않는 권한 규칙 때문에 매번 경고를 남기지 않고, 권한 설명이 실제로 쓰기를 허락하는 규칙과 맞게 한다.

## Actions

- 지금 동작: W-00000295 가 리뷰어에게 판정 파일의 `Write(...)` 와 `Edit(...)` 규칙을 함께 준다. 그 카드의 닫기에서
  Claude Code 가 "파일 권한 검사는 `Edit(path)` 규칙만 맞춘다"고 경고했고, 판정 파일은 `Edit` 규칙만으로 새로
  써졌다(R-00000295). `Write` 규칙은 쓰이지 않고 리뷰마다 경고만 남긴다.
- 프로젝트 `reviewers.claude` 명령, `claude_review_companion.py`, 두 시험, 템플릿 안내에서 `Write` 규칙을 뺀다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일에 Edit 규칙만 주고 Write 규칙을 주지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: The project's reviewers.claude command and stage/scripts/claude_review_companion.py now allow the verdict file through a single Edit(//<path>) rule instead of Write and Edit rules; both tests now expect the Edit rule alone and assert that no Write rule is passed; the settings template guidance names the Edit rule and says Edit rules govern every file write; one changelog line.
Why: W-00000296 - the reviewer's permission list should contain only rules that take effect, so it matches what actually allows the verdict write and stops warning on every review.
Decisions made: Rely on the W-00000295 close as evidence that an Edit rule alone lets a non-interactive reviewer create the verdict file, since that close ran with the Write rule ignored and still wrote a fresh verdict; keep the existing Unreleased line for W-00000295 and add a short correcting line rather than rewriting it.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `af7baa87` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 이 카드가 고친 `stage/scripts/claude_review_companion.py` 대역(`Edit` 규칙만)으로 이 프로젝트의
`implementation` 리뷰 명령을 설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 1.921s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 24 tests in 0.062s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793452110
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793452110. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpm5jlvlwy/unattended/W-00000001-1793452110
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
Ran 704 tests in 135.853s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000296.md
Criteria:
- PASS: 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일에 Edit 규칙만 주고 Write 규칙을 주지 않는다는 것을 테스트가 확인한다
  Reason: test_template_v4 runs the project reviewers.claude command against a fake claude and asserts the exact argv with only Edit(/verdict) plus assertNotIn Write( on the command; test_environment_venues asserts claude_review_companion argv has only Edit(rule) and no part starting with Write(; both suites pass (7 and 24 tests), all changed paths are within card scope, and the executor report fills Decisions made and Work not done (None) consistently with the purpose.
```

## Retrospective

[R-00000296](../../retrospectives/R-00000296.md).

## Promotion decision
