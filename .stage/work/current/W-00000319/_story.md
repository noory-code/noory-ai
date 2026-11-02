---
id: W-00000319
title: CI 에서 드러난 Stage 의 Windows·작업 폴더 버그를 고친다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000319 CI 에서 드러난 Stage 의 Windows·작업 폴더 버그를 고친다

## Purpose

Stage 시험과 범위 넘음 알림이 Windows 와 다른 작업 폴더에서도 로컬과 같게 동작해 CI 가 다시 초록이 되게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Windows 에서 '/dev/null' 처럼 드라이브 없이 쓴 POSIX 장치 경로가 범위 넘음으로 알려지지 않는다는 것을 시험이 확인한다
- stage 폴더에서 돌려도(CI 와 같게) scripts·hooks 시험 전체가 통과하고, 현재 폴더를 옮기는 시험이 임시 폴더를 지우기 전에 원래 폴더로 돌아온다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
