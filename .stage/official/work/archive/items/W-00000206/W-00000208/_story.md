---
id: W-00000208
title: 그 순서가 실제로 걸리는 자리를 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000206
promotion: promoted
review: not_required
scope: .stage/decisions/, stage/docs/, stage/CHANGELOG.md
promotes: .stage/official/decisions/index.md, .stage/official/decisions/records/DE-00000059.md
decision_refs: DE-00000059
---

# W-00000208 그 순서가 실제로 걸리는 자리를 정한다

## Purpose

스킬에 적어 두는 것만으로는 내가 읽고 안 읽고를 스스로 정해서 여덟 번 안 지켰으므로, 목적을 안 캐내고 일을 시작하면 무엇이 어디서 막을지를 결정으로 못박는다

## Actions

없음 — 결정 하나를 내리는 일이다.

## User value

다음 사람이 "이건 왜 게이트로 안 잡나"를 다시 토론하지 않는다. 무엇을 막고 무엇을 못 막는지가
한 자리에 적혀 있다.

## Scope

### Included

- 목적을 안 캐내고 시작하는 길을 무엇이 어디서 막는지 정한다.
- 기계가 못 잡는 자리를 명시한다. 잡는 척하는 게이트를 안 만든다.
- 구현 카드를 건다.

### Excluded

- 코드는 안 건드린다. W-00000209 가 한다.

## Risks

- 못 잡는 자리를 안 적으면 다음 사람이 게이트를 믿고 안 본다. 믿는 만큼 안 보는 것이 더 나쁘다.

## Success criteria

- 무엇이 거부되고 무엇이 통과하는지가 결정에 적혀 있다.
- 기계가 못 잡는 자리와 그 이유가 같은 결정에 적혀 있다.
- 구현 카드가 그 결정을 근거로 걸려 있다.

## Next action

없음 — DE-00000059 를 내렸고 W-00000209 를 걸었다.


## Related truth


## Progress

실측이 결정을 갈랐다. `--purpose` 가 선택 항목이고 기본값이 빈 문자열이라 **목적이 아예 없는
카드가 만들어진다.** 감사도 카드의 목적을 안 본다. 그 사실을 보기 전에는 "이미 묻고 있으니 더 할
게 없다"고 생각했다.

DE-00000059 가 셋을 막기로 하고, **못 잡는 자리 하나를 같은 결정에 명시했다.** 지어낸 목적은
기계가 못 잡는다. 잡는 척하면 다음 사람이 그걸 믿고 안 본다.

## Verification


### Executed at close — 2026-08-05

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.435s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (249 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785927293
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785927293. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp0c6xdo1e/unattended/W-00000001-1785927293
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
Ran 577 tests in 94.799s

OK
```

## Retrospective

R-00000206.

## Promotion decision

DE-00000059 를 공식으로 올렸다 — 앞으로의 등록을 구속한다.
