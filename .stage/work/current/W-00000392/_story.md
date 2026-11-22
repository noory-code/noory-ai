---
id: W-00000392
title: 릴리스된 변경 기록 절에 나중에 끼어든 줄을 찾는다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_changelog_union.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,stage/scripts/tests/test_changelog_union.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000392 릴리스된 변경 기록 절에 나중에 끼어든 줄을 찾는다

## Purpose

합친 뒤 이미 릴리스된 버전 절에 들어간 줄을 사람이 손으로 비교하지 않아도 명령 하나가 알려 준다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- release_plugin.py 의 점검이 각 릴리스 절을 그 릴리스 커밋이 쓴 내용과 비교해 더해진 줄을 출력하고 실패로 끝나는 시험이 있고 통과한다
- 끼어든 줄이 없으면 점검이 통과한다

## Next action

## Related truth

## Progress

## Verification
