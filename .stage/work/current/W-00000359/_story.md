---
id: W-00000359
title: 리뷰 명령을 셸 문법 없이 Python 스크립트로 실행하기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_run_review.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000359
promotion: pending
review: pending
scope: stage/scripts/run_review.py,stage/scripts/tests,stage/docs/SCHEMA_V4.md,stage/templates/v4/project-stage/settings.jsonc,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000359 리뷰 명령을 셸 문법 없이 Python 스크립트로 실행하기

## Purpose

이 프로젝트의 리뷰 명령이 POSIX 셸 문법으로 출력을 받아 작업 로그에 덧붙이기 때문에 Windows 의 cmd.exe 에서 실행되지 않아 리뷰가 필요한 카드를 닫지 못하는 것을 고쳐, 설정 파일 하나로 Windows 에서도 카드를 끝까지 닫을 수 있게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

Windows 에서 일하는 사람이 리뷰가 필요한 카드를 그 자리에서 닫을 수 있다. 지금은 카드를 macOS 로
넘겨야 한다. W-00000352, W-00000356, W-00000357 이 그렇게 넘어갔다.

## Scope

### Included

- `stage/scripts/run_review.py` 를 더한다. 리뷰어를 셸 없이 실행하고, 출력을 작업 로그에
  `### Reviewer report` 로 덧붙이고, 리뷰어의 종료 코드로 끝난다. 인자 안의 `$STAGE_이름` 을 직접
  펼친다. `cmd.exe` 는 그것을 펼치지 않기 때문이다.
- 이 프로젝트 `.stage/settings.json` 의 리뷰 명령 여섯 개를 그 스크립트 호출로 바꾼다.
- 프로젝트의 리뷰 명령에 셸마다 다르게 읽히는 문법이 들어오면 실패하는 테스트를 더한다.
- Windows 에서 건너뛰던 테스트 두 개의 건너뛰기를 없앤다.
- `docs/SCHEMA_V4.md`, 설정 템플릿의 설명, `stage/CHANGELOG.md` 에 적는다.

### Excluded

- 실행자 명령(`executors`). 이 명령도 POSIX 문법(`$STAGE_…`, 작은따옴표)을 쓴다. 감독 모드와 닫기는
  실행자 명령을 쓰지 않으므로 이 카드에서 다루지 않는다.
- `close_work.py` 와 드라이버가 명령을 실행하는 방식. `docs/SCHEMA_V4.md` 가 정한 대로 플랫폼의
  셸(`cmd.exe` 또는 `sh`)로 넘기는 것을 그대로 둔다.
- Stage 릴리스.

## Risks

- 닫기 절차가 쓰는 리뷰 명령을 바꾼다. DE-00000087 에 따라 사용자가 확인한 뒤에 닫는다.
- 리뷰어 출력을 한꺼번에 받아서 끝난 뒤에 출력한다. 예전 셸 명령도 `OUT=$(…)` 로 같은 방식이었다.
- macOS 와 Linux 에서는 이 카드에서 실행해 보지 않았다. CI 가 세 OS 에서 테스트를 실행한다.

## Success criteria

- Windows 에서 이 프로젝트의 리뷰 명령이 close_work 를 거쳐 실행되고 리뷰어의 출력이 작업 로그에 남는다
- 프로젝트 설정의 리뷰 명령에 셸마다 다르게 읽히는 문법이 없고, 들어오면 테스트가 실패한다
- 리뷰어가 받는 프롬프트에서 `$STAGE_이름` 이 cmd.exe 와 POSIX 셸 양쪽에서 같은 값으로 바뀐다

## Next action

사용자가 확인하면 커밋하고, 이 Windows 에서 `close_work.py` 로 닫는다. 닫히면 그것이 첫 번째 성공
기준의 증거다.

## Related truth

