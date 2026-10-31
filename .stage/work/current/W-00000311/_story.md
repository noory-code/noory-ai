---
id: W-00000311
title: 범위 넘음 알림에서 고치지 않은 경로를 뺀다
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
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, .stage/state/observations/O-00000050.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000311 범위 넘음 알림에서 고치지 않은 경로를 뺀다

## Purpose

범위 넘음 알림 한 줄이 실제로 범위 밖 프로젝트 파일을 고친 경우에만 떠서 사람과 에이전트가 진짜 넘음을 가려낼 수 있게 한다

## Actions

- 지금 동작(O-00000050, 2026-11-01 재현): `purpose_tool_context` 가 Edit·Write 에 `transcript_path` 를,
  `cp … "$TMPDIR/x"` 에 `$TMPDIR/x` 를, `> /dev/null` 에 `/dev/null` 을, `> /tmp/foo.txt` 에 `/tmp/foo.txt` 를 넘은 경로로 낸다.
- 원인 셋: `collect_explicit_paths` 가 `tool_input` 이 아니라 페이로드 전체를 훑어 최상위 `transcript_path` 를 줍는다.
  셸 변수를 펼치지 않은 대상이 작업 폴더 밑 상대 경로가 된다. 장치 파일과 OS 임시 폴더도 범위 밖으로 센다.
- `collect_explicit_paths` 는 `tool_input` 만 본다. 범위 넘음 보고에서만 장치 파일(`/dev/…`, Windows `NUL`)과 OS 임시
  폴더(`tempfile.gettempdir()`, `$TMPDIR`)를 빼고, 앞에 붙은 셸 변수는 훅 환경에 값이 있을 때 펼쳐서 판단한다. `.stage`
  쓰기 게이트는 바꾸지 않는다. O-00000050 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Edit·Write 호출의 세션 transcript 경로, 출력을 버리는 /dev/null, OS 임시 폴더 안 경로, 환경에서 펼칠 수 있는 셸 변수로 시작하는 임시 경로가 범위 넘음으로 알려지지 않는다는 것을 테스트가 확인한다
- 범위 밖 프로젝트 파일과 작업 폴더 밖의 다른 경로는 여전히 범위 넘음으로 알려지고, .stage 쓰기를 막는 게이트는 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
