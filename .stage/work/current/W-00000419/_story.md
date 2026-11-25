---
id: W-00000419
title: 후속 작업 후보는 지금 깨져 있거나 열린 마일스톤의 완료 기준 한 줄을 지목할 때만 카드가 된다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000419
promotion: pending
review: pending
scope: stage/skills/stage-orchestrate/SKILL.md,stage/scripts/subsession_brief.py,stage/operations/before.md,stage/operations/after.md,stage/operations/cloud-execution.md,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs: DE-00000102
---

# W-00000419 후속 작업 후보는 지금 깨져 있거나 열린 마일스톤의 완료 기준 한 줄을 지목할 때만 카드가 된다

## Purpose

카드를 닫을 때마다 나오는 후속 작업 후보 가운데 문턱을 넘은 것만 카드가 되고 나머지는 기록 없이 버려져서, 일감이 끝없이 생기지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 작업 브리핑이 후속 후보마다 재현 명령이나 열린 마일스톤의 완료 기준 한 줄을 붙이라고 한다
- 지휘 스킬이 그 증거가 있는 후보만 등록하고 나머지는 기록하지 않는다
- 카드를 닫을 때 등록 몇, 버림 몇 한 줄이 적힌다
- before.md, after.md, 지휘 스킬이 같은 조건을 말한다

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6QrDdz3LAVPpMYGmyK — work — 2026-11-25 — opened from the index: DE-00000102, M-00000006

## Progress

- 2026-11-25 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 사용자가 토론 세션 session_018VXR6SH4PsfzwA6PTiZW3a 에서 문턱을 정했고 DE-00000102 에 적었다. 성공 기준 네 줄은 토론 세션의 초안이고 사용자가 그대로 받았다("추천대로 해주세요"). 고칠 자리는 DE-00000102 의 "Where this applies" 에 있다.
- 범위 밖: 규칙 후보의 문턱(아직 정해지지 않았다), 버린 후보의 목록(사용자가 고르지 않았다).
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-25 작업 세션 session_018VXR6QrDdz3LAVPpMYGmyK 가 4ad0af16 을 보고했다. 성공 기준 넷을 모두 채웠다고 했다. 조건의 주인은 `operations/before.md` 의 "Follow-up candidates" 다. 범위 밖으로 `stage/scripts/started_cards.py` 의 설명 한 줄을 고쳤다. 작업 세션은 사용자가 그 세션에서 두 확인(버린 수를 적는 줄, 인용한 줄을 찾아보지 않는 것)에 "추천대로"라고 답했다고 전했다.
- 2026-11-25 지휘 세션이 squash 커밋 3a9b852 에서 훅 시험(489 통과)과 스크립트 시험(1027 통과)을 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0

## Verification

2026-11-25 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `3a9b852` 의 것이다.
