---
id: W-00000417
title: 세션 시작의 고정 규칙 문장을 줄여 색인의 자리를 만든다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_context.py,stage/hooks/stage_memory_index.py,stage/hooks/tests,stage/hooks/README.md,stage/operations/hooks.md,.stage/operations/session-hooks.md,.stage/research/memory-layers,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000417 세션 시작의 고정 규칙 문장을 줄여 색인의 자리를 만든다

## Purpose

세션 시작 글에서 매번 같은 규칙 문장이 차지하던 자리가 줄어서, 진행 중인 카드가 여러 장이어도 결정 제목이 색인에서 빠지지 않는다 (DE-00000100)

## Actions


## User value


## Scope

### Included


### Excluded

- 훅이 막는 동작을 바꾸는 일.
- 상한 10,000자를 바꾸는 일. 줄여도 기준을 채울 수 없으면 그렇다고 보고한다.


## Risks


## Success criteria

- 세션 시작 글의 고정 규칙 문장이 지금보다 1,500자 넘게 줄고, 덜어낸 문장마다 그 내용을 이미 말하는 자리(훅의 거부 문구, 스킬, 운영 문서)가 연구 자료에 적혀 있다
- 진행 중인 카드 다섯 장과 규칙 후보 39건이 있는 상태에서 이 저장소의 결정 제목이 모두 실린다
- 훅이 막는 동작과 거부할 때 내는 문구는 바뀌지 않았다

## Next action

작업 세션 session_018VXR6RJNk1s8m8M3F7rQwV 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.


## Related truth

- `.stage/research/memory-layers/measurements.md`: 세션 시작 글의 68% 가 매번 같은 규칙 문장과 경로 목록이다(규칙 문장 3,373자).
- W-00000409, W-00000410, W-00000413: 색인의 여유가 40자였고, 진행 중 카드 다섯 장과 규칙 후보 39건이 있을 때 결정 제목 82건 가운데 63건이 실렸다.
- M-00000006 의 (가): 하중을 확인하지 못한 장치는 덜어낸다. 이 문장들의 하중은 잰 적이 없다. 클라우드 세션은 이 글을 받지 않고 브리핑의 색인만 받는다.
- 사용자가 2026-11-23 에 실기기에서 해야 할 일만 두고 나머지를 진행하라고 했다("실기기에서 해야할 일은 두고 나머지는 합시다"). 목적과 성공 기준은 지휘 세션이 옮겨 적었다.


## Sessions

- session_018VXR6RJNk1s8m8M3F7rQwV — work — 2026-11-23 — opened from the index: not reported yet


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 2401aebb 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6RJNk1s8m8M3F7rQwV (`claude/w417-shrink-rule-text`)를 띄웠다. 번호 묶음은 잡지 않았다.


## Verification
