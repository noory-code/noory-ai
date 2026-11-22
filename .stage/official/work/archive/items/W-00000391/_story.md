---
id: W-00000391
title: 드라이버의 닫기와 보류 호출, 리뷰어 실행에도 프로세스 트리 시간 제한을 건다
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000391
promotion: not_applicable
review: passed
scope: stage/scripts/driver_lifecycle.py,stage/scripts/run_review.py,stage/scripts/tests/test_drive.py,stage/scripts/tests/test_run_review.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000391 드라이버의 닫기와 보류 호출, 리뷰어 실행에도 프로세스 트리 시간 제한을 건다

## Purpose

드라이버가 close_work 와 escalate_work 를 부를 때와 리뷰어를 띄울 때 시간이 넘으면 Windows 에서도 프로세스 트리 전체가 끝난다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- driver_lifecycle 의 close_via_close_work 와 escalate_via_escalate_work 가 hooks/stage_process.run_bounded 를 쓰고, 손자 프로세스가 남지 않는 시험이 있고 통과한다
- run_review.py 가 리뷰어에 시간 제한을 걸고, 시간이 넘으면 리뷰가 실패로 끝나는 시험이 있고 통과한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: driver_lifecycle.close_via_close_work and escalate_via_escalate_work run their scripts through stage_process.run_bounded, and the close outer margin is the named constant CLOSE_WORK_MARGIN_SECONDS; run_review.py runs the reviewer through run_bounded with a new `--timeout SECONDS` (default close_work.DEFAULT_REVIEW_TIMEOUT, 3600), and past it records the partial output plus a `run_review: <label> review timed out after Ns` line in the work log and exits 124; stage_process.kill_process_tree on POSIX sends SIGTERM to the group, waits up to TERM_GRACE_SECONDS (2s), then SIGKILL, and run_bounded on the main thread turns SIGTERM into SystemExit(143) so it ends its own command's group before exiting; test_drive.py covers close and escalate timeouts with a fake script that starts its child through run_bounded and asserts no descendant survives, and its four close mocks patch driver_lifecycle.run_bounded; test_run_review.py covers a reviewer past its limit (exit 124, partial output, no survivor), the default limit, invalid limits, and close_work's review limit reaching a reviewer run_review started; SCHEMA_V4.md documents `--timeout`; CHANGELOG entry under Unreleased.
Why: A time limit on the driver's close and escalate calls and on a reviewer has to end every process it started, on Windows and POSIX, or a stuck check or reviewer keeps running and keeps the call open.
Decisions made: run_review's default limit imports close_work.DEFAULT_REVIEW_TIMEOUT instead of repeating 3600, so the review timeout keeps one source; the reviewer's stderr now follows its stdout in the report instead of being interleaved, because run_bounded captures the two separately and adding a merge option was not needed for the purpose; the timeout exit status is 124, the GNU `timeout` convention; the nested-kill fix lives in stage_process.py because putting run_review's reviewer in its own group made close_work's --review-timeout stop reaching it on POSIX (verified: the reviewer's child survived with the new run_review and the old stage_process), and the same gap already existed for driver -> close_work -> checks; SIGTERM is handled only while run_bounded waits on the main thread, since signal handlers cannot be set on worker threads and drive_parallel's worker threads are the outermost level; Windows kill is unchanged because taskkill /T follows the parent chain; no decision record was written.
Work not done: A process that ignores SIGTERM at an inner level still escapes on POSIX after the outer SIGKILL, because SIGKILL to the outer group does not reach inner groups; a SIGTERM that arrives in the instant before run_bounded installs its handler terminates the caller with the default action and leaves its child running; the Windows branch was not run here (no Windows host).
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6PGPshT5eXUidWzv8a)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w391-bounded-driver-calls` 의 7c8e136d 를 squash 했다(089d0e1d).
- 성공 기준 1: `test_drive.py` 의 새 프로세스 트리 시험 2개가 손자 프로세스가 남지 않는지 본다. 고치기 전 코드에서 실패한다.
- 성공 기준 2: `test_run_review.py` 의 새 시험이 시간이 넘으면 리뷰가 124 로 끝나고 실패하는지 본다.
- PR #103 의 089d0e1d 에서 CI 30개가 모두 통과했다(windows-latest 3.9 와 3.12 샤드 12개 포함, 영어 로캘).
- 메인 세션이 다시 돌린 검사: scripts 와 hooks 전체 통과, 감사 오류 0건.
- 범위 밖 변경(`stage_process.py` 의 종료 방식, 리뷰어 보고의 출력 순서)은 사용자가 2026-11-22 에 받아들였다.
- `.stage/operations/verification.md` 의 한국어 Windows 실행은 아직 하지 않았다. #103 을 머지한 뒤 사용자가 돌린다.

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_run_review.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
- 2026-11-22 사용자가 한국어 Windows(Python 3.14, main ec37013b, 이 카드 포함)에서 `test_run_review.py` 와 `test_drive.py` 를 돌렸고 모두 통과했다.
