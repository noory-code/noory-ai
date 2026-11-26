---
id: W-00000421
title: 규칙 후보는 두 번 보면 묻지 않고 규칙이 되고, 한 번 본 것은 사람이 잡은 것만 사용자가 판정한다
kind: development
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
scope: stage/skills/stage-retrospective/rule-promotion.md,stage/skills/stage-retrospective/SKILL.md,stage/skills/stage-orchestrate/SKILL.md,stage/hooks/stage_memory_index.py,stage/hooks/stage_context.py,stage/hooks/README.md,stage/hooks/tests,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/operations/cloud-execution.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs: DE-00000104
---

# W-00000421 규칙 후보는 두 번 보면 묻지 않고 규칙이 되고, 한 번 본 것은 사람이 잡은 것만 사용자가 판정한다

## Purpose

회고의 규칙 후보가 사용자 판정 0건인 채 쌓이지 않고, 두 번 본 것은 규칙이 되고 한 번 본 것은 사람이 잡은 것만 사용자에게 온다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- rule-promotion.md 의 둘째 시험이 사람이 잡은 것이나 병합·릴리스 뒤에 드러난 것을 들고, 닫기 리뷰어와 CI 가 잡은 것은 뺀다
- 회고가 스스로 두 번째라고 적은 후보는 두 번 본 것으로 센다
- 세션 색인이 proposed: promote 줄과 나머지 후보의 수를 싣는다
- 두 번 본 줄은 사용자 판정 없이 규칙이 되고 한 번 본 줄은 판정을 기다리며, PO 스킬은 한 번 본 것의 표와 집계 한 줄만 사용자에게 보인다
- 누가 잡았는지 적지 않은 한 번짜리 후보는 hold 다

## Next action

## Related truth

## Sessions

- session_018VXR6NLyvitbSjC79DvT8T — pm — 2026-11-26 — opened from the index: DE-00000104

## Progress

- 2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 문턱은 사용자가 2026-11-25 에 정했고 DE-00000104 에 적었다. 성공 기준 다섯 줄은 토론 세션의 초안이고 사용자가 PO 세션에서 그대로 진행하라고 했다("네"). 고칠 자리는 DE-00000104 의 "Where this applies" 에 있다.
- 범위 밖: `.stage/state/rule-candidates.md` 에 새 문턱을 적용하는 일(다음 카드), 올린 규칙을 빼는 방법.
- 새 브리핑(`--po-session`, `--role pm`)으로 뜨는 첫 PM 세션이다.
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-26 PM 세션 session_018VXR6NLyvitbSjC79DvT8T 가 만들기 전에 결정 하나를 올렸다: 사용자가 올리지 않는다고 판정한 한 번짜리 줄은 목록에서 어떻게 되는가. 선택지는 A `proposed: hold` 로 내리고 `user declined <날짜>` 를 적는다(PM 의 추천), B 목록에서 뺀다, C 이 카드에서는 정하지 않는다. PO 세션이 사용자의 위임("왠만하면 니 추천을 따를 테니까 쭉쭉 진행해라")으로 A 를 골랐다. DE-00000104 가 문턱 아래의 후보를 목록에 두기로 한 것과 같은 방향이다. 사용자가 보고 뒤집을 수 있다.
- 2026-11-26 PM 세션이 카드를 두 조각(색인 코드, 규칙 문서와 브리핑)으로 나눠 전문가 서브에이전트 둘에게 맡긴다고 알렸다. 범위 밖으로 `stage/operations/retrospective.md` 34행을 고친다고 했다.

## Verification
