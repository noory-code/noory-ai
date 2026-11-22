---
id: W-00000382
title: 드라이버가 저장소 상태를 볼 때 띄우는 git 프로세스를 줄인다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 7
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/driver_repository.py,stage/scripts/driver_git.py,stage/scripts/tests,stage/CHANGELOG.md
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
