---
id: W-00000425
title: 규칙: 기록의 자리나 배치를 바꾸는 변경은 그 자리를 읽는 코드와 화면의 테스트부터 센다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000425
promotion: pending
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000425 규칙: 기록의 자리나 배치를 바꾸는 변경은 그 자리를 읽는 코드와 화면의 테스트부터 센다

## Purpose

기록의 자리를 옮기는 세션이 그 자리를 읽는 코드와 화면의 테스트를 먼저 센다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000241 과 R-00000373 을 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `2b4bca6` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
## Verification

2026-11-26 PO 세션이 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 커밋 `2b4bca6` 의 것이다.
