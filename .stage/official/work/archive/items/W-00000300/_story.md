---
id: W-00000300
title: 드라이버가 실행자가 바꾼 닫기 도구 몫의 카드 칸을 거절한다
kind: fix
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
retrospective_ref: R-00000300
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/driver_unattended.py, stage/scripts/driver_supervised.py, stage/scripts/tests/test_close_work.py, stage/scripts/tests/test_drive.py, stage/scripts/tests/test_template_v4.py, stage/skills/stage-drive/SKILL.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, .stage/settings.json, .stage/state/observations/O-00000054.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000300 드라이버가 실행자가 바꾼 닫기 도구 몫의 카드 칸을 거절한다

## Purpose

실행자가 검사를 돌리지 않고 카드의 verification 같은 닫기 도구 몫의 칸을 손으로 바꿔 기록이 사실과 달라지는 일을 막는다.

## Actions

- 지금 동작(O-00000054): W-00000286 을 드라이버로 실행할 때 Codex 실행자가 카드의 `verification` 을 손으로
  `passed` 로 바꿨다. 이 값은 `close_work.py` 가 검사를 돌린 뒤 쓰는 값이다. 실행 명령은 `promotion` 을 직접
  고치라고 하지만 닫기 도구 몫의 칸은 막지 않고, 드라이버도 검사하지 않는다.
- `close_work.py` 가 닫기 도구 몫의 칸(`status`, `verification`, `review`, `retrospective`, `retrospective_ref`)이
  실행자 턴 동안 바뀌었는지 판정하는 함수를 소유하고, 두 드라이버가 실행 보고 검증 옆에서 그 함수로 판을
  거절한다.
