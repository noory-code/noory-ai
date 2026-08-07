---
id: W-00000242
title: 막는 자리 열넷을 세고 겹치는 것을 합친다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000242
promotion: not_applicable
review: not_required
scope: stage/hooks/, stage/hooks/tests/, stage/docs/, stage/CHANGELOG.md, .stage/decisions/
promotes:
decision_refs:
---

# W-00000242 막는 자리 열넷을 세고 겹치는 것을 합친다

## Purpose

훅이 막는 자리가 열넷이라 규칙을 만든 사람도 정당한 일을 하다 걸리고 왜 걸렸는지 알려면 코드를 열어야 하므로, 자리마다 무엇을 지키는지 세어 겹치는 것을 합치고 남는 것은 막을 때 다음에 뭘 하면 되는지 말하게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 열넷 각각이 무엇을 지키는지와 어느 것이 겹치는지가 한 표에 있다
- 막히는 메시지마다 다음에 무엇을 하면 되는지가 한 줄로 들어 있다

## Next action

## Related truth

## Progress

## Verification

### Executed at close — 2026-08-07

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 364 tests in 1.410s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (295 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1786096874
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786096874. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp912aq743/unattended/W-00000001-1786096874
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
Ran 604 tests in 103.752s

OK
```

## Retrospective

## Promotion decision
