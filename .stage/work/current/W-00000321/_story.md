---
id: W-00000321
title: Windows 셸 파서가 드라이브에 붙인 /dev/null 도 장치로 알아본다
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
retrospective_ref: R-00000321
promotion: not_applicable
review: passed
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000321 Windows 셸 파서가 드라이브에 붙인 /dev/null 도 장치로 알아본다

## Purpose

Windows 에서 출력을 /dev/null 로 버리는 셸 명령이 범위 넘음으로 알려지지 않게 해, W-00000319 이 겨눈 결과를 실제로 낸다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 셸 파서가 드라이브에 붙여 낸 장치 경로('C:\dev\null', 'C:/dev/stderr')가 범위 넘음으로 알려지지 않고, 'C:\dev\proj\app.py' 같은 일반 경로는 장치로 보지 않는다는 것을 시험이 확인한다
- PR 의 Windows CI(Python 3.9·3.12)에서 Stage hooks 시험이 통과한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: scratch_target() also treats a target whose text, with backslashes read as slashes, is a drive letter followed by /dev/ and a known device name (null, zero, full, random, urandom, tty, stdin, stdout, stderr, or fd/N) as a device, through WINDOWS_ANCHORED_DEVICE_RE; the device test adds C:\dev\null, C:/dev/stderr, and d:\dev\fd\2 as devices and C:\dev\proj\app.py and C:/dev/nullify.txt as ordinary paths; the unreleased CHANGELOG line from W-00000319 now describes the final behavior.
Why: W-00000321 - on Windows a shell command that discards output to /dev/null must not be reported as a scope crossing, which W-00000319 aimed at but did not achieve.
Decisions made: Match only known device names after a drive letter, so a workspace or file under C:\dev\ is never mistaken for a device; fix the report check rather than the shell parser's anchoring, which the .stage gates also rely on; amend the unreleased W-00000319 changelog line instead of adding a second one; out-of-scope paths changed: none.
Work not done: Windows cannot run here; the pull request's Windows CI is the check for the second criterion.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `c91f196f` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

두 번째 기준의 증거: PR noory-code/noory-ai#24 의 CI 가 커밋 `c91f196f` 에서 모두 통과했다. Stage 워크플로의
`test (windows-latest, 3.9)` 와 `test (windows-latest, 3.12)` 가 성공했다(run 41542264164).


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 263 tests in 1.574s

OK (skipped=1)

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 398 tests in 5.873s

OK (skipped=1)

$ cd stage && python3 -m unittest discover -s scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793661302
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793661302. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp2ltn4n9n/unattended/W-00000001-1793661302
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
Ran 736 tests in 153.165s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000321.md
Criteria:
- PASS: 셸 파서가 드라이브에 붙여 낸 장치 경로('C:\dev\null', 'C:/dev/stderr')가 범위 넘음으로 알려지지 않고, 'C:\dev\proj\app.py' 같은 일반 경로는 장치로 보지 않는다는 것을 시험이 확인한다
  Reason: scratch_target() now matches WINDOWS_ANCHORED_DEVICE_RE (drive + /dev/ + known device name only) and the scope report at stage_guard.py:664 skips scratch targets; test_posix_device_paths_are_scratch_even_without_a_drive asserts C:\dev\null, C:/dev/stderr, d:\dev\fd\2 are devices and C:\dev\proj\app.py, C:/dev/nullify.txt are not; I ran python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q and it showed 263 tests OK (1 skipped).
- PASS: PR 의 Windows CI(Python 3.9·3.12)에서 Stage hooks 시험이 통과한다
  Reason: I did not observe the CI myself (gh run view needed approval and was not run); the card's Verification records PR noory-code/noory-ai#24 run 41542264164 on commit c91f196f, which is the HEAD reviewed here, with test (windows-latest, 3.9) and test (windows-latest, 3.12) succeeding, and the executor reported this CI as the check for this criterion.
```

## Retrospective


## Promotion decision
