---
id: W-00000305
title: 판 사이에 완료 기준이 바뀌면 전체 리뷰로 다시 판정한다
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
scope: stage/scripts/driver_review.py, stage/scripts/driver_supervised.py, stage/scripts/tests/test_drive.py, .stage/state/observations/O-00000052.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000305 판 사이에 완료 기준이 바뀌면 전체 리뷰로 다시 판정한다

## Purpose

사람이 리뷰 사이에 카드의 완료 기준을 바꿔도 드라이버가 승인된 판정을 버리거나 새 기준을 판정 없이 지나가게 하지 않게 한다.

## Actions

- 지금 동작(O-00000052): 감독 드라이버는 이전 판정 파일이 있으면 늘 좁은 재리뷰를 돌리고, 합칠 때 이전 판정에 없던
  기준이 돌아오면 "narrow review returned criteria absent from the previous verdict" 로 판정을 버린다. 사람이 판 사이에
  완료 기준을 더하면 리뷰어가 모두 PASS 로 승인해도 시도를 태운다. 반대로 리뷰어가 새 기준을 판정하지 않으면 그
  기준이 합친 판정에서 빠진 채 지나갈 수 있다.
- 판정이 확정될 때(전체 리뷰든 합친 재리뷰든) 카드 `## Success criteria` 의 지문을 판정 파일 옆에 기록한다. 다음 판에서
  지문이 다르면 좁은 재리뷰 대신 전체 리뷰를 돌린다. 지문 기록이 없는 예전 판정은 지금처럼 다룬다.
- 실행자가 이전 실패 기준에 처분을 적는 의무는 그대로 둔다. 바뀌는 것은 리뷰 방식뿐이다.
- O-00000052 를 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 이전 판정 뒤에 카드의 완료 기준이 바뀌면 다음 판 리뷰가 좁은 재리뷰가 아니라 전체 리뷰로 돌고 그 승인이 받아들여진다는 것을 테스트가 확인한다
- 완료 기준이 그대로면 지금처럼 실패한 기준만 다시 보는 좁은 재리뷰가 돈다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
