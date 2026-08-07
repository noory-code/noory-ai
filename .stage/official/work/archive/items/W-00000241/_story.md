---
id: W-00000241
title: 드라이버를 책임별로 나눈다
kind: development
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q -k Drive"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000243
promotion: not_applicable
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/CHANGELOG.md, .stage/decisions/
promotes:
decision_refs: DE-00000067
---

# W-00000241 드라이버를 책임별로 나눈다

## Purpose

드라이버가 한 파일에 3,952줄로 들어 있어 서로 다른 카드가 같은 파일을 고칠 때마다 남의 코드를 피해 다녀야 하므로, 책임별로 나눠 한 카드가 한 자리만 만지게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 드라이버의 어느 파일도 1,000줄을 넘지 않고 965개 테스트가 그대로 통과한다
- 한 파일을 열었을 때 그 파일이 무슨 책임을 지는지 파일 이름만으로 말할 수 있다

## Next action

## Related truth

## Progress

## Verification

### Executed at close — 2026-08-07

```
$ python3 -m unittest discover -s stage/scripts/tests -q -k Drive
[exit 0]
... (81 earlier lines omitted)
Path(os.environ['"'"'STAGE_REVIEW_VERDICT_FILE'"'"']).write_text(
    json.dumps({'"'"'criteria'"'"': [{'"'"'criterion'"'"': '"'"'criterion'"'"', '"'"'verdict'"'"': '"'"'PASS'"'"', '"'"'reason'"'"': '"'"'test reviewer inspected the inputs'"'"'}], '"'"'approved'"'"': True}), encoding='"'"'utf-8'"'"')
print('"'"'APPROVED'"'"')'
Attempt: 1/unlimited
Iteration: 1/unlimited
Execution time: 0s/unlimited
WARNING: preflights.codex is not configured; continuing without a venue health check
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmplcbcab2f/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmplcbcab2f/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
Removed worktree and branch for W-00000001
Removed worktree and branch for W-00000001
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpmvo6cgb_/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpmvo6cgb_/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000003: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpmvo6cgb_/worktrees/W-00000003
Merge branch: stage/worktree/W-00000003
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp34fyu7ar/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp34fyu7ar/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp9d2nhxor/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp9d2nhxor/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
----------------------------------------------------------------------
Ran 124 tests in 33.691s

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
[W-00000001] completed on stage/driver/W-00000001-1786101656
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786101656. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpslt5fqqz/unattended/W-00000001-1786101656
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
Ran 604 tests in 100.953s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 364 tests in 1.373s

OK
```

## Retrospective

## Promotion decision
