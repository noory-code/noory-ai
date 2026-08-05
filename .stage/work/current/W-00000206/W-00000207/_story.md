---
id: W-00000207
title: 등록이 목적부터 캐내는 순서로 바뀐다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000205
promotion: not_applicable
review: not_required
scope: stage/skills/stage-work/SKILL.md, stage/docs/PHILOSOPHY.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000207 등록이 목적부터 캐내는 순서로 바뀐다

## Purpose

등록 스킬이 규모부터 판단하라고 시작하고 목적은 그 뒤에 상위 문서에서 찾으라고만 해서 캐내는 자리가 통째로 비어 있으므로, 캐내는 절차를 첫 절로 올리고 규모와 범위를 그 뒤로 내린다

## Actions

없음 — 절차를 쓰는 것과 순서를 옮기는 것이 같은 파일의 같은 자리다.

## User value

등록 스킬을 처음 여는 사람이 "무엇을 하고 싶은지부터 묻는다"를 첫 줄에서 읽는다. 지금은
"얼마나 큰 일인가부터 물어라"를 읽는다.

## Scope

### Included

- 캐내는 절차를 스킬의 첫 절로 쓴다. 여러 번 묻고, **셋을 지어내지 않고 쓸 수 있을 때** 멈춘다 —
  무엇을 이루려는지 한 문장, 어느 큰 성취에 닿는지, 끝났다는 걸 무엇으로 아는지.
- 규모 판단을 그 뒤로 내린다. 목적을 모르는 채로 크기를 재면 눈에 보이는 고장의 크기를 재게 된다.
- "상위 문서에서 목적을 찾아라, 짐작 금지" 한 줄을 고친다. 상위 문서는 목적을 확인하는 자리이지
  캐내는 자리가 아니고, 없을 때 무엇을 할지가 지금 비어 있다.
- 철학 문서의 §일감은 사용자의 의도에서 나온다 에 그 절차를 가리키는 줄을 넣는다. 철학은 받으라고
  말하고 절차는 어떻게 받는지 말한다.

### Excluded

- 등록 카드에 칸을 새로 안 만든다.
- 그 순서를 무엇이 강제하는지는 안 정한다. W-00000208 이 정한다.

## Risks

- **이 카드만으로는 사용자가 정한 끝나는 자리를 못 넘는다.** 적혀 있어도 내가 안 읽으면 그만이다.
  마일스톤의 "적혀 있다"는 기준은 채우지만, "다음에 실제로 다르게 행동한다"는 208 몫이다.
- 절차를 길게 쓰면 안 읽힌다. 스킬은 이미 200줄이 넘는다.

## Success criteria

- 스킬을 처음부터 읽는 사람이 목적을 캐내는 것을 규모 판단보다 먼저 만난다.
- 상위 문서가 없을 때 무엇을 해야 하는지가 적혀 있다.
- 언제 그만 묻는지가 적혀 있고, 그 기준이 사람의 인내심이 아니라 받은 답으로 정해진다.
- 철학 문서와 스킬이 서로를 가리키고 같은 셋을 말한다.

## Next action

스킬의 첫 절을 캐내는 절차로 바꾸고, 규모 판단을 그 뒤로 옮긴다.

## Related truth


## Progress

스킬의 첫 절이 "규모부터 판단하라"에서 "무엇보다 먼저 목적을 캐낸다"로 바뀌었다. 규모 판단은
그 뒤 절로 내려갔다.

절차에 적은 것: 셋이 다 채워질 때까지 묻는다, 한 번 물어서는 안 나온다(첫 답은 증상이다),
멈추는 기준은 사람의 인내심이 아니라 받은 답이다, 저장소 기록으로 빈칸을 안 채운다,
상위 문서는 목적을 확인하는 자리이지 공급하는 자리가 아니다.

스킬의 설명 줄도 고쳤다. 그 줄이 이 스킬을 언제 꺼내는지를 정하므로, "뭐가 안 돼요"도 이
스킬을 부르는 말이라고 적었다.

철학 문서에 같은 순서를 넣고 스킬을 가리키게 했다 — 철학은 "셋을 받아라"를, 스킬이 "어떻게
받나"를 소유한다.

**이 카드로는 사용자가 정한 끝나는 자리를 못 넘는다.** 적혀 있어도 내가 안 읽으면 그만이다.
W-00000208 몫이다.

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
Ran 361 tests in 1.405s

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
[W-00000001] completed on stage/driver/W-00000001-1785917878
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785917878. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp1x6u8bfo/unattended/W-00000001-1785917878
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
Ran 577 tests in 93.118s

OK
```

## Retrospective

R-00000205.

## Promotion decision

승격 경로 없음.
