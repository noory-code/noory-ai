---
id: W-00000316
title: 마일스톤 완료 기준 앞의 목록 기호가 겹치지 않게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_v4.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-roadmap/manage_roadmap.py, stage/scripts/tests/test_roadmap_v4.py, .stage/state/observations/O-00000045.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000316 마일스톤 완료 기준 앞의 목록 기호가 겹치지 않게 한다

## Purpose

완료 기준을 목록 기호를 붙여 넘겨도 마일스톤 기록에 기호가 겹쳐 남지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 완료 기준 값이 '- ', '* ', '+ ' 로 시작해도 기록에는 '- 기준' 한 겹만 남고, 기호 없는 값과 하이픈이 내용의 일부인 값('-5% 지연')은 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
