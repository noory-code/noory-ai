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

## Related truth

## Progress

## Verification
