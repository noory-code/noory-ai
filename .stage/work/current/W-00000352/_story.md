---
id: W-00000352
title: 자식 프로세스 출력을 로캘 인코딩이 아니라 UTF-8 로 읽기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000352
promotion: not_applicable
review: passed
scope: stage/hooks/stage_work.py, stage/scripts/driver_git.py, stage/scripts/driver_lifecycle.py, stage/scripts/driver_repository.py, stage/scripts/drive_parallel.py, stage/scripts/handoff_producers.py, stage/scripts/handoff_sources.py, stage/scripts/stage_schema_v4_migration.py, stage/scripts/stage_schema_v5_migration.py, stage/skills/stage-retrospective/close_work.py, stage/skills/stage-retrospective/worktree_guard.py, stage/scripts/tests/test_subprocess_text_encoding.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000352 자식 프로세스 출력을 로캘 인코딩이 아니라 UTF-8 로 읽기

## Purpose

Windows 한국어 로캘(cp949)에서 close_work 와 드라이버가 자식 프로세스의 UTF-8 출력을 로캘 인코딩으로 읽다가 UnicodeDecodeError 로 출력을 잃는 것을 고쳐, 어느 로캘에서도 검사 출력이 카드에 남게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

Windows 를 한국어 등 UTF-8 이 아닌 로캘로 쓰는 사람이 카드를 닫아도 검사 출력이 카드의 증거에 남는다.
지금은 닫기는 종료 코드로 통과하지만 출력이 사라져, 리뷰하는 사람이 무엇이 실행됐는지 볼 수 없다.

## Scope

### Included

- `text=True` 로 자식 프로세스를 띄우는 플러그인 코드 18곳 모두에 `encoding="utf-8", errors="replace"` 를 준다:
  close_work, worktree_guard, 드라이버(`driver_git`·`driver_lifecycle`·`driver_repository`·`drive_parallel`),
  스키마 마이그레이션 둘, handoff 읽기 둘, 훅의 `stage_work.py`.
- 플러그인 코드를 AST 로 훑어, 텍스트 모드 호출이 UTF-8 과 `replace` 를 넘기지 않으면 실패하는 테스트를 둔다.
- 로캘 인코딩을 cp949 로 바꿔 둔 채 UTF-8 한국어를 내는 자식을 close_work 의 `run_check` 로 돌리는 테스트를 둔다.
  macOS 에서도 같은 상황이 되도록 `subprocess` 가 기본 인코딩을 묻는 자리를 바꿔 끼운다.

### Excluded

- 바이트로 읽고 `os.fsdecode` 나 `.decode(errors="replace")` 로 푸는 호출은 그대로 둔다. 기본 인코딩이 UTF-8 이다.
- 자식 Python 이 자기 출력을 로캘 인코딩으로 쓰는 것(`PYTHONUTF8` 을 자식 환경에 넣는 일)은 바꾸지 않는다.
  검사 명령의 동작을 바꾸기 때문이다.
- 테스트 코드 안의 `text=True` 호출은 고치지 않는다.

## Risks

- 자식이 로캘 인코딩(cp949)으로 쓴 출력은 이제 오류 대신 대체 문자로 읽힌다. 출력은 남지만 글자가 깨질 수 있다.

## Success criteria

- 로캘 인코딩이 UTF-8 이 아닐 때도 close_work 가 한국어 UTF-8 을 출력하는 검사의 출력을 잃지 않고 증거로 남긴다.
- Stage 플러그인 코드에서 text=True 로 자식 프로세스를 띄우는 모든 호출이 encoding="utf-8", errors="replace" 로 읽는다.
- 인코딩 없이 텍스트 모드로 자식 프로세스를 띄우는 호출이 새로 생기면 테스트가 실패한다.

## Next action

전체 테스트를 돌리고 회고를 쓴 뒤 닫기 리뷰를 받는다.

## Related truth

- novel-workspace 의 W-00000040 을 Windows 11 ARM64, 한국어 로캘에서 닫을 때 close_work 가
  `UnicodeDecodeError: 'cp949' codec can't decode byte 0xec` 를 냈다(`subprocess.py _readerthread`).
  닫기는 종료 코드로 통과했지만 검사 출력이 사라졌다.

## Progress

- 커밋 `d8f5c2ec`: 텍스트 모드 호출 18곳에 `encoding="utf-8", errors="replace"` 를 줬다.
- 테스트를 고치기 전 코드에 돌려 봤다. 가드는 18곳을 실패로 잡았고, close_work 테스트는 출력을 빈 문자열로 받아
  실패했다. 대조 테스트(인코딩 없는 호출은 출력을 잃는다)는 통과했다. 고친 뒤에는 넷 다 통과한다.

## Verification

