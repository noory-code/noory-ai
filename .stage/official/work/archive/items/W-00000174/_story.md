---
id: W-00000174
title: 커밋하는 자리도 쓰는 자리와 같은 규칙을 따르게 한다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000174
promotion: not_applicable
review: not_required
scope: stage/hooks/, stage/skills/stage-handoff/SKILL.md, stage/skills/stage-archive/SKILL.md, stage/docs/, stage/operations/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000174 커밋하는 자리도 쓰는 자리와 같은 규칙을 따르게 한다

## Purpose

DE-00000052 가 카드의 파일 목록을 담장에서 신호로 내렸다. 목록 밖 파일을 쓰는 것은 이제 통과한다.
**그런데 그것을 커밋하려 하면 여전히 거절당한다.**

2026-07-31, 감독자가 목록 밖 파일 한 문장을 고쳤다. 쓰기는 통과했고 커밋은 막혔다. 목록을
넓히면 넘었다는 기록이 사라지므로(O-00000020) 그 수정을 버렸다.

**만든 쪽은 목록 밖 일을 하라는 말을 듣고 실제로 할 수 있는데, 그 결과를 남길 수 없다.** 계약이
반쪽만 서 있다. 결정이 고칠 자리를 여덟 세었는데 커밋 검사가 그 목록에 없었다.

## Actions

- 커밋 검사가 쓰기 검사와 같은 규칙을 따르게 한다 — 열린 일이 하나도 없으면 막고, 목록 밖은
  통과시킨다.
- **끝난 일의 파일을 커밋하려는 것은 계속 막는다.** 지금 커밋 검사가 하는 다른 일이고, 이 결정과
  상관없다.
- 커밋할 때도 넘었다는 것이 보이게 한다. 쓰기 때는 보인다.
- 설명 문서 셋에서 목록을 막는 것으로 적어 둔 문장을 고친다.
- 위를 고정하는 시험.

## User value

목록 밖에서 한 일을 남길 수 있다. 지금은 하라고 해 놓고 결과를 버리게 한다.

## Scope

### Included

- 커밋 검사와 그 설명, 시험.
- 목록을 막는 것으로 적어 둔 문장들.

### Excluded

- 만든 쪽이 카드의 목록을 스스로 넓히는 것(O-00000020). 따로 정한다.
- 규칙을 새로 정하는 일. DE-00000052 가 정한 것을 옮긴다.

## Risks

- **끝난 일의 파일을 커밋하려는 것을 막는 동작을 같이 풀면 안 된다.** 커밋 검사가 두 가지를
  보는데 하나만 바꿔야 한다. 여기가 제일 위험하다.
- 등록된 일이 하나도 없을 때 막는 것도 그대로 있어야 한다.

## Success criteria

- 열린 일이 있는 상태에서 목록 밖 파일을 커밋하면 통과한다.
- 열린 일이 하나도 없으면 커밋이 여전히 막힌다.
- 끝난 일인데 회고나 승격이 안 끝난 카드의 파일을 커밋하려 하면 여전히 막힌다.
- 설명 문서에 목록이 커밋을 막는다고 적힌 곳이 없다.
- 사람이 겪는 결과: 목록 밖 파일을 고친 뒤 목록을 안 넓혀도 커밋된다.

## Next action

`stage/hooks/stage_work.py` 의 커밋 검사가 두 가지를 어떻게 같이 보는지 읽는다.

## Related truth

- DE-00000052 가 규칙을 소유한다. 이 카드는 안 옮겨진 자리 하나를 옮긴다.
- O-00000022 가 이 문제를 기록했다.

## Progress

## Verification

### Executed at close — 2026-07-31

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.289s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.285s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (203 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785488414
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785488414. Human review + merge required; the base branch was not modified.
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
Ran 514 tests in 78.949s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
