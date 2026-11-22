---
id: W-00000382
title: 드라이버가 저장소 상태를 볼 때 띄우는 git 프로세스를 줄인다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000382
promotion: pending
review: pending
scope: stage/scripts/driver_repository.py,stage/scripts/driver_git.py,stage/scripts/driver_runstate.py,stage/scripts/land_run.py,stage/scripts/tests/test_driver_git.py,stage/scripts/tests/test_driver_repository.py,stage/scripts/tests/test_land_run.py,stage/scripts/tests/test_drive.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000382 드라이버가 저장소 상태를 볼 때 띄우는 git 프로세스를 줄인다

## Purpose

드라이버가 저장소 상태를 볼 때마다 git 을 3~4번 띄우는 것을 줄여 Windows 에서 실행과 시험이 빨라진다

## Actions


## User value

W-00000380 서브세션이 strace 로 셌다. scripts 시험 전체에서 `rev-parse --git-path index` 1,021회,
`ls-files --others` 920회, `ls-files --cached --stage` 427회, `diff --no-ext-diff --binary HEAD` 416회가 뜬다. 남은 git
프로세스 약 6,000개의 절반 가까이다. 자리는 `stage/scripts/driver_repository.py` 의 `repository_path_snapshot()`,
`git_index_path()`, `git_index_entries()`, `git_untracked_paths()`, `git_diff()` 와 `stage/scripts/driver_git.py:107`
(경로마다 `ls-files` 를 따로 부른다)이다.

Windows 러너에서 git 프로세스 하나는 35~46ms, ubuntu 는 약 1ms 다. 같은 루트의 `--git-path index` 결과를 다시 쓰고
`ls-files` 호출을 합치면 동작을 그대로 두고 프로세스를 줄일 수 있다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- scripts 시험 전체에서 띄우는 git 프로세스 수가 바꾸기 전보다 줄었고 그 수가 카드에 적혀 있다
- 드라이버의 동작 시험이 바꾸기 전과 같은 수로 모두 통과한다

## Next action

## Related truth

## Progress

- scripts 시험 전체가 띄우는 git 프로세스(Linux, `strace -f -e trace=execve`): 바꾸기 전 6,879개(시험 840개),
  바꾼 뒤 5,330개(시험 851개, 새 시험 11개 포함). 기존 시험 840개는 바꾼 뒤에도 모두 통과한다.
  - `rev-parse --git-path index` 1,044 → 145, `ls-files --others` 906 → 248,
    `ls-files --cached --stage` 422 → 0 (`ls-files -t --cached --stage --others` 467 로 합침).

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6PenXB1UzzSA9HXNWt)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w382-fewer-git-calls` 의 7e86550b 를 squash 했다(af0af805).
- 성공 기준 1: scripts 시험 전체가 띄우는 git 프로세스가 6,879개에서 5,330개로 줄었다(리눅스, `strace -f -e trace=execve`).
  자세한 수는 이 카드의 `## Progress` 에 있다.
- 성공 기준 2: 바꾸기 전의 시험 840개가 모두 그대로 통과한다. 메인 세션이 main(W-00000381, W-00000384 포함) 위에 squash 한
  뒤 다시 돌린 scripts 전체, hooks 전체가 통과했고 감사 오류는 0건이다.
- 반쯤 폐기된 `git ls-files -t` 를 쓰는 것은 사용자 확인을 기다린다. 메인 세션은 받아들이자고 권했다.

- Review at close 2026-11-22 by claude_review_companion: rejected (1 PASS, 2 PASS, 3 FAIL)
