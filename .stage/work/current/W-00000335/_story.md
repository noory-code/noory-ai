---
id: W-00000335
title: cd 로 들어간 폴더 아래에서도 같은 명령에서 정한 변수 경로를 풀어 범위 알림에서 뺀다
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
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md, .stage/state/observations/O-00000057.md, .stage/state/current.md
promotes:
decision_refs:
---

# W-00000335 cd 로 들어간 폴더 아래에서도 같은 명령에서 정한 변수 경로를 풀어 범위 알림에서 뺀다

## Purpose

cd 로 다른 폴더에 들어간 뒤 같은 명령에서 정한 변수 경로에 쓸 때 훅이 그 경로를 프로젝트 파일로 잘못 알리지 않게 한다

## Actions

없음 — 변수를 푸는 함수 한 곳을 고치고 테스트를 더하는 일이라 나누지 않는다.

## User value

`cd 다른폴더 && S=/tmp/... && cat > "$S/a.md"` 처럼 쓰는 명령에 범위를 넘었다는 알림과 전체
작업 맥락이 더 붙지 않는다. 보고서나 PR 본문을 임시 폴더에 쓰는 명령에서 자주 나오는 모양이다.

## Scope

### Included

- 훅이 쓰기 대상 경로를 `cd` 한 폴더 아래로 붙여 읽은 경우에도, 그 경로가 같은 명령에서 정한
  변수로 시작했으면 그 변수를 풀어서 판정한다.
- 변수 값이 절대 경로면 `cd` 한 폴더를 떼고 그 값으로 읽는다. 상대 경로면 지금처럼 `cd` 한
  폴더 아래로 읽는다.
- 쓰기 대상이 실제로 변수로 시작했는지는 명령에 적힌 인자로 확인한다. 경로 가운데에 변수가
  있는 인자(`dir/$S/x`)는 지금처럼 둔다.
- O-00000057 을 원인과 함께 닫는다.

### Excluded

- 등록 게이트, 커밋 게이트, `.stage` 게이트는 바꾸지 않는다. 범위 알림만 바뀐다.
- `.stage/.runtime/` 아래 쓰기를 범위 알림에서 빼는 일은 하지 않는다. 같은 날 따로 본 경우라
  관찰로 남길지 따로 정한다.

## Risks

- 인자가 변수로 시작했는지 확인하는 방법이 명령 글자를 다시 읽는 것이라, 따옴표나 리다이렉트를
  특이하게 쓴 명령에서는 놓칠 수 있다. 놓치면 지금처럼 알린다(알림이 남는 쪽으로 틀린다).
- `stage/hooks/` 를 고치는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).

## Success criteria

- cd 로 프로젝트 안 폴더에 들어간 뒤 같은 명령에서 프로젝트 밖 절대 경로로 정한 변수에 쓰면 범위를 넘었다고 알리지 않는다
- 변수 값이 상대 경로이면 지금처럼 cd 한 폴더 아래 경로로 읽는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
- O-00000057 에 원인과 고친 곳을 적고 닫는다

## Next action

`test_stage_guard.py` 에 깨지는 테스트를 먼저 쓰고 `expand_leading_shell_variable` 을 고친다.

## Related truth

- O-00000057 — 이 카드가 닫을 관찰.
- W-00000332 — 같은 명령에서 정한 변수 경로를 범위 알림에서 뺀 카드(보관됨). 그때는 경로가
  변수로 시작하는 경우만 다뤘다.
- DE-00000086 — codex 가 없는 로컬 세션에서 Claude 가 실행하고 닫기 리뷰를 따로 받는다.
- DE-00000087 — `stage/hooks/` 를 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress


## Verification


## Retrospective


## Promotion decision
