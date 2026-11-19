---
id: W-00000356
title: evonest 가 Windows 한국어 로캘에서도 동작하고 테스트가 통과하게 고치기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "cd evonest && uv run pytest -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000356
promotion: not_applicable
review: passed
scope: evonest/src/evonest/cli.py,evonest/src/evonest/core/doc_updater.py,evonest/src/evonest/core/phases.py,evonest/src/evonest/core/orchestrator.py,evonest/src/evonest/core/process_manager.py,evonest/src/evonest/core/claude_runner.py,evonest/tests,evonest/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000356 evonest 가 Windows 한국어 로캘에서도 동작하고 테스트가 통과하게 고치기

## Purpose

Windows 한국어 로캘(cp949)에서 evonest 가 파일과 자식 프로세스 출력을 로캘 인코딩으로 읽고 쓰다가 실패하고, 경로를 역슬래시로 돌려주는 것을 고쳐, 어느 로캘과 OS 에서도 같은 결과를 내게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

Windows 를 한국어처럼 UTF-8 이 아닌 로캘로 쓰는 사람도 evonest 를 쓸 수 있다. 지금은 `claude` 나
`git` 이 한글이나 기호를 출력하면 엔진이 그 출력을 읽다가 멈추거나 깨진 글자를 받는다.
`evonest init` 은 출력을 파이프로 연결하면 바로 죽는다. 이 저장소를 Windows 에서 고치는 사람은
테스트 438개 가운데 239개가 실패해서 자기 변경이 맞는지 확인할 수 없다.

## Scope

### Included

- `phases.py`, `orchestrator.py`, `process_manager.py` 의 텍스트 모드 `subprocess` 호출 12개에
  `encoding="utf-8", errors="replace"` 를 준다.
- 새 텍스트 모드 호출이 인코딩을 빠뜨리면 실패하는 테스트를 더한다.
- `cli.py` 가 스트림이 인코딩할 수 없는 글자를 만나면 죽지 않고 그 글자를 바꿔 출력하게 한다.
- `doc_updater.py` 가 상대 경로를 어느 OS 에서나 슬래시로 돌려주게 한다.
- 테스트가 파일을 UTF-8 로 읽고 쓰게 하고, 파일 이름을 `/` 로 자르지 않고 `Path.name` 으로 얻게 한다.
- `evonest/CHANGELOG.md` 의 `## Unreleased` 에 기록한다.

### Excluded

- evonest 릴리스. 버전은 이 카드에서 올리지 않는다.
- `tools/evolve.py:77` 과 `tools/analyze.py:58` 의 mypy 오류 두 개. Windows 에서는
  `# type: ignore` 가 필요 없다고 나오는 오류이고, 이 카드를 시작하기 전에도 같았다.
- 포매터가 고치려 하는 기존 파일 7개. 이 카드가 바꾼 줄과 상관없는 서식 차이다.
- `claude_runner.py`. 범위에 넣었지만 텍스트 모드 호출이 없어서 고치지 않았다.
- rag. 이 기기(ARM64 Windows)에는 `kuzu` 가 설치되지 않아 테스트를 실행하지 못했다.

## Risks

- `cli.py` 는 스트림의 인코딩을 바꾸지 않고 오류 처리만 `replace` 로 바꾼다. cp949 파이프에서는
  em dash 가 `?` 로 나온다. 죽는 것보다는 낫지만 글자가 그대로 나오지는 않는다.
- 자식 프로세스가 UTF-8 이 아닌 인코딩으로 출력하면 `errors="replace"` 때문에 오류 없이 깨진
  글자가 들어온다. `claude`, `codex`, `git`, `gh` 는 UTF-8 로 출력한다고 보고 정했다.
- 실제 `claude -p` 를 부르는 실행은 이 카드에서 해 보지 않았다. 테스트는 그 호출을 가짜로 바꾼다.

## Success criteria

- 한국어 Windows(cp949)에서 uv run pytest 가 실패와 오류 없이 통과한다
- 출력이 파이프로 연결된 cp949 환경에서 evonest init 이 UnicodeEncodeError 없이 끝난다
- 문서 동기화 대상의 상대 경로가 Windows 에서도 슬래시로 나온다

## Next action

macOS 에서 닫는다. 닫기 리뷰 명령은 POSIX 셸 문법이라 Windows 의 `cmd.exe` 에서 실행되지 않는다
(W-00000352 와 같다). 코드 커밋 `20dd7ccd` 에 맞춘 분리 worktree 에서
`STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 를 앞에 두고 `close_work.py` 를
실행한다. 회고 R-00000356 은 이미 썼다.

## Related truth

- `.stage/operations/verification.md` 의 "Windows 동작 확인": Windows 동작을 고치는 카드는 영어가
  아닌 로캘의 실제 Windows 에서 테스트를 한 번 실행하고 기기·로캘·명령·결과를 남긴다.
- R-00000354: 같은 인코딩 실수가 stage 에서 두 번 나왔다.
- 사용자 결정(2026-11-20): evonest 의 Windows 실패를 고치는 카드를 등록하고 고치라고 했다.

## Progress

- 2026-11-20: 고치기 전 상태를 쟀다. cp949 에서 438개 가운데 199개가 통과하고 232개가 오류, 7개가
  실패였다. 오류 232개는 모두 `tests/conftest.py:20` 이 템플릿을 로캘 인코딩으로 읽는 데서 났다.
- `evonest init` 을 파이프에 연결해 실행하니 `cli.py` 의 `input(prompt)` 에서
  `UnicodeEncodeError: 'cp949' codec can't encode character '—'` 로 죽었다.
