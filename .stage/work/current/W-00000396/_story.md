---
id: W-00000396
title: 릴리스된 절 점검이 기준 버전 이후만 보게 한다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000396 릴리스된 절 점검이 기준 버전 이후만 보게 한다

## Purpose

릴리스된 절 점검을 기준 버전 이후에만 걸어 과거 기록 때문에 실패하지 않고 CI 에 넣을 수 있다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- release_plugin.py --check-released --since <버전> 이 그 버전보다 오래된 절을 건너뛰는 시험이 있고 통과한다
- 이 저장소에서 --since 를 지금 최신 버전으로 주면 stage 가 통과한다

## Next action

## Related truth

## Progress

## Verification
