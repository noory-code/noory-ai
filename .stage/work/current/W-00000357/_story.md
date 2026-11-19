---
id: W-00000357
title: 훅 명령이 Windows에서는 python을 부르게 고친다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/hooks.json,stage/hooks/tests/test_hooks_json_interpreter.py,stage/hooks/README.md,stage/CHANGELOG.md,evonest/hooks/hooks.json,evonest/tests/test_hooks_json.py,evonest/CHANGELOG.md,CLAUDE.md
promotes:
decision_refs:
---

# W-00000357 훅 명령이 Windows에서는 python을 부르게 고친다

## Purpose

python3 명령이 없는 Windows에서도 Stage와 evonest 훅이 실행된다

## Actions

액션으로 나누지 않고 이 스토리에서 바로 고친다. 훅 명령 여섯 줄과 그 설명 문서를 함께 바꾸는 한 덩어리 일이다.


## User value

python.org 에서 Python 을 설치한 Windows 사용자는 `python3` 명령이 없다. Claude Code 는 시작하지 못한 훅을
"막지 않는 오류"로 처리해 도구 호출을 그대로 진행한다. 그래서 그 기기에서는 Stage 관문이 아무것도 막지 않는다.
이 일이 끝나면 그 기기에서도 훅이 실행되어 관문이 동작한다.


## Scope

### Included

- Stage 훅 명령 다섯 줄과 evonest 훅 명령 한 줄이 Windows 에서는 `python`, 그 밖에서는 `python3` 를 부른다.
- 훅 명령이 이 형태를 벗어나면 테스트가 실패한다.
- 루트 `CLAUDE.md` 의 훅 명령 규칙과 `stage/hooks/README.md` 의 설명이 고친 명령과 같은 내용을 말한다.
- 두 플러그인의 변경 기록에 이 고침이 실린다.


### Excluded

- 훅 본문(`stage_guard.py`, `post-improve.py`)은 고치지 않는다.
- 문서와 스킬에 적힌 `python3 stage/scripts/...` 명령 예시는 그대로 둔다. 모델과 사람이 읽고 실행하는 명령이라
  기기에 맞는 이름으로 부를 수 있다.
- 테스트 고정물이 `python3` 를 직접 부르는 자리는 이 카드에서 고치지 않는다.
- 훅이 실패하면 도구 호출을 막는 설정(`onFailure: "block"`)은 넣지 않는다. 사용자가 설계안 1번만 골랐다.
- 릴리스는 이 카드가 닫힌 뒤 따로 한다.


## Risks

- Git Bash 없이 PowerShell 이 훅을 실행하는 Windows 에서는 이 셸 문장이 실패한다. 그 기기에서는 고치기 전에도
  훅이 실행되지 않았으므로 더 나빠지지는 않는다.
- Codex 가 Windows 에서 훅 명령을 어느 셸로 실행하는지 확인하지 못했다. Codex 구독이 끊겨 실행해 볼 수 없다.
- Codex 가 이미 신뢰한 훅을 명령이 바뀐 뒤에도 신뢰하는지 확인하지 못했다. 다시 신뢰해야 할 수 있다.
- python.org 설치본에서 `python` 이 PATH 에 잡히는지는 설치할 때 고른 옵션에 달려 있다.


## Success criteria

- 맥에서 훅 테스트와 감사가 통과하고, 고친 명령으로 실제 세션의 Stage 관문이 전과 같이 동작한다
- 훅 명령 6줄이 모두 같은 형태인지 테스트가 확인하고, 한 줄을 python3 로 되돌리면 그 테스트가 실패한다
- python3 가 없는 한국어 Windows에서 Stage 훅이 실행되어 관문이 동작하고, 그 결과가 이 카드의 Verification 에 남는다

## Next action

Windows 세션이 `python3` 가 없는 한국어 Windows 에서 이 브랜치의 훅을 실행해 보고 결과를 `## Verification` 에
남긴다. 그 뒤 맥북 세션이 닫기 리뷰를 받고, 관문 경로를 고친 카드이므로 사용자 확인을 받아 닫는다(DE-00000087).


## Related truth

- 훅 실행 규칙: 루트 `CLAUDE.md` 의 `Cross-Platform Compatibility`.
- 훅 구성과 호환성 설명: `stage/hooks/README.md`.
- 이 문제를 처음 적은 회고: R-00000354 의 `## Next changes`.
- Windows 동작을 고치는 카드의 확인 기준: `.stage/operations/verification.md` 의 `## Windows 동작 확인`.


## Progress

- 훅 명령 여섯 줄 앞에 `case "$OS" in Windows_NT) p=python;; *) p=python3;; esac; "$p" ` 를 붙였다. Windows 는
  `OS=Windows_NT` 환경 변수로 구분한다. 프로세스를 더 띄우지 않는다.
- evonest 훅 명령은 플러그인 경로에 따옴표가 없었다. 함께 따옴표로 감쌌다.
- 테스트 두 개를 먼저 쓰고 실패를 본 뒤 고쳤다. Stage 쪽은 명령 형태와, `sh` 로 실행했을 때 실제로 불리는
  이름을 확인한다. evonest 쪽은 명령 형태를 확인한다.
- `CLAUDE.md` 의 규칙 문장, `stage/hooks/README.md` 의 호환성 설명, 두 변경 기록을 고쳤다.


## Verification

맥북(macOS, Python 3.15.2)에서 확인한 것이다. 성공 기준 1번과 2번에 해당한다.

| 명령 | 고치기 전 | 고친 뒤 |
|---|---|---|
| `python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q` | 2개 중 실패 10건(하위 검사 기준) | 2개 통과 |
| `uv run python -m pytest tests/test_hooks_json.py -q` (evonest) | 1개 실패 | 1개 통과 |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 실행하지 않았다 | 450개 통과 |
| `uv run python -m pytest -q` (evonest) | 실행하지 않았다 | 439개 통과 |
| `python3 stage/scripts/audit_stage.py` | errors=0, warnings=32 | errors=0, warnings=32 |

- 고친 `PreToolUse` 명령을 `sh -c` 로 실행하고 인라인 코드가 `.stage` 를 말하는 Bash 입력을 넣었다. 훅이
  `permissionDecision: "deny"` 를 돌려줬다.
- 새 Claude Code 세션(`claude -p`, 플러그인은 이 저장소 폴더에서 읽힘)에서 같은 종류의 명령을 실행시켰다.
  `PreToolUse` 훅이 거절했고, 세션 시작 글에 `Stage context` 절이 있었다.
- 성공 기준 3번(한국어 Windows)은 아직 확인하지 않았다.
- Codex 에서는 실행해 보지 않았다.


## Retrospective


## Promotion decision
