---
id: W-00000357
title: evonest 의 mypy 검사가 Windows 에서도 통과하게 고치기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "cd evonest && uv run mypy src/evonest/"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000357
promotion: pending
review: pending
scope: evonest/src/evonest/tools/analyze.py,evonest/src/evonest/tools/evolve.py,evonest/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000357 evonest 의 mypy 검사가 Windows 에서도 통과하게 고치기

## Purpose

Windows 에서 uv run mypy src/evonest/ 가 필요 없는 type: ignore 주석 2개 때문에 실패하는 것을 고쳐, Windows 에서 일하는 사람도 타입 검사를 통과 기준으로 쓸 수 있게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

evonest 를 Windows 에서 고치는 사람이 타입 검사 결과를 믿을 수 있다. 지금은 자기가 바꾸지 않은 줄에서
오류 2개가 항상 나와서, 새로 생긴 오류를 그 사이에서 골라내야 한다.

## Scope

### Included

- `tools/analyze.py` 와 `tools/evolve.py` 의 `subprocess.CREATE_NEW_PROCESS_GROUP` 줄에서
  `# type: ignore[attr-defined]` 를 지운다.
- `evonest/CHANGELOG.md` 의 `## Unreleased` 에 기록한다.

### Excluded

- evonest 릴리스.
- evonest 에 CI 를 더하는 일. `.github/workflows/` 에 evonest 워크플로가 없다.

## Risks

- 다른 플랫폼에서 mypy 가 실패할 수 있다고 봤으나, `--platform linux` 와 `--platform darwin` 으로
  실행해 통과를 확인했다. 실제 Linux 나 macOS 기기에서는 실행하지 않았다.

## Success criteria

- Windows 에서 uv run mypy src/evonest/ 가 오류 없이 끝난다
- uv run mypy --platform linux src/evonest/ 와 --platform darwin 도 오류 없이 끝난다

## Next action

macOS 에서 닫는다. 닫기 리뷰 명령은 POSIX 셸 문법이라 Windows 의 `cmd.exe` 에서 실행되지 않는다.
W-00000356 과 같은 브랜치(`claude/evonest-windows-locale`)에 있으므로 함께 닫는다.

## Related truth

- W-00000356 이 이 오류 2개를 범위에서 빼고 다음 변경으로 남겼다(R-00000356).
- 사용자 결정(2026-11-20): 이 오류부터 고치라고 했다.

## Progress

- 2026-11-20: 주석 2개를 지웠다. 두 호출은 `if sys.platform == "win32":` 안에 있다. mypy 는 다른
  플랫폼에서 이 분기를 검사하지 않으므로 주석이 처음부터 필요 없었다.
- 감독 모드의 팀원을 띄우지 않고 이 세션이 직접 고쳤다. Windows 에는 tmux 가 없다.

## Verification

기기: Windows 11 (10.0.28000) ARM64, 로캘 cp949, 시스템 Python 3.14.10. `evonest/` 안에서
`UV_PYTHON=3.14 UV_PYTHON_PREFERENCE=only-system` 을 앞에 두고 실행했다. 고정된 Python 3.11 로는
확인하지 않았다. mypy 설정의 `python_version` 은 3.11 이다.

| 명령 | 고치기 전 | 고친 뒤 |
|---|---|---|
| `uv run mypy src/evonest/` | 오류 2개 (`unused-ignore`) | Success: no issues found in 44 source files |
| `uv run mypy --platform linux src/evonest/` | Success | Success |
| `uv run mypy --platform darwin src/evonest/` | Success | Success |
| `uv run ruff check src/ tests/` | 통과 | 통과 |
| `uv run pytest -q` | 440 passed | 440 passed |

- 리뷰는 아직 받지 않았다. 닫을 때 받는 리뷰는 codex 가 아니라 같은 모델(Claude 대역)의 리뷰다.

## Retrospective


## Promotion decision

