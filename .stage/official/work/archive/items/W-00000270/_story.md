---
id: W-00000270
title: 닫기 전 리뷰에 일반 검사와 따로 제한 시간을 준다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000270
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/operations/review.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000077
---

# W-00000270 닫기 전 리뷰에 일반 검사와 따로 제한 시간을 준다

## Purpose

생각 깊이가 높은 리뷰가 일반 검사용 제한 시간에 걸려 닫기가 막히지 않게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- close_work 가 리뷰 명령에 일반 검사와 다른 제한 시간을 쓰고, 그 값을 인자로 바꿀 수 있다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress

- 2026-10-31 Claude Code 클라우드 세션이 `claude/w268-cloud` 에서 이 카드를 실행했다(커밋
  `558ac6e7`). 실행 보고는 사용자의 직접 지시에 따랐다고 적었다. 이 카드의 Actions 가 비어 있어
  `--review-timeout` 기본값 3600초는 실행자가 정했다. 실제 리뷰 시간을 재서 나온 값은 아니다.
  venue 예외는 실행 뒤에 DE-00000077 로 기록했다.
- 범위 밖 변경: `stage/scripts/driver_lifecycle.py` 와 `stage/scripts/tests/test_drive.py`.
  드라이버는 `close_work` 를 `timeout + 60` 초 뒤에 끝내므로, 리뷰 기본값 3600초를 그대로 두면
  드라이버가 리뷰 도중 `close_work` 를 끝낸다. 실행자는 드라이버가 자기 `--timeout` 을
  `--review-timeout` 으로 넘기게 해서 드라이버 동작을 이전과 같게 유지했다. 이 넘음은 실행
  보고에 적혀 있다.
- 실행자가 남긴 일: 드라이버가 닫을 때도 긴 리뷰 시간을 쓰려면 드라이버의 바깥 제한 시간이
  검사와 리뷰를 함께 셈해야 한다. 드라이버 설계 변경이라 이 카드 밖이다.
- 실행 보고는 커밋 메시지에서 `.stage/.runtime/driver/logs/W-00000270.md` 로 옮겼다.
- 닫기는 HEAD `558ac6e7` 을 대상으로 한다. `.stage/` 는 `0101c3e1` 상태로, 리뷰 명령과 모델 고정
  시험은 W-00000286 커밋 `1ab2fdf5` 상태로 커밋하지 않고 덮어 썼다.


## Verification


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 62 tests in 10.531s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 62 tests in 10.838s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (14 earlier lines omitted)
dW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcpOyBQYXRoKCdleGVjdXRvci13b3JrLnR4dCcpLndyaXRlX3RleHQoJ2RvbmVcbicsIGVuY29kaW5nPSd1dGYtOCcpOyBpbXBvcnQganNvbiwgb3M7IGZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aDsgbG9nID0gUGF0aChvcy5lbnZpcm9uWydTVEFHRV9XT1JLX0xPR19QQVRIJ10pOyBsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgJ1xuIyMjIEV4ZWN1dG9yIHJlcG9ydFxuV2hhdCBjaGFuZ2VkOiB0ZXN0IGV4ZWN1dG9yIGNoYW5nZWQgaXRzIGRlY2xhcmVkIHBhdGhzXG5XaHk6IGV4ZXJjaXNlIHRoZSBkcml2ZXIgY29udHJhY3RcbkNoYW5nZWQgcGF0aHMgKEpTT04pOlxuJyArIGpzb24uZHVtcHMoWydleGVjdXRvci13b3JrLnR4dCddKSArICdcblJldmlldyByZXF1ZXN0OiByZXZpZXcgZXZlcnkgc3VjY2VzcyBjcml0ZXJpb25cbicsIGVuY29kaW5nPSd1dGYtOCcp'"'"'))'
[exit 0]

Acceptance result:
$ /opt/homebrew/opt/python@3.15/bin/python3.15 -c 'import base64;exec(base64.b64decode('"'"'ZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3Zhci9mb2xkZXJzL3dnLzZobmRfZjI1NV96NG5nazd5bndwdHltNDAwMDBnbi9UL3RtcGpuejY4cWRfL2FjY2VwdGFuY2UtY291bnQnKTsgcGF0aC53cml0ZV90ZXh0KHN0cihpbnQocGF0aC5yZWFkX3RleHQoZW5jb2Rpbmc9J3V0Zi04JykpICsgMSkgaWYgcGF0aC5leGlzdHMoKSBlbHNlICcxJywgZW5jb2Rpbmc9J3V0Zi04Jyk='"'"'))'
[exit 0]

