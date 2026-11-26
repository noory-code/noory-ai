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
