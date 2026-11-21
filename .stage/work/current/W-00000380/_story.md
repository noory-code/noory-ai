---
id: W-00000380
title: Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000380 Stage 스크립트 테스트 픽스처 비용 줄여 Windows CI 단축

## Purpose

Windows CI 의 Scripts suite 단계(샤드당 128-181초, ubuntu 의 약 5배)를 테스트 격리와 단언을 그대로 둔 채 픽스처 비용을 줄여 단축한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- PR 의 stage 워크플로에서 windows-latest Scripts suite 단계의 가장 느린 샤드가 main 기준(e0d95a1, 최대 181초)보다 30% 이상 빠르다(127초 미만).
- scripts 테스트 수가 변경 전후 같고(806), 삭제·skip·단언 약화가 없다.

## Next action


## Related truth


## Progress


## Verification
