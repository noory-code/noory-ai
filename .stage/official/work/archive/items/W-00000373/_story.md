---
id: W-00000373
title: 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다
kind: fix
maintenance: true
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000373
promotion: not_applicable
review: passed
scope: stage/hooks,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000373 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다

## Purpose

세션 시작 글이 상태가 selected 인 계획 카드를 보여 주지 않고 오늘 연 관찰을 open -1d 로 보여 준다

## Actions


## Scope

### Included


### Excluded


## Success criteria

- 상태가 selected 인 폴더 카드(_story.md, _epic.md)가 세션 시작 글의 Selected backlog 에 나온다
- 한국 시각으로 오늘 연 관찰이 UTC 날짜가 하루 앞이어도 open 0d 로 나온다

## Progress

- 세션 시작 글의 두 함수가 이름이 `_` 로 시작하는 파일을 모두 건너뛰고 있었다. 그 줄을 지우고
  `record_paths` 의 규칙(맨 위 템플릿은 빼고 폴더 안의 `_story.md`, `_epic.md` 는 남긴다)을 따르게 했다.
- 끝나는 조건 밖에서 고친 것: 같은 원인으로 `planned — none` 이라고 나오고 보관한 카드를 32장으로 세던
  것도 고쳤다. 이 저장소에서는 계획 카드 4장, 보관한 카드 368장으로 나온다.
- 관찰이 며칠째 열려 있는지를 UTC 날짜가 아니라 세션이 실행되는 곳의 날짜로 센다(`local_today`).
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 두 줄을 적었다.
- 범위 밖으로 나간 것: 카드를 시작하고 닫으면서 `.stage` 의 카드와 색인 파일이 바뀌었다.

## Verification

맥북(macOS)에서 커밋 `aa96c933` 으로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/hooks/tests -q` | 455개 통과 |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 804개 통과, 2개 건너뜀 |
| `python3 -m unittest tests.test_plugin_contracts -q` | 7개 통과 |
| `python3 stage/scripts/audit_stage.py --project-root .` | 오류 0건, 경고 32건 |

- 새 테스트 다섯 개(`test_session_context_selected_cards.py`)는 고치기 전에 실패하는 것을 먼저 보았다.
- 이 저장소에서 훅을 직접 실행해 Selected backlog 에 W-00000366, W-00000367 이 나오는 것을 보았다.
- 다른 시간대의 컴퓨터에서 연 관찰은 하루 어긋날 수 있다. 고치지 않았다.
- Windows 에서는 실행하지 않았다.
- 사용자 확인 — 2026-11-21: 고친 세 군데와 원인 두 가지, 끝나는 조건 밖에서 고친 것, 테스트 결과를 보고
  "확인, 닫으세요" 라고 답했다. 리뷰 판정은 확인 뒤에 받았다.
- 닫을 때의 리뷰는 만든 쪽과 같은 계열(Claude)이 본다. 훅 코드를 고친 카드라 리뷰 모델은 `opus` 로 한다.

- Checks at close 2026-11-21: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS)
