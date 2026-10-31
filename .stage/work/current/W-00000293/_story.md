---
id: W-00000293
title: 계획 카드 등록도 겹친 번호의 브랜치 이름을 보여 준다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-work/register_work.py, stage/scripts/tests/test_register_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000293 계획 카드 등록도 겹친 번호의 브랜치 이름을 보여 준다

## Purpose

계획 카드를 등록할 때도 다른 브랜치가 이미 쓴 번호면 어느 브랜치인지 알려 주어 사람이 바로 고를 수 있게 한다.

## Actions

- 지금 동작: `register_work.py` 는 현재 카드 등록에서는 다른 브랜치가 쓴 번호를 브랜치 이름과 함께
  거절하지만, `--backlog` 등록에서는 "id is already used" 만 보여 준다(W-00000291 닫기 리뷰, R-00000291).
- `--backlog` 경로도 다른 브랜치의 번호면 그 브랜치 이름을 함께 보여 준다. 지금 체크아웃에서 쓰인 번호는
  지금처럼 거절한다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 다른 브랜치가 이미 쓴 번호로 계획 카드를 등록하면 그 브랜치 이름과 함께 거절된다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
