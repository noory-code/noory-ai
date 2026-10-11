---
id: W-00000269
title: 닫기 전 리뷰의 기준별 판정을 카드에 적는다
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

# W-00000269 닫기 전 리뷰의 기준별 판정을 카드에 적는다

## Purpose

코드 카드가 리뷰를 통과했다는 표시만이 아니라 무엇을 보고 통과시켰는지가 카드에 오래 남게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰가 통과하면 카드의 Verification 에 기준마다 판정과 까닭이 적힌다는 것을 테스트가 확인한다
- operations/review.md 가 닫기 도구가 카드에 무엇을 적는지 코드와 같게 적는다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
