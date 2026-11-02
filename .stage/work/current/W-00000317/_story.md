---
id: W-00000317
title: 실패한 리뷰가 남긴 파일이 다음 판에 섞이지 않게 한다
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
retrospective_ref: R-00000317
promotion: not_applicable
review: passed
scope: stage/scripts/driver_supervised.py, stage/scripts/driver_runstate.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000317 실패한 리뷰가 남긴 파일이 다음 판에 섞이지 않게 한다

## Purpose

리뷰가 판정 파일 밖에 쓴 변경이, 사람이 치우지 않은 채 다음 판의 항목 커밋에 리뷰 없이 섞여 들어가지 않게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰가 파일을 써서 실패한 뒤, 그 파일이 리뷰 전 상태로 돌아오지 않았으면 다음 판이 실행자를 돌리지 않고 멈추며 그 경로를 알리고, 되돌렸으면 평소대로 돈다는 것을 테스트가 확인한다
- 사람이 --reset-attempts 로 그 변경을 받아들이면 다음 판이 막히지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: close_work.py gains review_written_paths(), which reject_review_writes() now uses; when a supervised review writes files, the driver records review_written_paths in the item's run state, mapping each path to its pre-review snapshot value ("" when it did not exist); the next supervised round compares those paths with the current repository before preflight and refuses to start, naming the paths, while any still differs; restoring them lets the round run, and reset_attempts drops the record as the person's explicit acceptance; load_run_state rejects a review_written_paths value that is not a mapping of non-empty paths to strings; tests cover leaving, restoring, and accepting the file (checking whether the executor ran again) and the state validation; SCHEMA_V4.md documents the field and the rule; the CHANGELOG has a line.
Why: W-00000317 - changes a failed review wrote must not enter the next item commit without the person restoring or accepting them.
Decisions made: Block only on the paths the failed review wrote, compared with their pre-review state, instead of requiring a clean working tree, which would also block the output deliberately kept for the person at the attempt cap; use --reset-attempts as the acceptance path because it already records a reason and is the person's explicit step; check before preflight so a blocked round spends nothing; out-of-scope paths changed: none.
Work not done: The unattended driver reviews through close_work, which fails such reviews but does not carry this record across runs; close_work's own failure message already tells the person to discard the files.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `bb4231e7` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
or result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXAwbjc4d2FsYS9leGVjdXRvci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKTsgUGF0aCgnZXhlY3V0b3Itd29yay50eHQnKS53cml0ZV90ZXh0KCdkb25lXG4nLCBlbmNvZGluZz0ndXRmLTgnKTsgaW1wb3J0IGpzb24sIG9zOyBmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGg7IGxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKTsgbG9nLndyaXRlX3RleHQobG9nLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSArICdcbiMjIyBFeGVjdXRvciByZXBvcnRcbldoYXQgY2hhbmdlZDogdGVzdCBleGVjdXRvciBjaGFuZ2VkIGl0cyBkZWNsYXJlZCBwYXRoc1xuV2h5OiBleGVyY2lzZSB0aGUgZHJpdmVyIGNvbnRyYWN0XG5EZWNpc2lvbnMgbWFkZTogTm9uZVxuV29yayBub3QgZG9uZTogTm9uZVxuQ2hhbmdlZCBwYXRocyAoSlNPTik6XG4nICsganNvbi5kdW1wcyhbJ2V4ZWN1dG9yLXdvcmsudHh0J10pICsgJ1xuUmV2aWV3IHJlcXVlc3Q6IHJldmlldyBldmVyeSBzdWNjZXNzIGNyaXRlcmlvblxuJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Acceptance result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXAwbjc4d2FsYS9hY2NlcHRhbmNlLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Independent reviewer result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXAwbjc4d2FsYS9yZXZpZXdlci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKSIpCmV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4YzoKICAgIGlmIGV4Yy5jb2RlIG5vdCBpbiAoTm9uZSwgMCk6CiAgICAgICAgcmFpc2UKaW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
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
Ran 105 tests in 41.632s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793634704
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793634704. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpucj1xx1p/unattended/W-00000001-1793634704
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
Ran 734 tests in 173.116s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000317.md
Criteria:
- PASS: 리뷰가 파일을 써서 실패한 뒤, 그 파일이 리뷰 전 상태로 돌아오지 않았으면 다음 판이 실행자를 돌리지 않고 멈추며 그 경로를 알리고, 되돌렸으면 평소대로 돈다는 것을 테스트가 확인한다
  Reason: test_files_a_failed_review_left_block_the_next_round_until_restored_or_accepted checks the recorded mapping of reviewer-wrote.txt to an empty pre-review state, that the 'left' round exits non-zero naming the path while the executor marker stays 'x', and that the 'restored' round runs the executor again ('xx'); the pre-preflight check in driver_supervised.py implements this and test_drive.py passes (105 tests OK).
- PASS: 사람이 --reset-attempts 로 그 변경을 받아들이면 다음 판이 막히지 않는다는 것을 테스트가 확인한다
  Reason: The 'accepted' subtest runs --reset-attempts with a reason, asserts exit 0, then asserts the next round prints no 'still changed' block and runs the executor again ('xx'); _record_reset in driver_runstate.py drops review_written_paths so the record is cleared.
```

## Retrospective


## Promotion decision
