---
id: W-00000381
title: Windows 에서 검사와 리뷰의 시간 제한이 실제로 끊게 한다
kind: fix
venue:
milestone: M-00000005
status: captured
priority: 6
autonomous: false
acceptance: []
review: not_required
scope: stage/skills/stage-retrospective/close_work.py,stage/scripts,stage/CHANGELOG.md
---

# W-00000381 Windows 에서 검사와 리뷰의 시간 제한이 실제로 끊게 한다

## Purpose

Windows 에서 --timeout 과 --review-timeout 이 시간을 넘긴 검사와 리뷰를 그 시간에 끊는다

## Actions


## User value

W-00000380 서브세션이 찾았다. `close_work.py` 의 `run_check()` 가 `subprocess.run(command, shell=True,
capture_output=True, timeout=...)` 을 쓴다. Windows 에서는 시간이 넘으면 cmd.exe 만 죽고, 손자 프로세스(python)가
stdout/stderr 파이프를 쥐고 있어서 kill 뒤의 communicate() 가 손자가 끝날 때까지 기다린다.

근거(PR #92 의 임시 진단 실행, windows-latest/3.12): `test_review_timeout_argument_bounds_the_review_command`(sleep 5,
timeout 1, subTest 2개)가 ubuntu 2.23초, Windows 11.53초. `test_check_timeout_argument_bounds_checks_not_reviews` 가
1.11초 대 5.48초.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Windows 에서 5초 걸리는 명령을 1초 시간 제한으로 돌리면 2초 안에 끝나는 시험이 있고 통과한다
- 드라이버 쪽에도 같은 모양(shell=True 와 timeout)이 있는지 확인한 결과가 카드에 적혀 있다

## Next action
