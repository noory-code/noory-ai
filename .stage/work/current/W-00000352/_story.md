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
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
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


## Verification


## Retrospective


## Promotion decision
