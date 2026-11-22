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

고친 스킬로 새 세션이 인수인계를 다시 해 보게 하고(세 번째 성공 기준), 통과하면 닫는다.

- Waiting on user: 검증 세션의 판정이 `close_work.py` 의 닫기 리뷰를 대체하는가, 둘 다 두는가? (추천: 둘 다 두고 W-00000401 에서 정한다)
- Waiting on user: 세션 태그 `stage-project:<repository>` 와 `stage-orchestrator` 를 새 규약으로 써도 되는가?

## Related truth

## Progress

- 2026-11-22 작업 세션 session_018VXR6SeAeMrUHEGhh8myKi 가 214667e 를 보고했다. 성공 기준 1, 2 를 주장했다.
- 2026-11-22 시험 세션 session_018VXR6RJwybKUJRATYqvEuM 이 스킬만으로 인수인계를 했다. 카드와 확인은 찾았지만 스킬의 빈 곳 열한 가지(A–K)를 보고했다.
- 2026-11-22 작업 세션이 29e2cf9 로 A–K 를 고쳤다(`started_cards.py` 추가). 메인 세션에서 scripts 907, hooks 467 통과.

## Verification
