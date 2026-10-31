---
id: W-00000302
title: 리뷰 판정 검증을 닫기 도구와 드라이버가 한 함수로 나눠 쓴다
kind: chore
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000302
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/driver_review.py, stage/scripts/tests/test_close_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000302 리뷰 판정 검증을 닫기 도구와 드라이버가 한 함수로 나눠 쓴다

## Purpose

리뷰 판정 JSON 의 기준별 검증 규칙이 두 곳에 따로 있어 한쪽만 고쳐지면 닫기와 드라이버가 같은 판정을 다르게 받아들이는 일을 막는다.

## Actions

- 지금 동작: `close_work.load_review_verdict()` 와 `driver_review.load_driver_review_verdict()` 가 기준 항목마다
  문자열·한 줄·중복·PASS/FAIL·approved 일치 검사를 각자 한다. 드라이버 쪽은 `reviewed_in_round` 를 하나 더 받으려고
  같은 검사를 다시 적었다.
- 기준 항목 검증을 `close_work.py` 의 함수 하나로 모으고 드라이버가 그것을 부른다. 오류 문구는 그대로 둔다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 닫기 도구와 드라이버가 판정 기준 항목 검증을 한 함수로 하고, 기존 오류 문구와 동작이 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: close_work.py gains normalize_review_verdict(raw, merged=False), which holds every verdict rule and, for a driver-merged verdict, also requires a positive reviewed_in_round on each criterion; load_review_verdict() reads the file and calls it; driver_review.load_driver_review_verdict() keeps its pre-checks, which return the first-round error, and then calls the shared function with merged=True instead of repeating the rules; a test pins first-round and merged results and error messages and checks that the driver's function is close_work's.
Why: W-00000302 - one rule set must decide whether a verdict is valid for both close and the driver.
Decisions made: Keep every existing error message, including the merged-verdict key message, so evidence and tests that match them do not change; keep the driver's pre-checks so a malformed file still reports the first-round error as before; out-of-scope paths changed: none.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `3af4cc52` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 73 tests in 19.685s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
tor result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBzOGxhOWJiOC9leGVjdXRvci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKTsgUGF0aCgnZXhlY3V0b3Itd29yay50eHQnKS53cml0ZV90ZXh0KCdkb25lXG4nLCBlbmNvZGluZz0ndXRmLTgnKTsgaW1wb3J0IGpzb24sIG9zOyBmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGg7IGxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKTsgbG9nLndyaXRlX3RleHQobG9nLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSArICdcbiMjIyBFeGVjdXRvciByZXBvcnRcbldoYXQgY2hhbmdlZDogdGVzdCBleGVjdXRvciBjaGFuZ2VkIGl0cyBkZWNsYXJlZCBwYXRoc1xuV2h5OiBleGVyY2lzZSB0aGUgZHJpdmVyIGNvbnRyYWN0XG5EZWNpc2lvbnMgbWFkZTogTm9uZVxuV29yayBub3QgZG9uZTogTm9uZVxuQ2hhbmdlZCBwYXRocyAoSlNPTik6XG4nICsganNvbi5kdW1wcyhbJ2V4ZWN1dG9yLXdvcmsudHh0J10pICsgJ1xuUmV2aWV3IHJlcXVlc3Q6IHJldmlldyBldmVyeSBzdWNjZXNzIGNyaXRlcmlvblxuJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Acceptance result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBzOGxhOWJiOC9hY2NlcHRhbmNlLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Independent reviewer result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBzOGxhOWJiOC9yZXZpZXdlci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKSIpCmV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4YzoKICAgIGlmIGV4Yy5jb2RlIG5vdCBpbiAoTm9uZSwgMCk6CiAgICAgICAgcmFpc2UKaW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
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
Ran 98 tests in 31.429s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793455899
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793455899. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp2xe3tsq1/unattended/W-00000001-1793455899
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
Ran 713 tests in 151.368s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000302.md
Criteria:
- PASS: 닫기 도구와 드라이버가 판정 기준 항목 검증을 한 함수로 하고, 기존 오류 문구와 동작이 그대로라는 것을 테스트가 확인한다
  Reason: driver_review.load_driver_review_verdict now delegates per-criterion checks to close_work.normalize_review_verdict(merged=True) after its unchanged pre-checks, every error string including the merged-key message is preserved in the same check order, the new test pins first-round and merged results and messages and asserts the driver's function is close_work's, both acceptance suites pass (73 and 98 tests), and the executor report's Decisions made and Work not done lines state the kept messages and pre-checks with no out-of-scope paths, matching the four in-scope changed paths.
```

## Retrospective

[R-00000302](../../retrospectives/R-00000302.md).

## Promotion decision
