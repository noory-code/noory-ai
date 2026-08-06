---
id: W-00000227
title: 팀원 워크트리 자리를 무시 목록에 넣는다
kind: chore
venue: codex
milestone:
autonomous: true
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000226
promotion: not_applicable
review: passed
scope: .gitignore
promotes:
decision_refs:
---

# W-00000227 팀원 워크트리 자리를 무시 목록에 넣는다

## Purpose

팀원 실행이 만드는 워크트리 디렉터리가 저장소에 추적 안 된 채로 남아 커밋할 때마다 걸리적거리므로, 그 자리를 무시 목록에 넣는다

## Actions

없음 — 무시 목록에 한 줄 더하는 일이다.

## User value

팀원 실행을 한 번 돌릴 때마다 `.claude/worktrees/` 아래가 추적 안 된 항목으로 뜬다. 커밋할
때마다 눈으로 걸러야 하고, 실수로 담으면 남의 작업 사본이 저장소에 들어간다.

## Scope

### Included

- `.gitignore` 에 `.claude/worktrees/` 를 더한다. 같은 파일이 이미 `.claude/` 아래 두 자리를
  무시하고 있으므로 그 옆에 둔다.

### Excluded

- 다른 무시 규칙은 안 건드린다.
- 이미 만들어진 워크트리를 지우지 않는다. 정리는 사람이 한다.

## Risks

- 없다. 한 줄 추가이고, 되돌리기는 그 줄을 지우는 것이다.


## Success criteria

- 팀원 워크트리가 있어도 git status 에 추적 안 된 항목으로 안 뜬다
- 기존 무시 규칙은 그대로 남는다

## Next action


## Related truth


## Progress


## Verification


### Executed at close — 2026-08-06

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

### Independent review at close — 2026-08-06

```
Review report: .stage/.runtime/driver/logs/W-00000227.md
```

## Retrospective


## Promotion decision
