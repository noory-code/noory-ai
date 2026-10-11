---
id: W-00000270
title: 닫기 전 리뷰에 일반 검사와 따로 제한 시간을 준다
kind: fix
venue: codex
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
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/operations/review.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000270 닫기 전 리뷰에 일반 검사와 따로 제한 시간을 준다

## Purpose

생각 깊이가 높은 리뷰가 일반 검사용 제한 시간에 걸려 닫기가 막히지 않게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- close_work 가 리뷰 명령에 일반 검사와 다른 제한 시간을 쓰고, 그 값을 인자로 바꿀 수 있다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
