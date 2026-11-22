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

닫고 PR #107 을 머지한다.

## Related truth

## Progress

- 2026-11-22 작업 세션 session_018VXR6SeAeMrUHEGhh8myKi 가 214667e 를 보고했다. 성공 기준 1, 2 를 주장했다.
- 2026-11-22 시험 세션 session_018VXR6RJwybKUJRATYqvEuM 이 스킬만으로 인수인계를 했다. 카드와 확인은 찾았지만 스킬의 빈 곳 열한 가지(A–K)를 보고했다.
- 2026-11-22 작업 세션이 29e2cf9 로 A–K 를 고쳤다(`started_cards.py` 추가). 메인 세션에서 scripts 907, hooks 467 통과.
- 2026-11-22 작업 세션이 159f03c 로 남은 여덟 가지를 고쳤다. 메인 세션에서 scripts 908, hooks 467 통과, PR #107 의 CI 30개 통과.
- 2026-11-22 사용자가 지휘자 교체 규칙을 승인했다("네 이대로 가죠"): 새 지휘자는 사용자가 지명하고, 이전 세션이 답이 없으면 사용자 확인 뒤 새 세션이 그 태그를 뗀다.
- 2026-11-22 사용자가 세션 태그 `stage-project:<owner>/<repository>` 와 `stage-orchestrator` 를 승인했다("네 그대로 쓰죠").
- 2026-11-22 사용자가 검증 세션의 판정과 닫기 리뷰를 둘 다 두고, 하나로 합칠지는 W-00000401 에서 정하기로 했다("네 추천대로 가죠"). 그때까지 검증 세션은 에픽에만 띄우고 스토리는 닫기 리뷰만 받는다.
- Follow-up candidate: `close_work.py` 가 검증 세션의 판정을 받아들이게 한다 (W-00000401 에서 다룬다).
- Follow-up candidate: 토론 세션과 계획 세션의 브리핑을 생성한다.
- Follow-up candidate: 에픽을 닫는 길(스토리별 cherry-pick)을 실제 에픽으로 해 본다.
- Follow-up candidate: 몇 번 쓴 뒤 stage-orchestrate 스킬(235줄)에서 줄일 수 있는 지시를 찾는다.

## Verification