- 루트 `CLAUDE.md` 의 Cross-Platform 표: 셸 스크립트 대신 Python 을 쓴다.
- `stage/docs/SCHEMA_V4.md`: 설정의 명령은 플랫폼의 셸로 실행되고, Windows 에서는 `cmd.exe` 다.
- 사용자 결정(2026-11-20): Windows 에서 Git 의 `sh` 로 명령을 실행하자는 첫 제안을 "우리 파이썬만
  쓰기로 했던 것 같다"며 멈추게 했고, 리뷰 명령을 Python 으로 바꾸는 방법을 골랐다.
- DE-00000087: 닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress

- 2026-11-20: 처음에는 `close_work.py` 가 Windows 에서 Git 의 `sh` 를 찾아 명령을 넘기게 하려고
  이 카드를 등록했다. 사용자가 멈추게 했다. 그 방법은 Stage 를 Git Bash 에 기대게 하고,
  `SCHEMA_V4.md` 를 따라 `%VAR%` 문법으로 쓴 Windows 설정을 깨뜨린다. 카드의 제목, 목적, 범위를
  지금 내용으로 고쳐 썼다. 그 방법의 코드는 쓰지 않았다.
- `run_review.py` 와 테스트 12개를 썼다. 설정의 리뷰 명령 여섯 개를 스크립트로 바꿨다. 손으로
  고치지 않고, 모양이 예상과 다르면 멈추는 스크립트로 바꿨다.
- 감독 모드의 팀원을 띄우지 않고 이 세션이 직접 고쳤다. Windows 에는 tmux 가 없다.
- 범위 밖 파일: `.stage/settings.json` 을 고쳤다. `.stage/` 는 관리 대상 소스가 아니라서 `scope` 에
  적지 않았다.

## Verification

기기: Windows 11 (10.0.28000) ARM64. 로캘: 콘솔 코드 페이지 949, `cp949`. Python 3.14.10.
Claude Code 2.1.326. 명령은 저장소 루트에서 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest stage/scripts/tests/test_run_review.py` | 12개가 통과했다. |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 448개가 통과했다(44개 건너뜀). |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 783개 가운데 2개가 실패했다(4개 건너뜀). 아래 참고. |
| `STAGE_LIVE_REVIEW_PROBE=1 python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -k LiveReviewerWriteProbeTest -v` | 2개가 통과했다(66초). |

- 전체 실행에서 실패한 2개는 이 카드가 만든 것이다. 하나는 예전 셸 명령 문자열을 기대하던
  `test_project_claude_reviewer_runs_through_the_companion` 이고, 다른 하나는 템플릿 설명에 백틱을
  넣어서 걸린 `test_v4_settings_template_does_not_suggest_backtick_command_substitution` 이다. 둘 다
  고쳤고, 그 뒤 `test_claude_review_guard.py`, `test_template_v4.py`, `test_run_review.py` 세 파일을
  다시 실행해 통과를 확인했다. 그 뒤 전체를 다시 실행했고 783개가 통과했다(4개 건너뜀, 648초).
- 건너뛴 테스트가 5개에서 4개로 줄었다. `test_project_claude_reviewer_may_write_only_its_verdict_file`
  이 이제 Windows 에서 실행된다.
- 실제 리뷰어 검사 2개는 진짜 `claude` 를 띄운다. `project reviewers.claude` 경로에서 이 프로젝트의
  리뷰 명령이 `cmd.exe` 를 거쳐 실행됐고, 리뷰어가 테스트를 실행했고(`exercised: true`), 테스트가
  `tracked.txt` 를 바꾸자 `close_work` 가 판정 파일을 지우고 리뷰를 실패로 남겼다. 이 검사는
  Windows 에서 처음 실행됐고, 검사 자체에도 Windows 문제가 세 군데 있어 함께 고쳤다(`claude` 를
  확장자 없이 실행, `shlex.quote` 의 작은따옴표, `run_review.py` 를 복사하지 않음).
- macOS 와 Linux 에서는 실행하지 않았다.
- 리뷰는 아직 받지 않았다. 닫을 때 받는 리뷰는 codex 가 아니라 같은 모델(Claude 대역)의 리뷰다.

## Retrospective


## Promotion decision

