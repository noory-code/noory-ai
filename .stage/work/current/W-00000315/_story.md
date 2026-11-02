---
id: W-00000315
title: 시도 횟수를 되돌릴 때 멈춘 판의 작업을 정리한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000315
promotion: not_applicable
review: passed
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, .stage/state/observations/O-00000051.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000315 시도 횟수를 되돌릴 때 멈춘 판의 작업을 정리한다

## Purpose

드라이버를 멈춘 뒤 되돌리고 다시 돌린 판이, 멈춘 판에서 살아남은 실행자나 리뷰어 작업 때문에 카드와 무관하게 깨지지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 중단된 역할이 기록된 상태에서 시도 횟수를 되돌리면, 그 역할의 venue 정리 명령(reaper)이 카드 경로와 역할을 받아 먼저 돈다는 것을 테스트가 확인한다
- 중단된 역할이 없으면 되돌릴 때 정리 명령을 부르지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: drive.py --reset-attempts now reads the selected item's recorded running_role and, when it is executor or reviewer, runs that role's venue reaper (the item's venue for the executor, the independent reviewer venue for the reviewer) through reap_turn with STAGE_TURN_ROLE set to the role and the card path, before reset_attempts changes the run state; with no recorded role nothing is reaped; the reap timeout falls back to MIN_COMMAND_TIMEOUT_SECONDS because --timeout has no default at that point; a test covers executor, reviewer, and no role, and checks the reaper saw the attempt count before the reset; SCHEMA_V4.md describes it; O-00000051 is closed and leaves the current-observation index; the CHANGELOG has a line.
Why: W-00000315 - a round after a stopped driver and a reset must not break because a job from the stopped round is still running.
Decisions made: Reap at reset rather than on KeyboardInterrupt, because the reset is the documented next step after any stop and a killed driver cannot run its own cleanup; reap only the interrupted role's venue, since a finished round was already reaped; keep resetting when the reaper is missing or fails, since reap_turn already warns in stdout and the work log and blocking the reset would leave the person no way forward; out-of-scope paths changed: none.
Work not done: A report the stopped job wrote before the reset is still in the log, but the next round starts counting from the log as it stands then, so it is not counted; the driver does not reap on KeyboardInterrupt itself.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `d9888873` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
or result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBxZnUwNTViMi9leGVjdXRvci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKTsgUGF0aCgnZXhlY3V0b3Itd29yay50eHQnKS53cml0ZV90ZXh0KCdkb25lXG4nLCBlbmNvZGluZz0ndXRmLTgnKTsgaW1wb3J0IGpzb24sIG9zOyBmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGg7IGxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKTsgbG9nLndyaXRlX3RleHQobG9nLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSArICdcbiMjIyBFeGVjdXRvciByZXBvcnRcbldoYXQgY2hhbmdlZDogdGVzdCBleGVjdXRvciBjaGFuZ2VkIGl0cyBkZWNsYXJlZCBwYXRoc1xuV2h5OiBleGVyY2lzZSB0aGUgZHJpdmVyIGNvbnRyYWN0XG5EZWNpc2lvbnMgbWFkZTogTm9uZVxuV29yayBub3QgZG9uZTogTm9uZVxuQ2hhbmdlZCBwYXRocyAoSlNPTik6XG4nICsganNvbi5kdW1wcyhbJ2V4ZWN1dG9yLXdvcmsudHh0J10pICsgJ1xuUmV2aWV3IHJlcXVlc3Q6IHJldmlldyBldmVyeSBzdWNjZXNzIGNyaXRlcmlvblxuJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Acceptance result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBxZnUwNTViMi9hY2NlcHRhbmNlLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Independent reviewer result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBxZnUwNTViMi9yZXZpZXdlci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKSIpCmV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4YzoKICAgIGlmIGV4Yy5jb2RlIG5vdCBpbiAoTm9uZSwgMCk6CiAgICAgICAgcmFpc2UKaW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
[exit 0]
APPROVED
Mode: execute
Target parent: W-00000001
Selected item: W-00000002
Executor: /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'cmFpc2UgU3lzdGVtRXhpdCgwKQ=='"'"'))'
Acceptance: /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'cmFpc2UgU3lzdGVtRXhpdCgwKQ=='"'"'))'
Independent reviewer: /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'aW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
Attempt: 1/unlimited
Iteration: 1/unlimited
Execution time: 0s/unlimited
WARNING: preflights.codex is not configured; continuing without a venue health check
----------------------------------------------------------------------
Ran 103 tests in 37.600s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793634000
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793634000. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp3p93upli/unattended/W-00000001-1793634000
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
Ran 731 tests in 165.166s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000315.md
Criteria:
- PASS: 중단된 역할이 기록된 상태에서 시도 횟수를 되돌리면, 그 역할의 venue 정리 명령(reaper)이 카드 경로와 역할을 받아 먼저 돈다는 것을 테스트가 확인한다
  Reason: test_reset_attempts_reaps_the_interrupted_roles_venue_first runs --reset-attempts with running_role executor (codex) and reviewer (claude), asserts the matching reaper wrote STAGE_TURN_ROLE, the resolved card path, and attempt_count 3 read before the reset, and it passes in the acceptance run (103 tests OK).
- PASS: 중단된 역할이 없으면 되돌릴 때 정리 명령을 부르지 않는다는 것을 테스트가 확인한다
  Reason: The same test's running_role None subtest asserts neither the codex nor the claude reaper marker exists after a successful reset, matching drive.py which skips reap_turn when no role is recorded; the executor report's Decisions made and Work not done are filled, and all changed paths lie inside the card scope as reported.
```

## Retrospective


## Promotion decision
