---
id: W-00000294
title: 닫기 도구가 감사와 같은 승격 기록 검사를 쓴다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/audit_stage.py, stage/scripts/tests/test_close_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000294 닫기 도구가 감사와 같은 승격 기록 검사를 쓴다

## Purpose

닫기 도구가 감사가 거부할 승격 선택으로 카드를 닫아 닫은 직후 감사가 깨지는 일을 막는다.

## Actions

- 지금 동작: `close_work.py` 는 승격 선택이 최종값인지만 본다. 감사는 닫힌 카드의 `approved` 를 늘 거부하고,
  `promoted` 는 `promotes:` 경로가 있고 그 파일이 있어야 받아들인다(WORK027). 그래서 W-00000292 는 `approved`
  로 닫힌 직후 감사 오류 2개를 냈다.
- 감사의 WORK027 검사를 함수 하나로 꺼내 감사와 닫기 도구가 함께 쓴다. 닫기 도구는 검사를 돌리기 전에 그
  함수로 거절하고 카드를 바꾸지 않는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 감사가 WORK027 로 거부할 승격 선택으로 닫으려 하면 닫기 도구가 카드를 바꾸지 않고 같은 이유로 거절한다는 것을 테스트가 확인한다
- 닫기 도구와 감사가 승격 기록 검사를 한 곳에서 공유한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