- 실행자 계약(드라이브 스킬, 스키마, 템플릿, 이 프로젝트의 실행 명령 둘)에 그 칸들을 고치지 않는다고 적는다.
- O-00000054 를 닫힌 관측으로 바꾼다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 실행자가 판 안에서 status, verification, review, retrospective, retrospective_ref 를 바꾸면 드라이버가 그 판을 거절한다는 것을 테스트가 확인한다
- 실행자 계약 문서와 실행 명령이 그 칸들을 실행자가 고치지 않는다고 같은 뜻으로 적는다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Across all attempts, close_work.py gained CLOSE_OWNED_FIELDS, close_owned_fields() that snapshots each close-owned frontmatter line, and close_owned_fields_error() that names and restores every changed field; driver_supervised.py and driver_unattended.py snapshot the card before each executor turn and run that check on every attempt after the repository snapshot, independently of the report check, executor exit status, or log errors, appending the field reason to any earlier failure; the drive skill, SCHEMA_V4, the settings template, and this project's two executor prompts say executors never edit those fields; O-00000054 is closed; tests cover the restore cases, every one of the five named fields from a literal list so dropping any from the code fails, a supervised rejection, supervised attempts that also fail on the report or exit 1, and an unattended attempt that also fails on the report.
Why: W-00000300 - verification: passed must come only from checks close_work ran, so an executor's hand-set close-owned value must neither pass an attempt nor survive into the next one.
Decisions made: Restore changed lines on rejection so the next attempt's snapshot never starts from a hand-set value; leave promotion out because the contract tells executors to set it; keep the check in close_work.py, which owns those fields; run it on every attempt outside the report check's short-circuit and append its reason instead of replacing an earlier one; run it after the repository snapshot so observed changed paths still show what the executor did; on a supervised --resume the snapshot is taken after the executor turn, like the repository fingerprint, so a change made before an interruption is not caught; test the five fields from a literal list rather than CLOSE_OWNED_FIELDS, and confirmed by dropping status and then retrospective_ref from the code that the test fails each time; out-of-scope path changed: stage/scripts/tests/test_drive_unattended.py, because the first criterion's review asked for an unattended-driver test and that driver's tests live there.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 첫 닫기(코드 커밋 `ccbd6903`)는 리뷰가 기준 1을 FAIL 로 판정해 막혔다. 두 번째
닫기(`99555d02`)는 보고 계약 FAIL 로, 세 번째 닫기는 다섯 칸 중 두 칸의 시험이 없다는 기준 1 FAIL 로 막혔다.
4판 코드 커밋 `5d1c05a1` 의 worktree 로, 세 판의 커밋에서 누적 보고를 옮겨 다시 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 74 tests in 19.647s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
tor result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBmeWtndzdpdC9leGVjdXRvci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKTsgUGF0aCgnZXhlY3V0b3Itd29yay50eHQnKS53cml0ZV90ZXh0KCdkb25lXG4nLCBlbmNvZGluZz0ndXRmLTgnKTsgaW1wb3J0IGpzb24sIG9zOyBmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGg7IGxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKTsgbG9nLndyaXRlX3RleHQobG9nLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSArICdcbiMjIyBFeGVjdXRvciByZXBvcnRcbldoYXQgY2hhbmdlZDogdGVzdCBleGVjdXRvciBjaGFuZ2VkIGl0cyBkZWNsYXJlZCBwYXRoc1xuV2h5OiBleGVyY2lzZSB0aGUgZHJpdmVyIGNvbnRyYWN0XG5EZWNpc2lvbnMgbWFkZTogTm9uZVxuV29yayBub3QgZG9uZTogTm9uZVxuQ2hhbmdlZCBwYXRocyAoSlNPTik6XG4nICsganNvbi5kdW1wcyhbJ2V4ZWN1dG9yLXdvcmsudHh0J10pICsgJ1xuUmV2aWV3IHJlcXVlc3Q6IHJldmlldyBldmVyeSBzdWNjZXNzIGNyaXRlcmlvblxuJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Acceptance result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBmeWtndzdpdC9hY2NlcHRhbmNlLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Independent reviewer result:
$ /usr/local/bin/python3 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3RtcC90bXBmeWtndzdpdC9yZXZpZXdlci1jb3VudCcpOyBwYXRoLndyaXRlX3RleHQoc3RyKGludChwYXRoLnJlYWRfdGV4dChlbmNvZGluZz0ndXRmLTgnKSkgKyAxKSBpZiBwYXRoLmV4aXN0cygpIGVsc2UgJzEnLCBlbmNvZGluZz0ndXRmLTgnKSIpCmV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4YzoKICAgIGlmIGV4Yy5jb2RlIG5vdCBpbiAoTm9uZSwgMCk6CiAgICAgICAgcmFpc2UKaW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
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
Ran 98 tests in 29.683s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793456790
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793456790. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpyplnb9y4/unattended/W-00000001-1793456790
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
Ran 715 tests in 133.030s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000300.md
Criteria:
- PASS: 실행자가 판 안에서 status, verification, review, retrospective, retrospective_ref 를 바꾸면 드라이버가 그 판을 거절한다는 것을 테스트가 확인한다
  Reason: New test_every_named_close_owned_field_is_named_and_restored changes each of the five fields from a literal list and asserts it is named and restored, so dropping any field from CLOSE_OWNED_FIELDS fails it; driver tests in both drivers cover rejection via that same check, and all four suites pass.
- PASS: 실행자 계약 문서와 실행 명령이 그 칸들을 실행자가 고치지 않는다고 같은 뜻으로 적는다
  Reason: The drive skill, SCHEMA_V4.md, the v4 settings template, and both .stage/settings.json executor prompts name the same five fields as not executor-edited and say the driver rejects and restores; this round changed only test_close_work.py.
- PASS: Executor report follows the purpose and scope-boundary reporting contract
  Reason: Decisions made restates every decision still in effect plus the new literal-list test decision and reports the out-of-scope test_drive_unattended.py crossing with its reason (now correctly attributed to the first criterion's review); Work not done: None is accurate; changed paths cover all attempts.
```

## Retrospective

[R-00000300](../../retrospectives/R-00000300.md).

## Promotion decision
