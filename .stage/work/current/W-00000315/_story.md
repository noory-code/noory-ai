---
id: W-00000315
title: 시도 횟수를 되돌릴 때 멈춘 판의 작업을 정리한다
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
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, .stage/state/observations/O-00000051.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000315 시도 횟수를 되돌릴 때 멈춘 판의 작업을 정리한다

## Purpose

드라이버를 멈춘 뒤 되돌리고 다시 돌린 판이, 멈춘 판에서 살아남은 실행자나 리뷰어 작업 때문에 카드와 무관하게 깨지지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 중단된 역할이 기록된 상태에서 시도 횟수를 되돌리면, 그 역할의 venue 정리 명령(reaper)이 카드 경로와 역할을 받아 먼저 돈다는 것을 테스트가 확인한다
- 중단된 역할이 없으면 되돌릴 때 정리 명령을 부르지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
