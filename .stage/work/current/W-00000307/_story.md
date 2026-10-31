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
scope: stage/scripts/driver_runstate.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, .stage/state/observations/O-00000047.md, .stage/state/current.md, stage/CHANGELOG.md
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
- 되돌릴 때 지난 판정 파일과 W-00000305 의 기준 지문 파일을 지워 다음 판이 전체 리뷰로 돌게 한다. 상태나 로그
  기록이 실패하면 지운 파일을 되살린다.
- `executor_changed_paths` 는 다 지우지 않는다. 드라이버는 이전 판의 결과를 작업 트리에 남기고(`restore_item_output` 은
  mixed reset), 항목 커밋이 `base_head` 이후 전부를 하나로 합친다. 그래서 다 지우면 사람이 남겨 둔 결과가 커밋에는
  들어가는데 리뷰에서는 빠진다. `base_head` 와 아직 다른 경로만 남기고 사람이 되돌린 경로는 뺀다(드라이버 스냅숏과
  같이 추적 파일과 무시되지 않은 미추적 파일 기준).
- 작업 로그의 되돌림 기록에 지운 판정 파일과 뺀·남긴 경로를 적는다. `stage/docs/SCHEMA_V4.md` 의 되돌림 설명을 맞춘다.
- O-00000047 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 시도 횟수를 되돌리면 지난 판정 파일과 그 기준 지문이 지워지고, 쌓인 실행자 변경 경로에서 사람이 되돌린 경로는 빠지되 기준 커밋과 아직 다른 경로는 남으며, 작업 로그에 그 사실이 남는다는 것을 테스트가 확인한다
- 되돌림 상태를 기록하지 못하면 지운 판정 파일과 기준 지문이 되살아나고 실행 상태가 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
