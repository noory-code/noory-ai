---
id: W-00000307
title: 시도 횟수를 되돌릴 때 지난 판정과 쌓인 변경 경로도 지운다
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
scope: stage/scripts/driver_runstate.py, stage/scripts/tests/test_drive.py, .stage/state/observations/O-00000047.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000307 시도 횟수를 되돌릴 때 지난 판정과 쌓인 변경 경로도 지운다

## Purpose

카드를 다시 설계하고 시도 횟수를 되돌린 뒤의 다음 판이 버린 설계의 판정과 변경 경로 때문에 카드와 무관한 이유로 실패하지 않게 한다.

## Actions

- 지금 동작(O-00000047): `driver_runstate.reset_attempts()` 는 시도 횟수와 몇몇 재개 칸을 지우지만, 쌓인
  `executor_changed_paths` 를 남기고 판정 파일(`.stage/.runtime/driver/verdicts/<카드>.json`)은 손대지 않는다. 다시 설계한
  카드의 다음 판이 지난 판정으로 좁은 재리뷰를 돌거나, 버린 설계의 변경 경로와 실행 보고가 어긋나 시도를 태운다.
- 되돌릴 때 `executor_changed_paths` 도 지우고, 상태와 로그 기록이 끝난 뒤 지난 판정 파일과 W-00000305 의 기준 지문
  파일을 지운다. 작업 로그의 되돌림 기록에 지운 것을 적는다.
- O-00000047 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 시도 횟수를 되돌리면 지난 판정 파일과 그 기준 지문, 쌓인 실행자 변경 경로가 지워지고 작업 로그에 그 사실이 남는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
