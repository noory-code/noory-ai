---
id: W-00000216
title: 감사가 두-자리 허가증을 잡는 동작을 시험으로 못 박는다
kind: qa
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
---

# W-00000216 감사가 두-자리 허가증을 잡는 동작을 시험으로 못 박는다

## Purpose

다 쓴 허가증이 대기 서랍과 보관함에 함께 남는 상태를 감사가 잡는 것은 확인됐지만 그 동작을 붙드는 시험이 없어 일반 규칙에 예외가 하나 더 붙으면 소리 없이 사라질 수 있으므로, 그 상태를 만든 픽스처 시험으로 동작을 못 박는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 같은 DE 기록을 decisions/pending 과 official/decisions/archive 에 함께 둔 픽스처에서 감사 오류를 요구하는 시험이 있고 통과한다
- 그 시험이 생긴 근거로 O-00000032 를 닫는다

## Next action
