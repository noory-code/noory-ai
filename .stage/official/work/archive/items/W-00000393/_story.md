---
id: W-00000393
title: release_plugin.py 가 Windows 에서도 UTF-8 로 출력하게 한다
kind: fix
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000393
promotion: not_applicable
review: passed
scope: stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000393 release_plugin.py 가 Windows 에서도 UTF-8 로 출력하게 한다

## Purpose

Windows 에서 --check-released 가 버전 제목의 줄표를 깨뜨리지 않고 출력한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 표준 출력이 cp1252 일 때 --check-released 가 버전 제목을 그대로 출력하는 시험이 있고, 고치기 전에는 실패하고 지금은 통과한다
- PR 의 windows-latest 잡이 통과한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-22

```
What changed: release_plugin.main() reconfigures sys.stdout and sys.stderr to UTF-8 before parsing arguments; test_release_plugin.py gains test_check_released_prints_utf_8_when_the_console_is_cp1252, which runs --check-released with PYTHONIOENCODING=cp1252 and requires the heading with its em dash and no replacement character, and run_mode accepts a stdout encoding; stage/CHANGELOG.md has an Unreleased entry.
Why: PR #102's windows-latest jobs failed test_check_released_fails_and_lists_a_line_added_to_a_released_section on the em dash; the new test failed before the fix on Linux too and passes after it.
Decisions made: Reconfigure both streams for both modes (release and check) because both print headings or paths a non-UTF-8 console can break; reproduce with PYTHONIOENCODING rather than a Windows-only test so every OS's CI catches the class of bug.
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 성공 기준 1: `test_check_released_prints_utf_8_when_the_console_is_cp1252` 가 고치기 전(리눅스, cp1252 출력)에 실패했고 지금 통과한다.
  `PYTHONIOENCODING=cp1252` 로 `test_release_plugin.py` 전체를 돌려도 통과한다.
- 성공 기준 2: PR #102 의 e463dc97 에서 CI 30개가 모두 통과했다. windows-latest 3.9 와 3.12 의 샤드 12개가 모두 통과했다. 고치기 전
  49606b7c 에서는 windows-latest 3.9/3.12 의 샤드 6 이 실패했다. CI 러너는 영어 로캘(cp1252)이다. 한국어 Windows(cp949)에서
  따로 돌리지 않았다.
- scripts 전체 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
- `.stage/operations/verification.md` 의 "Windows 동작 확인"(영어가 아닌 로캘의 실제 Windows 실행)은 아직 하지 못했다. 2026-11-22 사용자가 한국어 Windows(Python 3.14)에서 돌렸지만 그 체크아웃은 이 카드가 들어가기 전의 main 이었다(`test_release_plugin.py` 8개). #102 를 머지한 뒤 다시 돌린다.
- 2026-11-22 사용자가 한국어 Windows(Python 3.14, main 2b3dc45e, 이 카드 포함)에서 `test_release_plugin.py` 를 돌렸고 12개가 모두 통과했다(`test_check_released_prints_utf_8_when_the_console_is_cp1252` 포함). 위의 "아직 하지 못했다"는 이 실행으로 채워졌다.
