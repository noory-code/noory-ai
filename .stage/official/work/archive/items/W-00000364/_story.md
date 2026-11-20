---
id: W-00000364
title: 두 번 넘게 겪은 실수 세 가지를 규칙 문서에 올린다
kind: documentation
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000364
promotion: not_applicable
review: passed
scope: CLAUDE.md,AGENTS.md,stage/skills/stage-drive,stage/README.md,stage/CHANGELOG.md,.stage/operations
promotes:
decision_refs:
---

# W-00000364 두 번 넘게 겪은 실수 세 가지를 규칙 문서에 올린다

## Purpose

두 번 넘게 겪은 실수 세 가지가 규칙 문서에 있어서 다음 세션이 같은 실수를 하지 않는다

## Actions

카드 하나로 한다. 나누지 않는다.

## User value

회고가 "규칙으로 올릴 만하다"고 적어 둔 것이 회고에만 남아 있으면 다음 세션은 읽지 않는다. 세션이 시작할 때
읽는 문서에 있어야 같은 실수를 다시 하지 않는다. 마일스톤 M-00000005 의 완료 기준 가운데 "세 규칙을 올린다"가
이 카드다.

## Scope

### Included

- 텍스트를 읽고 쓸 때 인코딩을 지정한다는 규칙을 루트 `CLAUDE.md` 의 Cross-Platform 표에 넣는다.
- 두 세션이 일할 때 등록하기 전에 fetch 하고 등록한 뒤 바로 push 한다는 규칙을 `.stage/operations/` 에 넣는다.
- 드라이버를 실행할 때 작업 폴더를 비운다는 규칙이 근거 회고와 함께 규칙 문서에 있는지 확인한다.
- `stage/README.md` 의 훅 목록을 `hooks.json` 의 이벤트 다섯 가지에 맞춘다.

### Excluded

- 회고의 다른 규칙 후보. 2026-11-20 에 센 값으로 34개가 있고, 이 카드는 두 번 넘게 겪은 세 가지만 올린다.
- 번호가 겹치지 않게 만드는 설계. W-00000367 이 맡는다. 이 카드의 규칙은 그 전까지 사람이 지키는 절차다.
- 인코딩을 지정하지 않은 호출을 코드에서 찾아 고치는 일.

## Risks

- 두 세션 규칙은 사람이 지켜야 한다. 잊으면 번호가 다시 겹친다. 훅이나 감사가 잡아 주지 않는다.

## Success criteria

- 드라이버를 실행하기 전과 실행하는 동안 작업 폴더를 비운다는 규칙이 근거 회고(R-00000248, R-00000259)를 인용하며 규칙 문서에 있다
- 텍스트를 읽고 쓸 때 인코딩을 지정한다는 규칙이 근거 회고(R-00000354, R-00000356)를 인용하며 규칙 문서에 있다
- 두 세션이 일할 때 카드를 등록하기 전에 fetch 하고 등록한 뒤 바로 push 한다는 규칙이 근거 회고(R-00000250, R-00000358)를 인용하며 규칙 문서에 있다
- stage/README.md 의 훅 목록이 hooks.json 에 있는 이벤트 다섯 가지와 같다

## Next action

사용자 확인을 받고 닫는다. `.stage/operations/` 에 문서를 더했고, DE-00000087 이 이 경로를 고친 카드는 Codex 가
없는 환경에서 사용자 확인을 받게 정했다.

## Related truth

- 규칙 후보를 적은 회고: R-00000248, R-00000259, R-00000354, R-00000356, R-00000358. R-00000250 은 번호가
  겹친 다른 사례다.
- 번호를 세는 방식: `stage/scripts/stage_record_ids.py` 의 설명. 이미 받아 온 브랜치만 세고 네트워크에는
  가지 않는다.
- 훅 이벤트의 SSOT: `stage/hooks/hooks.json`. 이벤트별 설명은 `stage/hooks/README.md`.

## Progress

- 드라이버 규칙은 이미 있었다. `stage/skills/stage-drive/SKILL.md` 의 "Start every driver step from a clean
  working tree" 문단이 실행 전과 실행 중을 모두 말하고 끝에 R-00000248 과 R-00000259 를 인용한다. 고치지
  않았다. 카드를 등록할 때 이 문단을 열어 보지 않았다.
- 인코딩 규칙을 루트 `CLAUDE.md` 의 Cross-Platform 표에 한 줄로 넣고, 표 아래에 이유와 근거 회고를 적었다.
- 두 세션 규칙을 `.stage/operations/parallel-sessions.md` 에 새로 썼다.
- `stage/README.md` 의 훅 목록에 `SubagentStop` 을 넣었다. `stage/CHANGELOG.md` 의 `## Unreleased` 에 적었다.
- 범위 밖으로 나간 것: `.stage/index.md` 에 새 운영 문서로 가는 줄을 넣었다. 감사가 새 문서가 색인에 없다고
  경고(ROUTE002)해서 넣었다.
- `AGENTS.md` 와 `stage/skills/stage-drive` 는 범위에 있지만 고치지 않았다. `AGENTS.md` 는 `CLAUDE.md` 를
  따르라고만 적혀 있어 같은 규칙을 다시 적지 않는다.

## Verification

맥북(macOS)에서 커밋 `5f264c7b` 로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/hooks/tests -q` | 통과 |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 804개 통과, 2개 건너뜀 |
| `python3 stage/scripts/audit_stage.py` | 오류 0건, 경고 32건 |

- 훅 목록은 `hooks.json` 의 이벤트 이름 다섯 개(`PreToolUse`, `SessionStart`, `Stop`, `SubagentStop`,
  `PostToolUse`)와 README 의 다섯 줄을 눈으로 맞춰 보았다. 둘을 비교하는 테스트는 없다.
- 새 세션이 이 규칙들을 읽고 실제로 지키는지는 확인하지 않았다.
- 사용자 확인 — 2026-11-21: 고친 것 네 가지, 첫째 규칙이 이미 있었다는 것, R-00000250 의 원인이 다르다는 것,
  범위 밖으로 나간 것, 확인하지 않은 것을 보고 "확인, 닫으세요" 라고 답했다. 리뷰 판정은 확인 뒤에 받았다.
- 닫을 때의 리뷰는 만든 쪽과 같은 계열(Claude)이 본다. 문서만 고친 카드라 리뷰 모델은 `sonnet` 으로 한다.

- Checks at close 2026-11-21: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS, 4 PASS)
