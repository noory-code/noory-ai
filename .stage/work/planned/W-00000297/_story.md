---
id: W-00000297
title: 드라이버가 닫을 때도 긴 리뷰 제한 시간을 쓰게 한다
kind: fix
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/driver_lifecycle.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
---

# W-00000297 드라이버가 닫을 때도 긴 리뷰 제한 시간을 쓰게 한다

## Purpose

드라이버가 close_work 를 timeout+60초에 끊어 더 긴 --review-timeout 을 쓰지 못하는 일을 막고 바깥 제한 시간이 검사와 리뷰를 함께 덮게 한다.

## Actions

- 지금 동작: `stage/scripts/driver_lifecycle.py` 의 `close_via_close_work()` 는 `close_work.py` 를
  `timeout + 60` 초에 끊고, 그 안의 리뷰에 `--review-timeout` 을 `--timeout` 과 같은 값으로 넘긴다.
  그래서 드라이버로 닫을 때는 `close_work.py` 의 리뷰 기본값 3600초를 쓰지 못한다.
- 출처: W-00000270 실행 보고(Work not done)와 R-00000270 "Next changes".

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 드라이버가 close_work 를 부를 때 바깥 제한 시간이 검사 시간과 리뷰 제한 시간을 함께 덮는다는 것을 테스트가 확인한다

## Next action
