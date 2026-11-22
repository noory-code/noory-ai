---
id: W-00000391
title: 드라이버의 닫기와 보류 호출, 리뷰어 실행에도 프로세스 트리 시간 제한을 건다
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_lifecycle.py,stage/scripts/run_review.py,stage/scripts/tests/test_drive.py,stage/scripts/tests/test_run_review.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000391 드라이버의 닫기와 보류 호출, 리뷰어 실행에도 프로세스 트리 시간 제한을 건다

## Purpose

드라이버가 close_work 와 escalate_work 를 부를 때와 리뷰어를 띄울 때 시간이 넘으면 Windows 에서도 프로세스 트리 전체가 끝난다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- driver_lifecycle 의 close_via_close_work 와 escalate_via_escalate_work 가 hooks/stage_process.run_bounded 를 쓰고, 손자 프로세스가 남지 않는 시험이 있고 통과한다
- run_review.py 가 리뷰어에 시간 제한을 걸고, 시간이 넘으면 리뷰가 실패로 끝나는 시험이 있고 통과한다

## Next action

## Related truth

## Progress

## Verification