이 기록은 Windows 11 ARM64, 한국어 로캘(cp949), Python 3.14 에서 `python` 으로 돌린 결과다. 이 머신의
`python3` 는 Store 바로가기라 쓰지 않았다.

- `python -m unittest stage/scripts/tests/test_subprocess_text_encoding.py -q`: 4개 통과
- `python -m unittest discover -s stage/hooks/tests -q`: 448개 통과, 44개 건너뜀.
- `python -m unittest discover -s stage/scripts/tests`: 770개 중 실패 9개, 오류 7개, 건너뜀 6개. 고치기 전
  `origin/main` 을 같은 머신에서 돌리면 761개 중 같은 16개가 실패한다. 새로 실패한 테스트는 없다. 16개는 테스트
  고정물이 `python3` 를 부르거나(exit 9009), 테스트 도우미가 자식 출력을 cp949 로 읽다가 깨지는 것이다.
- `python stage/scripts/audit_stage.py --project-root .`: errors=0.
- 닫기 리뷰는 아직 받지 않았다. 이 저장소의 리뷰 명령이 POSIX 셸 문법(`OUT=$(...)`)과 `python3` 를 써서
  Windows 의 `cmd.exe` 에서 돌지 않는다. macOS 에서 닫는다.

### Executed at close — 2026-11-18

```
$ python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py -q
[exit 0]
----------------------------------------------------------------------
Ran 4 tests in 0.368s

OK

$ python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py -q
[exit 0]
----------------------------------------------------------------------
Ran 4 tests in 0.300s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 448 tests in 7.068s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1795007874
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1795007874. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpk24f8t2w/unattended/W-00000001-1795007874
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
Ran 765 tests in 179.125s

OK (skipped=2)
```

### Review at close — 2026-11-18

```
Review report: .stage/.runtime/driver/logs/W-00000352.md
Criteria:
- PASS: 로캘 인코딩이 UTF-8 이 아닐 때도 close_work 가 한국어 UTF-8 을 출력하는 검사의 출력을 잃지 않고 증거로 남긴다.
  Reason: macOS 에서 python3 -m unittest stage/scripts/tests/test_subprocess_text_encoding.py -q 를 돌려 4개 통과를 봤고, 기본 인코딩을 cp949 로 바꿔 끼운 채 run_check 를 돌리니 고친 close_work 는 '한국어 ok �' 를 raw 와 evidence 에 남기고 encoding 을 뺀 사본은 UnicodeDecodeError 를 냈다.
- PASS: Stage 플러그인 코드에서 text=True 로 자식 프로세스를 띄우는 모든 호출이 encoding="utf-8", errors="replace" 로 읽는다.
  Reason: hooks·scripts·skills 의 테스트 밖 subprocess 호출을 grep 으로 모두 훑었다. text=True 호출 18곳이 모두 encoding="utf-8", errors="replace" 를 넘기고, 나머지는 바이트로 읽어 fsdecode·decode(errors="replace") 하거나 출력을 잡지 않으며, release_plugin.py 의 text=True 는 tempfile.mkstemp 이다. AST 가드 테스트도 통과했다.
- PASS: 인코딩 없이 텍스트 모드로 자식 프로세스를 띄우는 호출이 새로 생기면 테스트가 실패한다.
  Reason: close_work.py 원문에서 encoding·errors 두 줄을 지운 소스를 text_mode_calls 에 넣으니 close_work.py:682 를 위반으로 잡았고, 가드 자체 테스트가 text=True·universal_newlines·별칭 import·cp949 지정 호출을 잡고 tempfile.mkstemp(text=True) 는 넘기는 것을 통과로 확인했다. 전체 scripts 765개, hooks 448개 테스트도 macOS 에서 통과했다.
```

- 위 닫기 검사와 리뷰는 macOS 에서 코드 커밋 `d8f5c2ec` 에 맞춘 분리 worktree 에서 돌렸다.
- 닫기 리뷰는 같은 모델 계열의 리뷰다. codex 가 없어 Claude 대역
  (`STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py`)으로 돌렸고, 다른 모델의 교차 리뷰가 아니다.
- macOS 에서는 전체 테스트가 통과해, Windows 에서 원래 실패하던 16개는 다시 보지 못했다.
- 사용자 확인 — 2026-11-18. 사용자는 바뀐 경로와 요약, 기준 세 개의 PASS 판정, 리뷰어가 cp949 를 바꿔 끼워 직접
  실행한 결과, macOS 에서 다시 보지 못한 Windows 16개를 보고 "확인, 닫으세요" 라고 답했다(DE-00000087).

## Retrospective

R-00000352 에 적었다.

## Promotion decision

not_applicable. 공식 기록으로 올릴 결정이 없다.
