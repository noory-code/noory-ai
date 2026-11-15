---
id: W-00000334
title: 세션 시작 글에 인라인 코드 규칙을 싣는다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_session_context_inline_rule.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_context.py, stage/hooks/tests/test_session_context_inline_rule.py, stage/hooks/README.md, stage/operations/hooks.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000334 세션 시작 글에 인라인 코드 규칙을 싣는다

## Purpose

Stage 작업 폴더를 건드리는 인라인 인터프리터 코드를 훅이 거절한다는 규칙을 세션이 시작할 때 알려, 거절당하고 다시 시도하는 왕복을 줄인다

## Actions

없음 — 한 함수에 한 줄을 넣고 시험과 문서를 맞추는 일이라 나누지 않는다.

## User value

세션이 `.stage` 를 건드리는 `python3 -c` 나 인터프리터 heredoc 을 쓰기 전에 그 명령이 거절된다는
것을 안다. 지금은 거절당한 뒤에야 알고 다른 방법으로 다시 시도한다. 최근 세션 50개(2026-11-02
~11-16)에서 이 거절이 67번 났고, Stage 훅이 낸 거절 115번 가운데 가장 많았다.

## Scope

### Included

- 세션 시작 글의 기본 안내에 규칙 한 줄을 넣는다. 그 줄은 무엇이 거절되는지와 대신 쓸 방법
  (Write/Edit, 이름 있는 스크립트 파일)을 말한다.
- 새 구조(v4)와 옛 구조 두 갈래가 같은 줄을 쓴다.
- 그 줄이 두 갈래에 실리는지 확인하는 시험을 더한다.
- 세션 시작 글을 설명하는 두 문서(`stage/hooks/README.md`, `stage/operations/hooks.md`)와 변경
  기록을 맞춘다.

### Excluded

- 거절 조건과 거절 메시지를 바꾸지 않는다. 훅은 인라인 코드가 무엇을 쓰는지 볼 수 없으므로
  거절은 그대로 둔다.
- 세션 시작 글의 다른 부분을 줄이거나 합치지 않는다. 열린 관찰 목록에 개수 상한을 두지 않는다
  (`db9f74f1` 이 일부러 없앴다).
- 하위 에이전트와 드라이버 실행자에게 이 규칙을 따로 전하지 않는다. 그쪽이 세션 시작 글을
  받는지는 확인하지 않았다.

## Risks

- 긴 세션이 요약되면 시작 글도 함께 줄어든다. 그 뒤에는 이 줄이 남지 않을 수 있어 거절이 모두
  사라지지는 않는다.
- 세션 시작 글이 한 줄만큼 길어진다(약 200자). 세션마다 치르는 값이다.
- 거절 횟수가 실제로 줄었는지는 이 카드 안에서 잴 수 없다. 며칠 치 세션 기록이 쌓인 뒤 같은
  방법으로 다시 잰다.

## Success criteria

- 세션 시작 글에 그 규칙이 한 줄로 실리고, 새 구조(v4)와 옛 구조 두 갈래 모두에 실린다
- 훅의 거절 동작과 거절 메시지는 그대로다
- 그 줄이 실리는지 확인하는 시험이 있고 통과한다

## Next action

`stage/hooks/tests/test_session_context_inline_rule.py` 에 깨지는 시험을 먼저 쓰고,
`stage/hooks/stage_context.py` 의 `session_context` 두 갈래에 같은 줄을 넣는다.

## Related truth

- `stage/hooks/stage_guard.py` 의 `interpreter_inline_stage_write` — 거절을 내는 자리. 이 카드는
  건드리지 않는다.
- DE-00000086 — codex 가 없는 로컬 세션에서 Claude 가 실행하고 닫기 리뷰를 따로 받는다.
- DE-00000087 — `stage/hooks/` 를 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress


## Verification


## Retrospective


## Promotion decision
