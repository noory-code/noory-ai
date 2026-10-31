---
id: W-00000307
title: 시도 횟수를 되돌릴 때 지난 판정과 쌓인 변경 경로도 지운다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000307
promotion: not_applicable
review: passed
scope: stage/scripts/driver_runstate.py, stage/scripts/tests/test_drive.py, stage/docs/SCHEMA_V4.md, .stage/state/observations/O-00000047.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000307 시도 횟수를 되돌릴 때 지난 판정과 쌓인 변경 경로도 지운다

## Purpose

카드를 다시 설계하고 시도 횟수를 되돌린 뒤의 다음 판이 버린 설계의 판정과 변경 경로 때문에 카드와 무관한 이유로 실패하지 않게 한다.

## Actions

- 지금 동작(O-00000047): `driver_runstate.reset_attempts()` 는 시도 횟수와 몇몇 재개 칸을 지우지만, 쌓인
  `executor_changed_paths` 를 남기고 판정 파일(`.stage/.runtime/driver/verdicts/<카드>.json`)은 손대지 않는다. 다시 설계한
  카드의 다음 판이 지난 판정으로 좁은 재리뷰를 돌거나, 버린 설계의 변경 경로와 실행 보고가 어긋나 시도를 태운다.
- 되돌릴 때 지난 판정 파일과 W-00000305 의 기준 지문 파일을 지워 다음 판이 전체 리뷰로 돌게 한다. 상태나 로그
  기록이 실패하면 지운 파일을 되살린다.
- `executor_changed_paths` 는 다 지우지 않는다. 드라이버는 이전 판의 결과를 작업 트리에 남기고(`restore_item_output` 은
  mixed reset), 항목 커밋이 `base_head` 이후 전부를 하나로 합친다. 그래서 다 지우면 사람이 남겨 둔 결과가 커밋에는
  들어가는데 리뷰에서는 빠진다. `base_head` 와 아직 다른 경로만 남기고 사람이 되돌린 경로는 뺀다(드라이버 스냅숏과
  같이 추적 파일과 무시되지 않은 미추적 파일 기준).
- 작업 로그의 되돌림 기록에 지운 판정 파일과 뺀·남긴 경로를 적는다. `stage/docs/SCHEMA_V4.md` 의 되돌림 설명을 맞춘다.
- O-00000047 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 시도 횟수를 되돌리면 지난 판정 파일과 그 기준 지문이 지워지고, 쌓인 실행자 변경 경로에서 사람이 되돌린 경로는 빠지되 기준 커밋과 아직 다른 경로는 남으며, 작업 로그에 그 사실이 남는다는 것을 테스트가 확인한다
- 되돌림 상태를 기록하지 못하면 지운 판정 파일과 기준 지문이 되살아나고 실행 상태가 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: driver_runstate.reset_attempts() now removes the item's review verdict and criteria digest before writing the reset state, restores both files and the previous run state when the state or log write fails, and replaces executor_changed_paths with only the recorded paths that still differ from base_head (git diff against base_head plus untracked non-ignored files, the driver's snapshot view; ls-files when there is no base commit), refusing the reset when Git cannot answer; the work-log reset entry lists what was cleared and which paths were dropped or kept; tests use real Git bases for the reset cases, check removal, the dropped/kept split and the log lines, and check that a failed state write restores the verdict, digest and state; SCHEMA_V4 describes the reset; O-00000047 is closed and leaves the current-observation index; the CHANGELOG has a line.
Why: W-00000307 - a reset after redesigning a card must not let the discarded design's verdict force a narrow re-review or its paths break the next executor report.
Decisions made: Keep still-changed paths instead of clearing them all, because the driver leaves earlier rounds' output in the working tree and the item commit squashes everything since base_head, so clearing would hide kept output from review (the card was amended in its own commit before this one); remove the review files before the state write and restore them on failure, because removing after a successful write would leave a failed removal unretryable once attempt_count is zero; fail closed when Git cannot compare paths; leave base_head unchanged, since it marks where the item's output starts; out-of-scope paths changed: none.
Work not done: None
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `6b88ba54` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
or result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBveGJuanlpYy9leGVjdXRvci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKTsgUGF0aCgnZXhlY3V0b3Itd29yay50eHQnKS53cml0ZV90ZXh0KCdkb25lXG4nLCBlbmNvZGluZz0ndXRmLTgnKTsgaW1wb3J0IGpzb24sIG9zOyBmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGg7IGxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKTsgbG9nLndyaXRlX3RleHQobG9nLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSArICdcbiMjIyBFeGVjdXRvciByZXBvcnRcbldoYXQgY2hhbmdlZDogdGVzdCBleGVjdXRvciBjaGFuZ2VkIGl0cyBkZWNsYXJlZCBwYXRoc1xuV2h5OiBleGVyY2lzZSB0aGUgZHJpdmVyIGNvbnRyYWN0XG5EZWNpc2lvbnMgbWFkZTogTm9uZVxuV29yayBub3QgZG9uZTogTm9uZVxuQ2hhbmdlZCBwYXRocyAoSlNPTik6XG4nICsganNvbi5kdW1wcyhbJ2V4ZWN1dG9yLXdvcmsudHh0J10pICsgJ1xuUmV2aWV3IHJlcXVlc3Q6IHJldmlldyBldmVyeSBzdWNjZXNzIGNyaXRlcmlvblxuJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Acceptance result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBveGJuanlpYy9hY2NlcHRhbmNlLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Independent reviewer result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBveGJuanlpYy9yZXZpZXdlci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKSIpCmV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4YzoKICAgIGlmIGV4Yy5jb2RlIG5vdCBpbiAoTm9uZSwgMCk6CiAgICAgICAgcmFpc2UKaW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
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
Ran 101 tests in 33.103s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793460053
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793460053. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmprliumih5/unattended/W-00000001-1793460053
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
Ran 719 tests in 147.379s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000307.md
Criteria:
- PASS: 시도 횟수를 되돌리면 지난 판정 파일과 그 기준 지문이 지워지고, 쌓인 실행자 변경 경로에서 사람이 되돌린 경로는 빠지되 기준 커밋과 아직 다른 경로는 남으며, 작업 로그에 그 사실이 남는다는 것을 테스트가 확인한다
  Reason: test_reset_attempts_resets_limit_state_and_logs_reason uses a real Git base and asserts the verdict and digest are removed, reverted.txt and removed.txt are dropped while tracked.txt and untracked.txt are kept, and the Cleared/dropped/kept log lines are written; it passes, and the Decisions made field matches the card's amended Actions and reports no out-of-scope paths.
- PASS: 되돌림 상태를 기록하지 못하면 지운 판정 파일과 기준 지문이 되살아나고 실행 상태가 그대로라는 것을 테스트가 확인한다
  Reason: test_reset_attempts_restores_the_review_when_the_state_cannot_be_written makes the first write_run_state fail and asserts an error, an unchanged run state, and restored verdict and digest contents; _record_reset restores both through _restore_files, and the test passes.
```

## Retrospective


## Promotion decision
