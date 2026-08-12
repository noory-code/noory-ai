---
id: W-00000260
title: 드라이버를 돌리기 전에 작업 트리를 비우라는 것을 규칙에 넣는다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000260
promotion: not_applicable
review: not_required
scope: stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000260 드라이버를 돌리기 전에 작업 트리를 비우라는 것을 규칙에 넣는다

## Purpose

드라이버를 돌리기 전에 남아 있던 파일과 도는 동안 사람이 쓴 파일이 실행자 몫으로 섞여 판이 통째로 버려지는데 규칙 문서가 도는 동안만 말하고 시작 전 상태도 버려진다는 손해도 안 말하므로 그 둘을 규칙에 넣는다

## Actions

없음 — 이미 있는 규칙 한 문단을 고치는 한 덩어리다.

## User value

버려지는 판이 줄어든다. 판 하나가 버려지면 실행자 시간이 통째로 날아가고, 실패 메시지가
파일 목록만 늘어놓아서 원인을 찾는 데 또 시간이 든다.

## Scope

### Included

**고칠 자리는 `stage/skills/stage-drive/SKILL.md` 의 한 문단이다.** 지금 이렇게 적혀 있다.

> Do not edit files, stage or commit changes, switch branches, or run other repository-changing Git
> commands in the same checkout while a driver step is running. ... Wait for the step to stop
> before changing the repository.

**모자란 것이 둘이다.**

| 모자란 것 | 그래서 무슨 일이 났나 |
|---|---|
| **시작 전 상태를 안 말한다** | 돌리기 전에 남겨 둔 파일도 섞인다. 사람이 만든 관찰 기록 둘을 커밋 안 하고 돌렸더니 실행자가 그것을 자기가 바꾼 것으로 신고했다 |
| **안 지켰을 때의 결과를 안 말한다** | "shared process-wide state" 라고만 하니 읽는 사람이 무엇을 잃는지 모른다. 실제로는 신고한 목록과 관측한 목록이 안 맞아 **그 판이 통째로 버려진다** |

- 두 가지를 그 문단에 넣는다. 새 문단을 만들지 않는다 — 같은 행동을 다루는 규칙이 이미 그
  자리에 있다.
- **어느 회고에서 왔는지 규칙 옆에 적는다.** `R-00000248` 과 `R-00000259` 다.
- 변경 기록에 줄을 넣는다.

### Excluded

- 드라이버 코드는 안 건드린다. 실행자가 자기 변경과 남의 변경을 가릴 수단이 없다는 것은
  `O-00000013` 이 갖고 있다. 이 카드는 규칙 문서만 고친다.
- 되돌리기 명령이 지난 판정을 안 지우는 것(`O-00000047`)은 다른 문제다.

## Risks

- **문서만 고치면 다음에도 밟을 수 있다.** 규칙을 읽는 것은 사람이고, 오늘 그 규칙을 적은
  사람이 바로 다음 카드에서 밟았다. 다만 지금 문단은 시작 전 상태를 아예 안 말하므로,
  읽어도 안 걸리는 상태다.


## Success criteria

- 드라이버를 돌리기 전에 작업 트리를 비워야 한다는 것이 규칙에 적혀 있다
- 안 지키면 그 판이 버려진다는 결과가 규칙에 적혀 있다
- 그 규칙이 어느 회고에서 왔는지 규칙 옆에 적혀 있다

## Next action

**`stage/skills/stage-drive/SKILL.md` 에서 `Do not edit files, stage or commit changes` 로
시작하는 문단을 연다.** `## One `--execute` step` 절 안, 감독이 하는 일을 설명하는 대목
바로 아래다.

**그 문단을 고친다.** 새로 넣을 것은 둘이다.

- 돌리기 전에 작업 트리를 비운다 — 커밋 안 된 변경이 남아 있으면 안 된다.
- 안 지키면 그 판이 버려진다 — 실행자가 신고한 변경 경로와 드라이버가 관측한 것이 안 맞기
  때문이다.

**규칙 옆에 출처를 적는다.** `R-00000248`, `R-00000259`. 규칙 승격 절차
(`stage/skills/stage-retrospective/rule-promotion.md`)가 출처 없는 규칙을 금지한다.

**문서 언어는 영어다.** `stage/CLAUDE.md` 가 스킬을 계약 문서로 분류한다.

## Related truth

- `R-00000259` — 규칙 후보를 3회차로 올린 회고. 무엇이 두 판을 태웠는지가 거기 있다.
- `R-00000248` — 같은 것을 2회차 후보로 적은 회고. 그것을 적은 사람이 다음 카드에서 밟았다.
- `O-00000013` — 실행자가 자기 변경과 남의 변경을 못 가린다는 관찰. 이 카드가 안 고치는 쪽이다.
- `stage/skills/stage-retrospective/rule-promotion.md` — 후보를 규칙으로 올리는 절차. 새로
  덧붙이기보다 있는 규칙을 고치라고 하고, 출처를 반드시 적으라고 한다.

## Progress


## Verification

**합격 검사(`python3 stage/scripts/audit_stage.py`)는 이 카드를 못 가린다.** errors=0,
warnings=32 로 통과했지만, 그 스크립트는 `.stage/` 만 읽고 `stage/skills/` 는 한 번도 안 연다
(`grep -c skills stage/scripts/audit_stage.py` → 0). 고침을 되돌려도 똑같이 통과한다. 그래서
아래는 고친 문단을 그대로 놓고 기준 셋을 하나씩 맞춰 본 것이다.

`stage/skills/stage-drive/SKILL.md` 의 고친 문단:

> Start every driver step from a clean working tree — commit or stash uncommitted changes before
> launching it. While a step is running, do not edit files, stage or commit changes, switch
> branches, or run other repository-changing Git commands in the same checkout. The executor
> receives a disposable Git index, so its `git add` cannot change the human's real index, but the
> working tree and `HEAD` remain shared process-wide state. Either violation discards the whole
> attempt: the driver compares the change paths the executor reports against what it observes in
> the checkout, and a file the executor never touched — left over from before the step, or written
> by a person during it — makes those two lists disagree. The run is thrown away even when the
> executor's own work was correct. Wait for the step to stop before changing the repository.
> (R-00000248, R-00000259)

| 기준 | 어디서 서는가 |
|---|---|
| 돌리기 전에 작업 트리를 비운다 | 첫 문장 — `Start every driver step from a clean working tree — commit or stash uncommitted changes before launching it.` 시점이 `before launching it` 으로 못 박혀서, 도는 동안을 다루는 뒷문장과 안 섞인다 |
| 안 지키면 그 판이 버려진다 | `Either violation discards the whole attempt` 과 그 뒤 두 문장. 왜 버려지는지(신고한 경로와 관측한 경로가 안 맞는다)와, 실행자 일이 옳아도 버려진다는 것까지 적었다 |
| 출처가 규칙 옆에 있다 | 문단 끝 `(R-00000248, R-00000259)`. 같은 파일 207~221 줄이 쓰는 인용 형식과 같다 |

새 문단을 안 만들고 있던 문단을 고쳤다. 변경 기록에는 무엇이 늘었고 이제 무엇까지 덮는지를
적었다(`stage/CHANGELOG.md` `## Unreleased`). 매니페스트 버전은 안 건드렸다.

### Executed at close — 2026-08-12

```
$ python3 stage/scripts/audit_stage.py
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

$ python3 stage/scripts/audit_stage.py
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

## Retrospective


## Promotion decision
