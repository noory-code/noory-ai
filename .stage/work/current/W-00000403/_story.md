---
id: W-00000403
title: 실행 방식 지시(B11)를 빼 보고 하중을 본다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-drive,stage/templates,.stage/settings.json,stage/CHANGELOG.md,.stage/research/claude-fit
promotes:
decision_refs:
---

# W-00000403 실행 방식 지시(B11)를 빼 보고 하중을 본다

## Purpose

실행자에게 일하는 절차를 지시하던 문장 없이 드라이버가 돌고, 그 장치가 받던 하중이 있었는지 기록으로 안다 (DE-00000098)

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage-drive 스킬과 실행자 프롬프트에서 일하는 절차를 지시하는 문장이 빠지고, 시간 제한과 보고 계약은 남아 있다
- 뺀 뒤 돈 카드들의 Driver failure, 리뷰 FAIL, 재시도를 빼기 전과 비교한 결과가 연구 자료에 있다

## Next action

작업 세션 session_018VXR6PA9aonbDLPim8LtfB 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.

- Waiting on user: 둘째 성공 기준은 B11 을 뺀 뒤에 돈 카드가 있어야 채워진다. 뺀 뒤 카드 몇 장을 보고 비교하면 이 카드를 닫는가?

## Related truth

- DE-00000098

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 99f82735 에서 카드를 시작하고 작업 세션 session_018VXR6PA9aonbDLPim8LtfB (`claude/w403-drop-execution-instructions`)를 띄웠다. 번호 묶음은 잡지 않았다.

## Verification
