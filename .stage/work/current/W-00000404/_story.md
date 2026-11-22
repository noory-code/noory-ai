---
id: W-00000404
title: stage-orchestrate 스킬과 역할별 브리핑을 만든다
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
scope: stage/skills,stage/scripts,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000404 stage-orchestrate 스킬과 역할별 브리핑을 만든다

## Purpose

새 세션이 stage-orchestrate 스킬로 오케스트레이터가 되고, 작업 세션과 검증 세션은 생성된 브리핑으로 역할을 받는다 (DE-00000099)

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage-orchestrate 스킬이 있고 stage-handoff 의 서브세션 절과 겹치지 않는다
- 작업 세션(에픽)과 검증 세션의 브리핑을 생성할 수 있고 그것을 보이는 시험이 통과한다
- 새 클라우드 세션이 이 스킬로 오케스트레이터 역할을 맡아 진행 중인 카드와 답을 기다리는 확인을 기록과 세션 목록에서 찾아냈다

## Next action

## Related truth

## Progress

## Verification
