---
id: W-00000302
title: 리뷰 판정 검증을 닫기 도구와 드라이버가 한 함수로 나눠 쓴다
kind: chore
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/driver_review.py, stage/scripts/tests/test_close_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000302 리뷰 판정 검증을 닫기 도구와 드라이버가 한 함수로 나눠 쓴다

## Purpose

리뷰 판정 JSON 의 기준별 검증 규칙이 두 곳에 따로 있어 한쪽만 고쳐지면 닫기와 드라이버가 같은 판정을 다르게 받아들이는 일을 막는다.

## Actions

- 지금 동작: `close_work.load_review_verdict()` 와 `driver_review.load_driver_review_verdict()` 가 기준 항목마다
  문자열·한 줄·중복·PASS/FAIL·approved 일치 검사를 각자 한다. 드라이버 쪽은 `reviewed_in_round` 를 하나 더 받으려고
  같은 검사를 다시 적었다.
- 기준 항목 검증을 `close_work.py` 의 함수 하나로 모으고 드라이버가 그것을 부른다. 오류 문구는 그대로 둔다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 닫기 도구와 드라이버가 판정 기준 항목 검증을 한 함수로 하고, 기존 오류 문구와 동작이 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
