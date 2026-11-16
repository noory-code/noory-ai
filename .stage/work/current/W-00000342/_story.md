---
id: W-00000342
title: 게이트가 셸 명령의 상대 경로를 셸이 실제로 있는 폴더에서 읽는다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000342
promotion: pending
review: pending
scope: stage/hooks/stage_guard.py, stage/hooks/stage_shell.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, stage/hooks/README.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000342 게이트가 셸 명령의 상대 경로를 셸이 실제로 있는 폴더에서 읽는다

## Purpose

셸이 저장소 밖 폴더에 있을 때 그 폴더의 파일을 고치는 명령을 열린 카드가 없다는 이유로 막지 않는다

## Actions

없음 — 게이트가 셸 명령을 읽기 시작하는 폴더 하나를 바꾼다.

## User value

셸이 저장소 밖 폴더(예: Claude 메모 폴더)에 있을 때 그 폴더의 파일을 `sed -i` 나 리다이렉트로
고치면, 열린 카드가 없을 때 게이트가 그 파일을 저장소 폴더의 같은 이름 파일로 읽고 거절한다.
2026-11-16 에 메모를 고치다 이 거절을 받았고 Edit 도구로 돌아갔다. 고치면 셸 명령으로도 그
폴더의 파일을 고칠 수 있고, 범위 알림도 실제로 쓰는 경로를 가리킨다.

## Scope

### Included

- 쓰기 대상과 지우기 대상을 계산할 때 훅에 오는 `cwd` 에서 읽기 시작한다. 등록 게이트와 범위
  알림이 둘 다 이 계산을 쓴다.
- `cwd` 가 없거나 존재하지 않는 폴더면 지금처럼 저장소 폴더에서 시작한다.
- 훅 문서(`stage/operations/hooks.md`, `stage/hooks/README.md`)와 변경 기록에 적는다.

### Excluded

- 커밋 대상 계산과 `.stage` 삭제 검사. git 은 따로 `git_runs_outside_workspace` 가 다루고,
  `.stage` 삭제 검사는 지금처럼 저장소 폴더 기준으로 막는 쪽에 둔다.
- 그때 명령에 있던 `cd` 가 훅에 왜 안 보였는지 밝히는 일. 훅이 받은 명령은 기록에 남지 않아서
  확인할 수 없다.

## Risks

- 이 고침은 허락하는 쪽으로 움직인다. 훅에 오는 `cwd` 가 실제 셸 폴더와 다르면 저장소 쓰기를
  놓칠 수 있다. Claude Code 는 셸의 현재 폴더를, Codex 는 저장소 폴더를 보낸다.
- 셸이 저장소 안 하위 폴더에 있을 때 대상 경로가 그 하위 폴더 기준으로 바뀐다. 실제 쓰는
  경로와 맞아지는 것이지만 범위 알림 내용이 달라진다.


## Success criteria

- 셸이 메모 폴더에 있을 때 sed -i 로 MEMORY.md 를 고치는 명령이 등록 게이트를 통과한다
- 셸이 저장소 안에 있을 때 저장소 파일을 고치는 명령은 열린 카드가 없으면 지금처럼 막힌다
- 훅에 오는 cwd 가 없거나 존재하지 않는 폴더면 저장소 폴더에서 읽기 시작해 지금처럼 막힌다
- 새 테스트가 고치기 전 코드에서 실패하고 고친 뒤 통과한다

## Next action

고치기 전 코드에서 실패하는 테스트를 `test_stage_guard.py` 에 먼저 쓴다.

## Related truth

- W-00000338 — 같은 명령에서 정한 변수를 등록 게이트가 풀게 했다(보관됨).
- W-00000335 — `cd` 뒤 변수 경로를 범위 알림이 풀게 했다(보관됨).
- DE-00000087 — 게이트를 바꾸는 카드는 닫기 전에 사용자 확인을 받는다.


## Progress

`stage_guard.py` 에 `shell_start_folder` 를 두었다. 훅에 오는 `cwd` 가 있는 폴더면 그 폴더를,
아니면 저장소 폴더를 돌려준다. `mutation_targets` 가 쓰기 대상과 지우기 대상을 이 폴더에서 읽기
시작한다. 등록 게이트와 범위 알림이 둘 다 이 계산을 쓴다. 문서 두 곳과 변경 기록에 적었다.
커밋 `fc5ca35f`.

원인을 찾을 때, 명령에 `cd /메모폴더 &&` 가 있으면 파서가 그 폴더를 따라가 통과한다는 것을
확인했다. 셸이 이미 메모 폴더에 있고 명령에 `cd` 가 없을 때만 그때와 같은 거절이 나왔다. 그때
명령에는 `cd` 가 있었으므로 훅이 받은 명령이 달랐을 수 있지만, 확인하지 못했다.

## Verification

- 셸이 메모 폴더에 있을 때 `sed -i` 로 `MEMORY.md` 를 고치는 명령이 등록 게이트를 통과한다 —
  통과. 새 테스트 `test_registration_gate_reads_shell_paths_from_the_shell_folder` 가 저장소 밖
  폴더에서 `sed -i`, 리다이렉트, `rm` 세 가지를 허락하는지 본다.
- 셸이 저장소 안에 있을 때 저장소 파일을 고치는 명령은 지금처럼 막힌다 — 통과. 같은 테스트가
  저장소 폴더와 하위 폴더에서 거절되는지 보고, 하위 폴더에서는 거절 메시지가 `src/app.py` 를
  가리키는지 본다.
- `cwd` 가 없거나 존재하지 않는 폴더면 저장소 폴더에서 시작해 막힌다 — 통과. 같은 테스트의 두
  경우.
- 새 테스트가 고치기 전 코드에서 실패하고 고친 뒤 통과한다 — 통과. 고치기 전에는 허락해야 할 세
  경우와 하위 폴더 경로 확인, 네 군데가 실패했다.
- 전체 테스트: 훅 447개 통과, 스크립트 758개 통과(건너뜀 2개). 감사 오류 0개.
- 확인하지 않은 것: 실제 Claude Code 세션에서 셸이 저장소 밖에 있을 때의 동작. 지금은 이 카드가
  열려 있어서 등록 게이트가 걸리지 않는다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).
- 사용자 확인 — 2026-11-16: 게이트를 바꾼 카드라 닫기 전에 사용자에게 보였다(DE-00000087).
  보인 것은 바뀐 파일과 요약, 새 테스트가 고치기 전에 네 군데 실패한 것, 전체 테스트와 감사
  결과, 확인하지 못한 두 가지(그때 거절된 이유, 실제 세션 동작)다. 닫기 리뷰는 이 확인 뒤에
  돌렸으므로 리뷰 판정은 사용자에게 보이기 전이다. 사용자가 "확인, 닫기"로 답했다.


## Retrospective

[R-00000342](../../retrospectives/R-00000342.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
