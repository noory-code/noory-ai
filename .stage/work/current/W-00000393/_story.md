---
id: W-00000393
title: release_plugin.py 가 Windows 에서도 UTF-8 로 출력하게 한다
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
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

# W-00000393 release_plugin.py 가 Windows 에서도 UTF-8 로 출력하게 한다

## Purpose

Windows 에서 --check-released 가 버전 제목의 줄표를 깨뜨리지 않고 출력한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 표준 출력이 cp1252 일 때 --check-released 가 버전 제목을 그대로 출력하는 시험이 있고, 고치기 전에는 실패하고 지금은 통과한다
- PR 의 windows-latest 잡이 통과한다

## Next action


## Related truth


## Progress


## Verification