Independent reviewer result:
$ /opt/homebrew/opt/python@3.15/bin/python3.15 -c 'import base64;exec(base64.b64decode('"'"'dHJ5OgogICAgZXhlYygiZnJvbSBwYXRobGliIGltcG9ydCBQYXRoOyBwYXRoID0gUGF0aCgnL3Zhci9mb2xkZXJzL3dnLzZobmRfZjI1NV96NG5nazd5bndwdHltNDAwMDBnbi9UL3RtcGpuejY4cWRfL3Jldmlld2VyLWNvdW50Jyk7IHBhdGgud3JpdGVfdGV4dChzdHIoaW50KHBhdGgucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpKSArIDEpIGlmIHBhdGguZXhpc3RzKCkgZWxzZSAnMScsIGVuY29kaW5nPSd1dGYtOCcpIikKZXhjZXB0IFN5c3RlbUV4aXQgYXMgZXhjOgogICAgaWYgZXhjLmNvZGUgbm90IGluIChOb25lLCAwKToKICAgICAgICByYWlzZQppbXBvcnQganNvbiwgb3MKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCmxvZyA9IFBhdGgob3MuZW52aXJvblsnU1RBR0VfV09SS19MT0dfUEFUSCddKQpyZXBvcnQgPSAoJ1xuIyMjIFJldmlld2VyIHJlcG9ydFxuQ1JJVEVSSUEgVkVSRElDVDpcbi0gY3JpdGVyaW9uOiBQQVNTIC0gdGVzdCByZXZpZXdlciBpbnNwZWN0ZWQgdGhlIGlucHV0c1xuQVBQUk9WRURcbk9VVC1PRi1DUklURVJJQSBPQlNFUlZBVElPTlM6XG4tIE5vbmVcbicpCmxvZy53cml0ZV90ZXh0KGxvZy5yZWFkX3RleHQoZW5jb2Rpbmc9J3V0Zi04JykgKyByZXBvcnQsIGVuY29kaW5nPSd1dGYtOCcpClBhdGgob3MuZW52aXJvblsnU1RBR0VfUkVWSUVXX1ZFUkRJQ1RfRklMRSddKS53cml0ZV90ZXh0KAogICAganNvbi5kdW1wcyh7J2NyaXRlcmlhJzogW3snY3JpdGVyaW9uJzogJ2NyaXRlcmlvbicsICd2ZXJkaWN0JzogJ1BBU1MnLCAncmVhc29uJzogJ3Rlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHMnfV0sICdhcHByb3ZlZCc6IFRydWV9KSwgZW5jb2Rpbmc9J3V0Zi04JykKcHJpbnQoJ0FQUFJPVkVEJyk='"'"'))'
[exit 0]
APPROVED
Mode: execute
Target parent: W-00000001
Selected item: W-00000002
Executor: /opt/homebrew/opt/python@3.15/bin/python3.15 -c 'import base64;exec(base64.b64decode('"'"'cmFpc2UgU3lzdGVtRXhpdCgwKQ=='"'"'))'
Acceptance: /opt/homebrew/opt/python@3.15/bin/python3.15 -c 'import base64;exec(base64.b64decode('"'"'cmFpc2UgU3lzdGVtRXhpdCgwKQ=='"'"'))'
Independent reviewer: /opt/homebrew/opt/python@3.15/bin/python3.15 -c 'import base64;exec(base64.b64decode('"'"'aW1wb3J0IGpzb24sIG9zCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApsb2cgPSBQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1dPUktfTE9HX1BBVEgnXSkKcmVwb3J0ID0gKCdcbiMjIyBSZXZpZXdlciByZXBvcnRcbkNSSVRFUklBIFZFUkRJQ1Q6XG4tIGNyaXRlcmlvbjogUEFTUyAtIHRlc3QgcmV2aWV3ZXIgaW5zcGVjdGVkIHRoZSBpbnB1dHNcbkFQUFJPVkVEXG5PVVQtT0YtQ1JJVEVSSUEgT0JTRVJWQVRJT05TOlxuLSBOb25lXG4nKQpsb2cud3JpdGVfdGV4dChsb2cucmVhZF90ZXh0KGVuY29kaW5nPSd1dGYtOCcpICsgcmVwb3J0LCBlbmNvZGluZz0ndXRmLTgnKQpQYXRoKG9zLmVudmlyb25bJ1NUQUdFX1JFVklFV19WRVJESUNUX0ZJTEUnXSkud3JpdGVfdGV4dCgKICAgIGpzb24uZHVtcHMoeydjcml0ZXJpYSc6IFt7J2NyaXRlcmlvbic6ICdjcml0ZXJpb24nLCAndmVyZGljdCc6ICdQQVNTJywgJ3JlYXNvbic6ICd0ZXN0IHJldmlld2VyIGluc3BlY3RlZCB0aGUgaW5wdXRzJ31dLCAnYXBwcm92ZWQnOiBUcnVlfSksIGVuY29kaW5nPSd1dGYtOCcpCnByaW50KCdBUFBST1ZFRCcp'"'"'))'
Attempt: 1/unlimited
Iteration: 1/unlimited
Execution time: 0s/unlimited
WARNING: preflights.codex is not configured; continuing without a venue health check
----------------------------------------------------------------------
Ran 95 tests in 40.590s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793425668
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793425668. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp7abjj7t7/unattended/W-00000001-1793425668
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
Ran 668 tests in 123.465s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.951s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000270.md
Criteria:
- PASS: close_work 가 리뷰 명령에 일반 검사와 다른 제한 시간을 쓰고, 그 값을 인자로 바꿀 수 있다는 것을 테스트가 확인한다
  Reason: 두 리뷰 경로는 --review-timeout(기본 3600초)을 쓰고 일반 검사와 경로 조회는 --timeout을 유지한다. 인수 테스트 62개가 일반 검사 제한보다 긴 리뷰의 성공과 --review-timeout 초과 시 닫기 실패를 확인하며, 전체 scripts 668개와 hooks 378개도 통과했다. Decisions made와 Work not done은 기본값 선택, 범위 밖 driver_lifecycle.py 및 test_drive.py 변경 이유, 드라이버의 긴 리뷰 시간 지원을 남긴 이유를 명시하므로 목적과 범위 경계 보고 계약을 충족한다.
```

## Retrospective

[R-00000270](../../retrospectives/R-00000270.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000077)뿐이므로 `not_applicable`이다.
