---
id: W-00000381
title: Windows 에서 검사와 리뷰의 시간 제한이 실제로 끊게 한다
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000381
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py,stage/scripts/drive_parallel.py,stage/scripts/tests/test_close_work.py,stage/scripts/tests/test_drive_parallel.py,stage/hooks,stage/CHANGELOG.md
promotes:
decision_refs:
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

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: Added hooks/stage_process.py with run_bounded(), which keeps the subprocess.run contract (CompletedProcess with UTF-8 text, raises TimeoutExpired) but starts the command in its own process group (CREATE_NEW_PROCESS_GROUP on Windows, start_new_session on POSIX) and on timeout or any interrupt ends the group (taskkill /T /F while the parent is alive on Windows, killpg SIGKILL on POSIX), then drains the pipes for at most 2 seconds; close_work.run_check, drive_parallel.run_driver, and drive_parallel.reap_after_timeout use it; new tests run a 1.5-second child that writes a marker file under a 1-second limit, directly and through a grandchild, and assert the call returns in under 2 seconds and the marker is never written; the existing drive_parallel timeout tests now patch run_bounded instead of subprocess.run.
Why: On Windows the time limits did not cut a check or review at the limit because cmd.exe's child kept the pipes open (W-00000381); the driver side had the same shape: the reaper uses shell=True with a timeout, and run_driver times out a python driver whose executor and reviewer children inherit its pipes.
Decisions made: One shared helper in hooks/ instead of a fix per call site, because both close_work.py and drive_parallel.py already import from hooks/; start_new_session instead of process_group because Stage supports Python 3.9 and preexec_fn is unsafe with drive_parallel's thread pool; taskkill instead of a Windows job object to stay within stdlib without ctypes; the tests check that the descendant never writes its marker, because on POSIX subprocess.run only waits after the kill and returned on time even before the fix, so a duration check alone passes on Linux without the fix (verified: both new tests fail on Linux with the call sites reverted); docs/BLUEPRINT.md was not updated with the new module because it is outside the card's scope and no layer row fits a process utility cleanly.
Work not done: Not run on Windows locally; the Windows evidence is the windows-latest CI job. driver_lifecycle.close_via_close_work and escalate_via_escalate_work keep subprocess.run with a timeout on a python child that starts its own children; they are outside the scope.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6QNJ7Rrr2EULVp6Bqg)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w381-windows-timeouts` 의 76570e05 를 squash 했다(d2bb8a34).
- 성공 기준 1: `test_run_check_timeout_ends_the_whole_process_tree_in_time` 과
  `test_run_driver_timeout_ends_the_driver_process_tree_in_time` 이 1.5초 걸리는 손자 프로세스를 1초 제한으로 돌려 2초 안에
  돌아오고 손자가 표식을 쓰지 않았는지 본다. PR #100 의 stage 실행(45018596856)에서 windows-latest 3.9 와 3.12 의 샤드
  12개가 모두 통과했다. 두 시험에는 건너뛰는 조건이 없고, 샤드는 OS 마다 모든 시험을 한 번씩 돌린다. 이 카드를 등록할 때
  Windows 에서 1초 제한 시험은 5.48초였다(W-00000380 진단 실행). 이것은 영어 로캘의 CI 러너다. 이 카드는 인코딩을
  고치지 않아서 한국어 Windows 실행을 따로 하지 않았다.
- 성공 기준 2: 드라이버 쪽에도 같은 모양이 있었다. `drive_parallel.reap_after_timeout` 은 `shell=True` 와 timeout 을 쓰고,
  `drive_parallel.run_driver` 는 shell 이 없지만 드라이버의 자식이 파이프를 물려받는다. 둘 다 고쳤다.
  `driver_lifecycle.close_via_close_work` 와 `escalate_via_escalate_work` 에도 같은 모양이 남아 있다(후속 후보).
- 메인 세션이 다시 돌린 검사: scripts 와 hooks 전체 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 5 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
