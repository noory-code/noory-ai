---
id: W-00000340
title: 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다
kind: fix
venue: claude
environment: local-no-codex
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
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000340 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다

## Purpose

승격을 나중에 쓰는 카드가 닫기 도구의 안내만 따라도 승격 게이트에 막히지 않게 실제로 통하는 순서를 알려 준다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 닫기 도구가 deferred 로 닫은 뒤 approved 로 바꾸고 intent 를 만들어 쓰고 promoted 로 기록하는 순서를 안내한다
- 닫기 도구와 게이트와 감사의 동작은 바뀌지 않는다
- 안내 문구를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
