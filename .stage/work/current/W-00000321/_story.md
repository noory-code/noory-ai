---
id: W-00000321
title: Windows 셸 파서가 드라이브에 붙인 /dev/null 도 장치로 알아본다
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
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000321 Windows 셸 파서가 드라이브에 붙인 /dev/null 도 장치로 알아본다

## Purpose

Windows 에서 출력을 /dev/null 로 버리는 셸 명령이 범위 넘음으로 알려지지 않게 해, W-00000319 이 겨눈 결과를 실제로 낸다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 셸 파서가 드라이브에 붙여 낸 장치 경로('C:\dev\null', 'C:/dev/stderr')가 범위 넘음으로 알려지지 않고, 'C:\dev\proj\app.py' 같은 일반 경로는 장치로 보지 않는다는 것을 시험이 확인한다
- PR 의 Windows CI(Python 3.9·3.12)에서 Stage hooks 시험이 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
