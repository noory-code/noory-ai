---
id: W-00000415
title: 쌓인 규칙 후보를 처음으로 한 목록에 묶는다
kind: documentation
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/state/rule-candidates.md,.stage/index.md
promotes:
decision_refs:
---

# W-00000415 쌓인 규칙 후보를 처음으로 한 목록에 묶는다

## Purpose

회고마다 흩어진 규칙 후보가 한 목록에 묶여 있어서, 같은 일이 몇 번 관찰됐는지 보고 규칙으로 올릴지를 정할 수 있다 (DE-00000100)

## Actions


## User value


## Scope

### Included

- `stage/skills/stage-retrospective/rule-promotion.md` 의 "Consolidating candidates" 가 말하는 형식을 따른다.
- O-00000061 의 규칙 후보 세 건도 넣는다.


### Excluded

- 규칙으로 실제 올리는 일. 제안까지만 한다.
- 회고와 결정의 본문을 고치는 일.


## Risks


## Success criteria

- 지금 있는 회고의 규칙 후보가 .stage/state/rule-candidates.md 에 through 와 함께 묶여 있고, 묶음마다 근거 회고와 관측 횟수가 있다
- 회고, 결정, 규칙 파일의 본문은 바뀌지 않았고, 규칙으로 올리자는 것은 제안으로만 적혀 있다

## Next action


## Related truth

- DE-00000100, W-00000409, `stage/operations/retrospective.md`
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions


## Progress


## Verification
