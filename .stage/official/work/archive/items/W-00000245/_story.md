---
id: W-00000245
title: 회고의 배움이 규칙이 되는 절차를 만든다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000241
promotion: not_applicable
review: not_required
scope: .stage/operations/, stage/skills/stage-retrospective/, stage/skills/stage-work/, stage/skills/stage-decision/, stage/templates/, stage/scripts/drive.py, stage/docs/, stage/CHANGELOG.md, .stage/decisions/, .stage/work/retrospectives/
promotes:
decision_refs:
---

# W-00000245 회고의 배움이 규칙이 되는 절차를 만든다

## Purpose

회고 238장 중 217장에 다음에 무엇을 바꿔야 하는지 적혀 있는데 규칙 파일 셋이 그중 하나도 인용하지 않아 배움이 그 자리에 묻히므로, 무엇을 규칙으로 올릴지 가르는 기준과 올리는 절차를 만들고 지금 쌓인 것을 그 기준으로 훑는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 무엇을 규칙으로 올릴지 가르는 기준이 규칙 파일에 있고 반복된 것만이 아니라 한 번이라도 큰 것을 올린다
- 쌓인 217장을 그 기준으로 훑어 뽑은 것이 규칙 파일에 들어가 있다
- 이 카드가 더하거나 고치는 규칙 한 줄마다 어느 회고에서 나왔는지 가리킨다
- 다음에 회고를 닫을 때 이 절차를 어디서 밟는지가 회고 스킬에 적혀 있다

## Next action


## Related truth


## Progress


## Verification


### Executed at close — 2026-08-07

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (295 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1786096303
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786096303. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp7ouj8wl0/unattended/W-00000001-1786096303
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
Ran 604 tests in 103.454s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.418s

OK
```

## Retrospective


## Promotion decision
