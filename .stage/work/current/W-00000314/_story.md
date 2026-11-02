---
id: W-00000314
title: 번호 도구가 제목 줄에만 번호가 있는 기록도 센다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/stage_record_ids.py, stage/scripts/tests/test_stage_record_ids.py, .stage/state/observations/O-00000056.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000314 번호 도구가 제목 줄에만 번호가 있는 기록도 센다

## Purpose

번호 도구가 이미 쓴 번호를 빈 번호로 알려 기록이 서로 부딪히는 일이 없게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 제목 줄에만 번호가 있는 기록(작업 트리와 다른 브랜치 모두)의 번호를 도구가 세어, 그보다 큰 번호를 다음 번호로 알린다는 것을 테스트가 확인한다
- frontmatter id 로 세던 기존 접두사의 결과는 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
