---
id: W-00000317
title: 실패한 리뷰가 남긴 파일이 다음 판에 섞이지 않게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_supervised.py, stage/scripts/driver_runstate.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000317 실패한 리뷰가 남긴 파일이 다음 판에 섞이지 않게 한다

## Purpose

리뷰가 판정 파일 밖에 쓴 변경이, 사람이 치우지 않은 채 다음 판의 항목 커밋에 리뷰 없이 섞여 들어가지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰가 파일을 써서 실패한 뒤, 그 파일이 리뷰 전 상태로 돌아오지 않았으면 다음 판이 실행자를 돌리지 않고 멈추며 그 경로를 알리고, 되돌렸으면 평소대로 돈다는 것을 테스트가 확인한다
- 사람이 --reset-attempts 로 그 변경을 받아들이면 다음 판이 막히지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