- 감독 모드의 팀원을 띄우지 않고 이 세션이 직접 고쳤다. Windows 에는 tmux 가 없다.
- 포매터(`ruff format src/ tests/`)를 전체에 실행하니 이 카드와 상관없는 파일까지 바뀌어서
  되돌렸다. 이 카드가 바꾼 줄만 남겼고, 길어진 세 줄은 손으로 나눴다.

## Verification

기기: Windows 11 (10.0.28000) ARM64. 로캘: 콘솔 코드 페이지 949, `locale.getpreferredencoding()` 은
`cp949`. Python 3.14.10 (시스템 설치본).

`uv` 가 내려받은 Python 3.11 은 이 세션에서 쓰지 못했다. `uv run` 이 "Missing expected target
directory for Python minor version link" 로 멈춘다. 그래서 모든 명령 앞에
`UV_PYTHON=3.14 UV_PYTHON_PREFERENCE=only-system` 을 두고 `evonest/` 안에서 실행했다. evonest 가
고정한 3.11 로는 확인하지 않았다.

| 명령 | 고치기 전 | 고친 뒤 |
|---|---|---|
| `uv run pytest -q` | 7 failed, 199 passed, 232 errors | 440 passed |
| `uv run ruff check src/ tests/` | 실행하지 않았다 | All checks passed |
| `uv run mypy src/evonest/` | 오류 2개 | 같은 오류 2개 (Excluded 참고) |
| `python -m evonest init <빈 폴더> < /dev/null \| tail` | `UnicodeEncodeError` 로 종료 | 종료 코드 0 |

- 새 테스트 `tests/test_subprocess_text_encoding.py` 는 고치기 전 소스에서 실패하고(1 failed,
  1 passed) 고친 뒤 통과한다.
- 리뷰는 아직 받지 않았다. 닫을 때 받는 리뷰는 codex 가 아니라 같은 모델(Claude 대역)의 리뷰다.
- 2026-11-20 맥북(macOS, 코드 커밋 `20dd7ccd` 에 맞춘 분리 worktree)에서 다시 실행했다. `uv run pytest -q` 는 440개 통과,
  `uv run ruff check src/ tests/` 는 통과, `uv run mypy src/evonest/` 는 오류 없음이다. Windows 에서 나온 mypy 오류 두 개는
  맥에서는 나오지 않는다. 맥에서는 `uv` 가 고른 Python 으로 실행했다.
- 닫기 리뷰는 맥북에서 Claude 대역(`claude_review_companion.py`)으로 받았다. 같은 모델의 리뷰다(DE-00000086).
- 고친 경로는 evonest 뿐이고 관문 경로가 아니라서 DE-00000087 의 사용자 확인 대상이 아니다. 사용자가 2026-11-20 에
  "PR #70도 맥북에서 닫아주세요" 라고 했다.

### Executed at close — 2026-11-20

```
$ cd evonest && uv run pytest -q
[exit 0]
........................................................................ [ 16%]
........................................................................ [ 32%]
........................................................................ [ 49%]
........................................................................ [ 65%]
........................................................................ [ 81%]
........................................................................ [ 98%]
........                                                                 [100%]
440 passed in 65.56s (0:01:05)

$ cd evonest && uv run ruff check src/ tests/
[exit 0]
All checks passed!

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
Review report: .stage/.runtime/driver/logs/W-00000356.md
Criteria:
- PASS: 한국어 Windows(cp949)에서 uv run pytest 가 실패와 오류 없이 통과한다
  Reason: 카드 Verification 에 Windows 11 ARM64, cp949 로캘에서 uv run pytest -q 가 440 passed 로 기록돼 있다(Python 3.14 사용을 밝혀 둠). 내가 macOS 에서 LC_ALL=ko_KR.CP949 PYTHONUTF8=0 uv run pytest -q 를 실행하니 440 passed 였고, 같은 조건에서 고치기 전 커밋 98e04cb7 은 3 failed, 232 errors(UnicodeDecodeError)로 깨져 이 검사가 고침을 구별함을 확인했다. 실제 Windows 에서는 내가 실행하지 않았다.
- PASS: 출력이 파이프로 연결된 cp949 환경에서 evonest init 이 UnicodeEncodeError 없이 끝난다
  Reason: 카드에 Windows cp949 에서 파이프로 연결한 evonest init 이 종료 코드 0 으로 기록돼 있다. 내가 macOS 에서 LC_ALL=ko_KR.CP949 PYTHONUTF8=0 uv run python -m evonest init <빈 폴더> < /dev/null | tail 을 실행하니 종료 코드 0 이었고 em dash 는 ? 로 나왔다(카드 Risks 에 적힌 대로). 같은 명령을 고치기 전 커밋에서 실행하니 UnicodeEncodeError 로 종료 코드 1 이었다.
- PASS: 문서 동기화 대상의 상대 경로가 Windows 에서도 슬래시로 나온다
  Reason: doc_updater._collect_targets 가 str(relative_to) 대신 relative_to(project).as_posix() 로 키를 만들어 OS 와 상관없이 슬래시를 쓴다. 이를 단언하는 test_update_docs 의 skills/mypkg/SKILL.md 같은 키 검사가 카드에 기록된 Windows 실행(440 passed)에 포함된다. 내가 Windows 에서 직접 실행하지는 않았고 macOS 에서는 uv run pytest -q 로 통과를 확인했다.
```

## Retrospective


## Promotion decision

