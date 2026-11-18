---
id: W-00000354
title: Stage 테스트가 자식 프로세스 출력을 UTF-8로 읽게 고치기
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000354
promotion: not_applicable
review: not_required
scope: stage/hooks/tests,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000354 Stage 테스트가 자식 프로세스 출력을 UTF-8로 읽게 고치기

## Purpose

한국어 Windows에서 Stage 테스트가 자식 프로세스 출력을 cp949로 잘못 읽어 깨지지 않게 한다

## Actions

액션으로 나누지 않는다. 같은 고침을 파일마다 반복하는 한 단위 작업이다.

## User value

한국어 Windows에서 테스트가 실패하면 그것이 진짜 결함인지 판단할 수 있게 된다. 지금은 테스트가
자식 프로세스 출력을 로캘 인코딩(cp949)으로 읽다가 `UnicodeDecodeError`를 내고, 출력이 `None`이
되어 `TypeError`가 뒤따른다. 실제 결과가 이 오류에 가려진다. 영어 로캘인 CI는 cp1252로 읽어서
오류 없이 글자만 깨진 채 통과하므로 이 문제를 잡지 못했다.

## Scope

### Included

- `stage/hooks/tests`, `stage/scripts/tests`: `encoding` 없이 `text=True`로 읽는 subprocess 호출
  56군데(파일 31개)에 `encoding="utf-8", errors="replace"`를 붙인다.
- `stage/scripts/tests/test_subprocess_text_encoding.py`: 지금은 `tests` 폴더를 빼고 소스만
  검사한다(W-00000352). 테스트 파일도 검사하게 넓힌다.
- `stage/CHANGELOG.md`: `## Unreleased`에 한 줄을 더한다.

### Excluded

- 이 기기의 `python3`가 Microsoft Store 바로가기라 실행되지 않는 문제. 기기 설정과 "훅은
  `python3`로 실행한다"는 저장소 규칙이 함께 걸려 있어 따로 결정한다. 이 문제로 실패하는
  `test_close_work` 여덟 개는 이 카드를 마쳐도 이 기기에서 남는다.
- 훅·스크립트 본체. W-00000352에서 이미 UTF-8로 읽게 고쳤다.

## Risks

- `errors="replace"`는 깨진 바이트를 대체 문자로 바꾼다. 테스트가 출력의 특정 바이트를 검사하면
  결과가 달라질 수 있다. 소스 쪽 계약이 같은 조합을 요구하므로 그대로 맞춘다.
- 원인을 모르는 `test_codex_companion` 한 개와 `test_drive_parallel` 한 개는 고친 뒤 다시 본다.
  이 카드로 풀리지 않으면 관측으로 남긴다.

## Success criteria

- 한국어 Windows에서 stage hooks와 scripts 테스트를 실행할 때 UnicodeDecodeError가 한 번도 나오지 않는다
- 인코딩 때문에 실패하던 test_archive_work 다섯 개와 test_schema_v4_lifecycle 한 개가 통과한다
- 테스트 파일에 UTF-8을 지정하지 않은 text=True subprocess 호출을 새로 넣으면 test_subprocess_text_encoding이 실패한다

## Next action

테스트 쪽 호출에 UTF-8 읽기를 지정하고, 인코딩 검사를 테스트 파일까지 넓힌다.

## Related truth


## Progress

- 테스트 쪽 subprocess 호출 56군데 가운데 55군데에 `encoding="utf-8", errors="replace"`를 붙였다.
  `encoding="utf-8"`만 있던 세 군데에는 `errors="replace"`를 더했다. 나머지 한 군데는
  `test_subprocess_text_encoding.py`의 대조군이다. 로캘로 읽어야 깨짐을 보여 줄 수 있어서
  `# decodes with the locale on purpose` 주석을 달고 그대로 두었다.
- `test_subprocess_text_encoding.py`가 `tests` 폴더도 읽게 했다. 위 주석을 단 호출만 건너뛴다.
- 범위 밖으로 둔 실패 두 개(`test_codex_companion`, `test_drive_parallel`)의 원인도 다시 봤다.
  `test_drive_parallel`은 실행자 명령 `python3 -B executor.py`가 `[exit 9009]`로 끝났다.
  `test_codex_companion`의 reaper 테스트는 가짜 companion을 `spawnSync('python3', …)`로 띄운다.
  둘 다 `python3` 문제 쪽이라 이 카드에서 고치지 않는다. reaper 쪽은 메시지로 직접 확인하지는
  않았다.

## Verification

이 기기: Windows 11, 한국어 로캘(cp949), Python 3.14.10. 고치기 전과 후를 같은 명령으로 비교했다.

| 명령 | 고치기 전 | 고친 뒤 |
|---|---|---|
| `python -m unittest discover -s stage/hooks/tests -q` | 448개 통과, 44개 건너뜀, `UnicodeDecodeError` 1번 | 448개 통과, 44개 건너뜀, `UnicodeDecodeError` 0번 |
| `python -m unittest discover -s stage/scripts/tests -v` | 770개 중 실패 9개, 오류 7개, 건너뜀 6개 | 770개 중 실패 9개, 오류 1개, 건너뜀 6개, `UnicodeDecodeError` 0번 |
| `python -m unittest stage/scripts/tests/test_subprocess_text_encoding.py` | 테스트 파일을 읽지 않았다 | 4개 통과 |

- 성공 기준 1: 두 스위트 출력 모두에서 `UnicodeDecodeError`가 0번이다.
- 성공 기준 2: 오류 7개 가운데 인코딩 때문이던 여섯 개(`test_archive_work` 다섯 개,
  `test_schema_v4_lifecycle` 한 개)가 통과한다.
- 성공 기준 3: `stage/hooks/tests/test_model_tiers.py`에 `subprocess.run(["x"], capture_output=True,
  text=True)`를 잠시 넣자 검사가 `hooks/tests/test_model_tiers.py:404`를 짚으며 실패했다. 그 줄을
  빼자 다시 통과했다.
- 남은 실패 아홉 개와 오류 한 개는 모두 이 기기의 `python3`가 Microsoft Store 바로가기(0바이트,
  실행하면 종료 코드 9009)라서 생긴다. 범위 밖으로 둔 문제다.
- 카드에 저장한 확인 명령은 `python3`로 시작한다. 이 기기에서는 `python3`가 실행되지 않아
  같은 테스트를 `python`으로 실행했다.


### Executed at close — 2026-11-18

```
$ python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py
[exit 0]
....
----------------------------------------------------------------------
Ran 4 tests in 1.314s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 448 tests in 15.263s

OK (skipped=44)

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794992443
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794992443. Human review + merge required; the base branch was not modified.
Removed unattended worktree: C:\Users\wooxi\AppData\Local\Temp\tmpp0ioq0im\unattended\W-00000001-1794992443
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
Ran 770 tests in 617.956s

OK (skipped=5)
```

## Retrospective

R-00000354에 적었다.

## Promotion decision

not_applicable. 공식 기록으로 올릴 결정이 없다.
