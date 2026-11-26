---
id: W-00000424
title: 두 번 이상 본 규칙 후보 여섯 줄을 규칙 파일에 넣는다
kind: documentation
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/operations,stage/skills,.stage/operations,.stage/state/rule-candidates.md,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000424 두 번 이상 본 규칙 후보 여섯 줄을 규칙 파일에 넣는다

## Purpose

두 번 이상 되풀이된 실수 여섯 가지가 규칙 파일에 적혀서 다음 세션이 같은 실수를 하기 전에 읽는다

## Stories


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 후보 목록의 seen 2 이상 여섯 줄이 각각 rule-promotion.md 의 Where the rule goes 가 정한 규칙 파일에 출처 회고와 함께 적혀 있다
- 규칙이 된 여섯 줄이 .stage/state/rule-candidates.md 에서 빠져 있다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 에픽과 스토리 여섯 장을 등록하고 시작했다. DE-00000104 가 두 번 이상 본 줄은 사용자에게 묻지 않고 규칙이 된다고 정했다. 여섯 줄은 W-00000423 이 가져온 `.stage/state/rule-candidates.md` 의 `seen 2` 이상인 줄이다. 목적과 성공 기준은 그 줄과 `rule-promotion.md` 에서 옮겨 적었다(사용자의 위임).
- PO 스킬은 줄마다 카드 한 장을 등록하라고 한다. PO 세션이 사용자의 위임으로 에픽 한 장에 줄마다 스토리를 두고 PM 세션 하나에 맡기기로 했다. 세션 여섯 개를 띄우지 않기 위해서다. 사용자가 보고 뒤집을 수 있다.
- 여섯째 스토리(절차를 바꾼 카드는 그 길로 한 번 해 본 뒤에 닫는다)는 닫는 절차에 닿는다. DE-00000087 에 따라 닫기 전에 사용자의 확인을 받는다.
- 새 기록 번호는 잡아 두지 않았다. 이 에픽은 새 기록을 만들지 않는다.
## Verification
- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 만들기 전에 결정 둘을 올렸다. (1) 여섯 줄을 후보 목록에서 지우는 커밋의 자리: A 에픽 번호로 일곱 번째 커밋 하나 / B 스토리마다 자기 줄을 지운다. PO 세션이 사용자의 위임으로 A 를 골랐다. (2) W-00000430 에서 닫기 전에 해 볼 수 없는 절차: A 예외 없이 해 본 증거가 생길 때까지 카드를 열어 두고 코드는 먼저 병합할 수 있다 / B 닫고 어느 다음 카드가 시험인지 적는다. 사용자가 A 를 골랐다("A로 하죠 추천대로"). 닫는 절차를 바꾸는 선택이라 DE-00000087 에 따라 사용자에게 물었다.
- PM 세션이 규칙의 자리를 알렸다: 425, 427, 428 은 `stage/skills/stage-work/SKILL.md`, 426 은 `stage/operations/output.md`, 429 는 `stage/operations/review.md`, 430 은 `stage/operations/verification.md`. PO 세션이 그대로 두라고 했다.
