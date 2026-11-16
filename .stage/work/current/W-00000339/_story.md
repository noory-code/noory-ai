---
id: W-00000339
title: 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000339 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다

## Purpose

열린 관찰·질문·제안 기록에 목록 줄이 없거나 목록 줄이 없는 기록을 가리킬 때 감사가 알려, 닫기 도구가 막히기 전에 어긋남을 찾게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 열린 기록에 목록 줄이 없으면 감사가 기록 이름과 함께 경고한다
- 목록 줄이 가리키는 열린 기록이 없으면 감사가 경고한다
- 목록과 기록이 맞으면 아무것도 알리지 않는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
