---
id: W-00000358
title: 훅 명령이 Windows에서는 python을 부르게 고친다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000358
promotion: not_applicable
review: passed
scope: stage/hooks/hooks.json,stage/hooks/tests/test_hooks_json_interpreter.py,stage/hooks/README.md,stage/CHANGELOG.md,evonest/hooks/hooks.json,evonest/tests/test_hooks_json.py,evonest/CHANGELOG.md,CLAUDE.md
promotes:
decision_refs:
---

# W-00000358 훅 명령이 Windows에서는 python을 부르게 고친다

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

Windows 세션이 한국어 Windows 에서 이 브랜치의 훅을 실행해 보고 결과를 `## Verification` 에 남겼다.
맥북 세션이 닫기 리뷰를 받고, 관문 경로를 고친 카드이므로 사용자 확인을 받아 닫는다(DE-00000087).


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
- Codex 에서는 실행해 보지 않았다.

### 한국어 Windows (성공 기준 3번)

기기: Windows 11 Home (10.0.28000) ARM64. 로캘: 콘솔 코드 페이지 949, `cp949`. Python 3.14.10
(`C:\Python314\python`). Claude Code 2.1.326. 브랜치 `claude/hook-python-on-windows` 의 `ce652431` 을
따로 체크아웃한 작업 트리에서 실행했다.

이 기기에는 `python3` 가 두 군데 있다. 사용자가 만든 shim 폴더와 `WindowsApps` 의 앱 실행 별칭이다.
두 폴더를 `PATH` 에서 뺀 채로 실행해서 `python3` 가 없는 기기를 흉내 냈다. `command -v python3` 가
아무것도 찾지 못하는 것을 실행마다 확인했다. `python3` 를 설치한 적이 없는 기기에서 실행한 것은 아니다.

| 명령 | 결과 |
|---|---|
| 고친 `PreToolUse` 명령을 Git 의 `sh -c` 로 실행하고, 인라인 코드가 `.stage` 를 말하는 Bash 입력을 넣었다 | 훅이 `permissionDecision: "deny"` 를 돌려줬다(종료 코드 0). |
| 같은 입력을 고치기 전 명령(`python3 "${CLAUDE_PLUGIN_ROOT}/hooks/stage_guard.py" pre-tool-use`)에 넣었다 | `sh: line 1: python3: command not found`, 종료 코드 127. |
| `claude -p … --plugin-dir <작업 트리>/stage --allowedTools Bash --model sonnet` 로 새 세션을 띄워 같은 종류의 Bash 명령을 실행시켰다 | `PreToolUse` 훅이 거절했고, 세션 시작 글에 `## Stage context` 절과 `W-00000358 … [active]` 줄이 있었다. |
| `python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q` | 2개가 통과했다. |
| `uv run python -m pytest tests/test_hooks_json.py -q` (evonest) | 1개가 통과했다. |

- 새 세션의 디버그 로그에서 확인한 것: `--plugin-dir` 의 Stage 가 설치된 0.66.6 을 대신했다.
  `SessionStart`, `PreToolUse`, `Stop` 훅이 모두 `case "$OS" in Windows_NT) p=python;; …` 명령으로 실행됐고
  `success` 로 기록됐다. `command not found` 는 로그에 없었다.
- Claude Code 는 이 기기에서 훅 명령을 POSIX 셸로 실행했다. `case` 문이 그대로 실행된 것으로 안다.
  Git Bash 가 없는 Windows 에서는 실행해 보지 않았다.
- 마지막 두 줄의 테스트는 `python3` 를 `PATH` 에 둔 채로 실행했다. 테스트 명령이 `python3` 를 부른다.
- evonest 훅(`post-improve.py`)은 실제 세션에서 실행해 보지 않았다. 명령 형태를 확인하는 테스트만 실행했다.

### 닫기

- 사용자 확인 — 2026-11-20. 훅은 관문 경로라서 닫기 전에 사용자 확인이 필요하다(DE-00000087). 위 Windows 결과와
  확인하지 않은 것 세 가지를 보여 준 뒤 사용자가 "확인, 닫고 머지" 라고 했다.
- 닫기 리뷰는 맥북에서 Claude 대역(`claude_review_companion.py`)으로 받는다. 같은 모델의 리뷰다(DE-00000086).


### Executed at close — 2026-11-20

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q
[exit 0]
----------------------------------------------------------------------
Ran 2 tests in 0.657s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 450 tests in 5.929s

OK

$ cd evonest && uv run pytest -q
[exit 0]
........................................................................ [ 16%]
........................................................................ [ 32%]
........................................................................ [ 49%]
........................................................................ [ 65%]
........................................................................ [ 82%]
........................................................................ [ 98%]
.......                                                                  [100%]
439 passed in 56.36s
Using CPython 3.11.14
Creating virtual environment at: .venv
   Building evonest @ file:///private/tmp/claude-501/-Users-woogis-Workspace-repo-noory-ai/0c2e6057-da69-4e2d-a103-0bee0b8e3685/scratchpad/close358/evonest
      Built evonest @ file:///private/tmp/claude-501/-Users-woogis-Workspace-repo-noory-ai/0c2e6057-da69-4e2d-a103-0bee0b8e3685/scratchpad/close358/evonest
Installed 49 packages in 39ms

$ python3 stage/scripts/audit_stage.py
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

### Review at close — 2026-11-20

```
Review report: .stage/.runtime/driver/logs/W-00000358.md
Criteria:
- PASS: 맥에서 훅 테스트와 감사가 통과하고, 고친 명령으로 실제 세션의 Stage 관문이 전과 같이 동작한다
  Reason: I ran `python3 -m unittest discover -s stage/hooks/tests -q` (450 tests OK), `uv run python -m pytest tests/test_hooks_json.py -q` in evonest (1 passed), and `python3 stage/scripts/audit_stage.py` (errors=0, warnings=32, same as recorded); I also ran the fixed PreToolUse command via `sh -c` with a Bash input whose inline python code reads `.stage/settings.json` and it returned permissionDecision deny; I did not start a new `claude -p` session myself, and the card's Verification records that run showing the PreToolUse deny and the Stage context section.
- PASS: 훅 명령 6줄이 모두 같은 형태인지 테스트가 확인하고, 한 줄을 python3 로 되돌리면 그 테스트가 실패한다
  Reason: Both tests read every command hook from hooks.json and assert the exact selector prefix (5 Stage lines, 1 evonest line); I ran the acceptance command `python3 -m unittest discover -s stage/hooks/tests -p test_hooks_json_interpreter.py -q` (2 tests OK), then in a scratch copy reverted the Stage `stop` line and the evonest line to `python3`, and the Stage test failed (failures=2) and `uv run python -m pytest` on the copied evonest test failed (1 failed).
- PASS: python3 가 없는 한국어 Windows에서 Stage 훅이 실행되어 관문이 동작하고, 그 결과가 이 카드의 Verification 에 남는다
  Reason: I did not run it (no Windows device here); the card's Verification records device Windows 11 ARM64, code page 949/cp949, Python 3.14.10, commit ce652431, with both python3 locations removed from PATH and `command -v python3` empty, showing the fixed PreToolUse command returning deny while the old command failed with `python3: command not found` (exit 127), and a new `claude -p --plugin-dir` session whose PreToolUse hook denied and whose debug log shows SessionStart/PreToolUse/Stop succeeding with the selector command; it honestly states python3 was hidden from PATH rather than never installed, which satisfies the verification.md Windows rule of a real non-English Windows run.
```

## Retrospective


## Promotion decision
