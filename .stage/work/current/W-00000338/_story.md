---
id: W-00000338
title: 등록 게이트도 같은 명령에서 정한 변수 경로를 풀어서 판정한다
kind: fix
venue: claude
environment: local-no-codex
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
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000338 등록 게이트도 같은 명령에서 정한 변수 경로를 풀어서 판정한다

## Purpose

열린 카드가 없을 때 같은 명령에서 프로젝트 밖으로 정한 변수 경로에 쓰는 명령을 등록 게이트가 프로젝트 파일 쓰기로 보고 막지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 열린 카드가 없을 때 S=프로젝트 밖 경로 다음에 "$S/파일" 에 쓰는 명령을 등록 게이트가 막지 않는다
- 변수 값이 프로젝트 안을 가리키거나 풀 수 없는 변수면 지금처럼 막는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
