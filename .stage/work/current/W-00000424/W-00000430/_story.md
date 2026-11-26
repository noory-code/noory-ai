---
id: W-00000430
title: 규칙: 절차를 바꾸거나 다른 세션이 따를 새 길을 적은 카드는 그 길로 실제 일을 한 번 해 본 뒤에 닫는다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000430 규칙: 절차를 바꾸거나 다른 세션이 따를 새 길을 적은 카드는 그 길로 실제 일을 한 번 해 본 뒤에 닫는다

## Purpose

절차를 바꾼 카드가 그 절차로 실제 일을 한 번 해 본 뒤에 닫힌다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000404, R-00000418, R-00000420 을 든다
- 절차를 바꾸는 다음 카드 한 장이 이 규칙의 길(시험을 성공 기준으로 적고, 코드를 먼저 병합하고 카드를 열어 두고, 그 시험을 `- Checked` 나 `- Observed` 줄로 적은 뒤 닫는다)로 처리됐고, 그 줄이 그 카드의 `## Verification` 에 있다

## Next action

절차를 바꾸는 다음 카드를 PO 세션이 이 규칙의 길로 처리한다. 그 카드가 닫히면 PO 세션이 여기 `## Verification` 에 `- Checked` 줄을 적고 이 카드의 닫기 리뷰를 돌린다. 그 다음 에픽 W-00000424 를 닫는다.

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 커밋 둘(1386a78, 8a74c32)을 보고했고, PO 세션이 `356f41f`, `3c404e8` 로 가져왔다. 규칙은 `stage/operations/verification.md` 의 "Rules" 에 있고, `cloud-execution.md`, `review.md`, PO 스킬이 따라간다. 결정은 에픽 W-00000424 의 `## Progress` 에 있다.
- 2026-11-26 사용자가 이 카드를 지금 닫지 않고 자기 규칙에 따라 병합하고 열어 두라고 했다("추천대로 하죠"). PO 세션이 위의 성공 기준 한 줄을 더했다.
- 2026-11-26 PO 세션이 가져온 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다. This change was merged without a close review. 코드는 시험 규칙에 따라 카드를 열어 둔 채 병합하고, 이 카드에 대해 사용자에게 따로 묻지 않았다.
## Verification
