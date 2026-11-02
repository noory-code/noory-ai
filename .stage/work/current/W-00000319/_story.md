---
id: W-00000319
title: CI 에서 드러난 Stage 의 Windows·작업 폴더 버그를 고친다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000319
promotion: not_applicable
review: passed
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000319 CI 에서 드러난 Stage 의 Windows·작업 폴더 버그를 고친다

## Purpose

Stage 시험과 범위 넘음 알림이 Windows 와 다른 작업 폴더에서도 로컬과 같게 동작해 CI 가 다시 초록이 되게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Windows 에서 '/dev/null' 처럼 드라이브 없이 쓴 POSIX 장치 경로가 범위 넘음으로 알려지지 않는다는 것을 시험이 확인한다
- stage 폴더에서 돌려도(CI 와 같게) scripts·hooks 시험 전체가 통과하고, 현재 폴더를 옮기는 시험이 임시 폴더를 지우기 전에 원래 폴더로 돌아온다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: scratch_target() now treats a target whose text, with backslashes read as slashes, starts with /dev/ as a device before any path math, replacing the resolved-path check that missed drive-less POSIX paths on Windows; a test checks /dev/null, its backslash form, /dev/stderr, and that a relative dev/null stays a workspace path; the cwd test restores the working directory in a finally block inside the temporary-folder context instead of through addCleanup, which ran after the folder deletion; test_project_claude_reviewer_may_write_only_its_verdict_file runs the project review command with the project root as its working directory, as drivers and close_work do; the CHANGELOG has a line.
Why: W-00000319 - Stage's tests and scope report must behave the same on Windows and from any working directory, so CI is green again.
Decisions made: Judge device paths from their text because Windows path math cannot tell a drive-less /dev/null from a path on the current drive; fix the template test rather than make the project command absolute, because review commands always run from the project root; reproduced the template failure locally by running the suites from stage/ as CI does; out-of-scope paths changed: none.
Work not done: The Windows-specific fixes could not run on Windows here; CI on the pull request is the check. The Ubuntu Python 3.9 runner failure is a separate card.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `68ebb688` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 263 tests in 1.528s

OK (skipped=1)

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 398 tests in 5.679s

OK (skipped=1)

$ cd stage && python3 -m unittest discover -s scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793659732
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793659732. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp0j6i6j6y/unattended/W-00000001-1793659732
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 735 tests in 151.571s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000319.md
Criteria:
- PASS: Windows 에서 '/dev/null' 처럼 드라이브 없이 쓴 POSIX 장치 경로가 범위 넘음으로 알려지지 않는다는 것을 시험이 확인한다
  Reason: scratch_target now treats any target whose slash-normalized text starts with /dev/ as a device before any Path math, and the new test_posix_device_paths_are_scratch_even_without_a_drive checks /dev/null, \dev\null and /dev/stderr as scratch and relative dev/null as not; I ran python3 -m unittest discover -s hooks/tests -p test_stage_guard.py -q from stage/ on Linux (263 tests OK, 1 skipped) but did not run it on Windows, which the executor's Work not done also states.
- PASS: stage 폴더에서 돌려도(CI 와 같게) scripts·hooks 시험 전체가 통과하고, 현재 폴더를 옮기는 시험이 임시 폴더를 지우기 전에 원래 폴더로 돌아온다
  Reason: From stage/ I ran python3 -m unittest discover -s scripts/tests -q (735 tests OK, 2 skipped) and python3 -m unittest discover -s hooks/tests -q (398 tests OK, 1 skipped); the cwd test now calls os.chdir(previous) in a finally block inside the TemporaryDirectory context, so it returns before the folder is deleted, and the template test runs the review command with cwd set to the project root.
```

## Retrospective


## Promotion decision
