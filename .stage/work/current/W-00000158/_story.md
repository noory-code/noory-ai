---
id: W-00000158
title: 카드가 저장하는 검사 명령을 좁게 고르는 규칙을 적는다
kind: documentation
venue: claude
milestone:
source:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000158
promotion: not_applicable
review: not_required
scope: .stage/decisions/pending/, stage/skills/stage-work/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000048
---

# W-00000158 카드가 저장하는 검사 명령을 좁게 고르는 규칙을 적는다

## Purpose

카드에는 그 일이 끝났는지 확인하는 명령을 저장한다. 드라이버는 일을 시킨 뒤 그 명령을 직접 다시
돌린다. 그런데 오늘 만든 카드 셋이 전부 같은 명령을 저장했다 — 전체 시험 두 묶음과 감사.

시험 전체가 도는 데 80초 걸린다(실측). 드라이버가 한 바퀴 돌 때마다 그 값을 내고, 판정이 막혀서
두 바퀴를 돌면 두 번 낸다. 오늘 W-00000155 가 그랬다.

카드 작성 절차 문서에는 **어떤 명령을 저장할지에 대한 말이 한 줄도 없다.** 그래서 쓰는 사람이
"다 돌리면 안전하다"로 기울고, 그 선택을 아무도 안 잡는다.

같은 자리에서 계층 이야기도 정리가 필요하다. 스토리를 액션으로 쪼개면 다시 돌 때 일부만 돈다.
그런데 오늘 한 번 막힌 것은 크기 탓이 아니라 고칠 자리를 하나 빠뜨린 탓이었고, 쪼갰어도 똑같이
났을 일이다. 쪼개기를 규칙으로 만들 근거가 아직 없다.

## Actions

- 결정 기록을 쓴다. 정할 것 둘: 카드가 저장하는 명령은 그 카드의 결과를 집는 좁은 것으로 한다.
  전체 시험은 카드를 닫을 때 한 번 돌린다.
- 그 두 층이 무엇을 잡고 무엇을 못 잡는지 결정에 적는다. 좁은 명령은 다른 데가 깨진 것을 못 잡고,
  그것은 닫을 때 드러난다.
- 액션으로 쪼개는 것은 규칙이 아니라 선택지로 남긴다는 것도 함께 적는다. 근거는 오늘 실측이다.
- 카드 작성 절차 문서에 명령 고르는 규칙을 넣는다. 지금 그 문서는 카드 본문이 답해야 할 네 가지는
  적어 두었지만, 명령에 대해서는 "없으면 드라이버가 거절한다"만 말한다.

## Scope

바꾸는 것은 결정 기록 하나, 카드 작성 절차 문서, 릴리스 노트다.

바꾸지 않는 것: 드라이버 코드. 닫을 때 넘기는 명령과 저장된 명령을 둘 다 돌리는 동작이 이미
있으므로(이 카드가 그 방식으로 돈다), 규칙만 적으면 된다.

## Success criteria

- 결정이 두 층을 나누고, 각 층이 무엇을 못 잡는지 밝힌다.
- 액션 쪼개기를 강제하지 않는 이유가 오늘 실측과 함께 적혀 있다.
- 카드 작성 절차 문서를 읽고 명령을 고를 수 있다 — 무엇을 저장하고 무엇을 닫을 때 넘길지.
- 사람이 겪는 결과: 이 카드 자체가 새 규칙대로 돌아간다. 저장한 명령은 감사 하나뿐이고, 전체
  시험은 닫을 때 한 번 돈다.

## Related truth

- 카드 작성 절차: `stage/skills/stage-work/SKILL.md`
- 드라이버가 저장된 명령을 다시 돌리는 계약: `stage/skills/stage-drive/SKILL.md`
- 오늘 두 바퀴를 돈 카드: W-00000155 와 그 회고 R-00000155

## Progress

## Verification

### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

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
[W-00000001] completed on stage/driver/W-00000001-1785417755
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785417755. Human review + merge required; the base branch was not modified.
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
Ran 511 tests in 76.630s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 350 tests in 1.070s

OK
```

## Retrospective

## Promotion decision
