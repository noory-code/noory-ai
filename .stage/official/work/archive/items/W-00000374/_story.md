---
id: W-00000374
title: Windows 에서 리뷰어가 PowerShell 도구로도 테스트를 실행하게 하기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000374
promotion: not_applicable
review: passed
scope: stage/scripts/claude_review_companion.py,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000374 Windows 에서 리뷰어가 PowerShell 도구로도 테스트를 실행하게 하기

## Purpose

Windows 의 Claude Code 는 셸 도구를 Bash 와 PowerShell 두 가지로 주는데 리뷰어에게 허용한 규칙은 Bash 도구에만 걸려 있어서, 리뷰어가 PowerShell 도구로 테스트를 실행하면 거절되고 기록만 읽고 판정하게 되는 것을 고쳐, Windows 에서도 리뷰어가 테스트를 직접 실행해 판정하게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

Windows 에서 카드를 닫을 때 리뷰어가 테스트를 직접 실행해 보고 판정한다. 지금은 리뷰어가 PowerShell
도구를 고르면 실행이 거절돼서 카드에 적힌 기록만 읽고 통과로 판정한다. W-00000361 을 닫을 때 리뷰어가
"감사와 테스트 명령은 실행 승인을 받지 못했다"고 보고했다.

## Scope

### Included

- `claude_review_companion.py` 가 Windows 에서 `PowerShell(python3 -m unittest:*)` 규칙을 함께 허용한다.
- 플랫폼마다 허용 목록이 무엇인지 확인하는 테스트를 더한다.
- `stage/CHANGELOG.md` 에 적는다.

### Excluded

- 감사 명령(`audit_stage.py`)을 리뷰어에게 허용하는 일. 리뷰어는 어느 OS 에서든 `python3 -m unittest` 만
  실행할 수 있게 설계돼 있다.
- macOS 와 Linux 의 허용 목록. 그대로 둔다.
- Stage 릴리스.

## Risks

- 리뷰어의 권한을 넓히는 변경이다. DE-00000087 에 따라 사용자가 확인한 뒤에 닫는다. 넓어지는 것은
  이미 Bash 도구로 허용한 명령을 PowerShell 도구로도 실행하는 것뿐이다.
- W-00000361 의 리뷰어가 실제로 PowerShell 도구를 썼는지는 확인하지 못했다. 작업 로그에는 도구 호출이
  남지 않는다. 그래서 이 고침이 그때의 거절을 없앤다고 단정하지 않는다.

## Success criteria

- 리뷰어 명령의 허용 목록에 PowerShell 도구로 python3 -m unittest 를 실행하는 규칙이 있다
- 허용 목록이 여전히 판정 파일 쓰기와 python3 -m unittest 실행만 허용한다

## Next action

사용자 확인을 받은 뒤 닫는다.

## Related truth

- DE-00000086: codex 가 없는 환경에서는 같은 모델이 리뷰한다.
- DE-00000087: 리뷰어의 권한을 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress

- `unittest_rules(platform)` 을 더했다. `win32` 에서만 PowerShell 규칙을 붙인다. macOS 와 Linux 의
  Claude Code 에는 PowerShell 도구가 없어서 그쪽 허용 목록은 바꾸지 않았다.
- `claude_command` 가 플랫폼을 인자로 받는다. 기본값은 `sys.platform` 이다. 테스트가 세 플랫폼의 허용
  목록을 한 기기에서 확인하려고 인자로 뺐다.

## Verification

- 환경은 `local-no-codex` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다(DE-00000086).
- 한국어 Windows 11(cp949)에서 실제 `claude`(haiku)로 고치기 전 규칙을 확인했다. Bash 규칙만 허용하고
  PowerShell 도구로 `python3 -m unittest discover -s plainly/tests -q` 를 실행하게 하면 승인이 필요하다며
  거절됐다. 같은 조건에서 Bash 도구로는 실행됐다.
- 고친 `claude_review_companion.py` 를 같은 기기에서 직접 실행했다. 리뷰어(haiku)가 PowerShell 도구로 같은
  명령을 실행했고 테스트 22개가 통과했다고 답했다.
- `python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q` 9개,
  `-p test_template_v4.py` 26개, `-p test_claude_review_guard.py` 8개(2개 건너뜀)가 통과했다.
- 닫기 리뷰어의 모델인 opus 가 어느 셸 도구를 고르는지는 확인하지 않았다.
- macOS 와 Linux 에서는 실행하지 않았다. 그쪽 허용 목록은 테스트로만 확인했다.
- 사용자 확인 — 2026-11-21. 사용자가 바뀐 파일 네 개와 한 줄씩의 요약, 넓어지는 권한, 확인한 것과
  확인하지 못한 것을 보고 닫으라고 했다. 닫기 명령이 리뷰와 닫기를 한 번에 해서 기준별 리뷰 판정은
  확인받을 때 보여 주지 못했고, 그 사실을 알렸다.

- Checks at close 2026-11-21: 5 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`; `python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -q`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS)
