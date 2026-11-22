---
id: W-00000394
title: 한국어 Windows 에서 close_work 시험과 검사 출력이 깨지지 않게 한다
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
retrospective_ref: R-00000394
promotion: not_applicable
review: passed
scope: stage/hooks/stage_process.py,stage/skills/stage-retrospective/close_work.py,stage/scripts/tests/test_close_work.py,stage/hooks/tests/test_stage_process.py,stage/scripts/tests/test_stage_process.py,stage/CHANGELOG.md,.stage/official/work/archive/items/W-00000381/_story.md,.stage/official/work/archive/items/W-00000391/_story.md,.stage/official/work/archive/items/W-00000393/_story.md
promotes:
decision_refs:
---

# W-00000394 한국어 Windows 에서 close_work 시험과 검사 출력이 깨지지 않게 한다

## Purpose

한국어 Windows 에서 test_close_work.py 가 true 명령 없이도 통과하고, 실패한 검사의 메시지가 깨지지 않고 읽힌다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- test_close_work.py 가 true 같은 POSIX 명령 대신 어느 OS 에서나 도는 명령을 쓰고, 한국어 Windows 에서 모두 통과한다
- cmd.exe 가 cp949 로 낸 오류 메시지가 close_work 출력에서 깨지지 않는 시험이 있고 통과한다
- W-00000381, W-00000391, W-00000393 의 Verification 에 2026-11-22 한국어 Windows 실행 결과가 적혀 있다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: hooks/stage_process.run_bounded captures bytes and decode_output reads them as UTF-8 with replacement, switching to the Windows OEM code page only when replacement characters reach FALLBACK_SHARE (half) of the stream's non-ASCII bytes; test_close_work.py uses python_command("pass") instead of `true`; hooks/tests/test_stage_process.py covers UTF-8, a cp949 cmd.exe message, UTF-8 with a stray byte under cp949 and cp437 fallbacks, empty output, a UTF-8 child, and on Windows a cmd.exe error without replacement characters; the archived W-00000381, W-00000391, and W-00000393 cards record the user's Korean Windows runs; stage/CHANGELOG.md has an Unreleased entry.
Why: W-00000394 fixes what the user's Korean Windows run exposed (close_work tests depending on `true`, cmd.exe cp949 messages read as UTF-8) without breaking W-00000352's mixed-output contract, which the first attempt broke on PR #104's Windows CI.
Decisions made: Decide by the share of non-ASCII bytes that fail as UTF-8 instead of by strict validity, because a stray byte in UTF-8 output and a message in another code page differ by that share by an order of magnitude; fall back to the OEM code page rather than the ANSI one because cmd.exe writes its own messages there; reuse the existing python_command test helper instead of a new constant command; record the Korean Windows evidence on the three archived cards inside this card because it is the same follow-up and the card's scope names those files.
Work not done: The card's Korean Windows run of test_close_work.py and test_stage_process.py with this change is the user's to do; it is recorded when it arrives.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 코드 커밋은 f90f28bb(첫 시도)와 2e1420c2(두 번째 시도)다. 사이에 W-00000396 커밋이 있어서, 메인 세션은 두 커밋만 합친
  로컬 커밋 946138a5 에서 닫았다.
- 첫 시도는 PR #104 의 windows-latest 3.9/3.12 에서 `test_close_work_check_keeps_utf8_output_under_a_cp949_locale` 이 실패했다.
  두 번째 시도 2e1420c2 에서 CI 30개가 모두 통과했다(windows-latest 샤드 12개 포함, 영어 로캘).
- 성공 기준 1, 2: 사용자가 2026-11-22 에 한국어 Windows(Python 3.14)에서 2e1420c2 를 받아 `test_close_work.py`,
  `test_stage_process.py`, `test_subprocess_text_encoding.py` 를 돌렸고 "다 된 것 같다"고 통과를 보고했다. 출력은 붙이지 않았다.
  바꾸기 전에는 같은 기기에서 `test_close_work.py` 80개 가운데 28개가 실패했다.
- 성공 기준 3: W-00000381, W-00000391, W-00000393 의 Verification 에 한국어 Windows 실행 결과를 적었다.
- 메인 세션이 다시 돌린 검사: scripts 와 hooks 전체 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s stage/hooks/tests -p test_stage_process.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_subprocess_text_encoding.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS, 4 PASS)
