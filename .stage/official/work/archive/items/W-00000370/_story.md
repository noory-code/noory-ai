---
id: W-00000370
title: 카드에서 회고 칸을 없애고 유지 카드는 두 가지만 묻는다
kind: development
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000370
promotion: not_applicable
review: passed
scope: stage/skills/stage-work,stage/scripts,stage/templates,stage/hooks,stage/skills/stage-retrospective,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000370 카드에서 회고 칸을 없애고 유지 카드는 두 가지만 묻는다

## Purpose

카드에 회고 파일과 겹치는 칸이 없고 유지 카드는 무엇이 무너졌나와 다시 서면 끝만 답하고 등록된다

## Actions


## User value


## Scope

### Included


### Excluded

- 이미 등록됐거나 보관된 카드는 고치지 않는다. 이 카드 자신도 고치기 전에 시작해서 두 칸을 가지고 있다.
- 스키마 v3 용 양식(`stage/templates/project-stage/`)은 고치지 않는다.
- 회고 파일의 칸은 줄이지 않는다. DE-00000089 가 미뤘다.


## Risks


## Success criteria

- 새로 등록하거나 시작한 카드에 Retrospective 와 Promotion decision 칸이 없고, 닫기와 감사가 그 칸 없이 통과한다
- 유지 카드를 등록할 때 User value, Risks, Related truth, Next action 칸이 생기지 않고, 스킬은 무엇이 무너졌나와 다시 서면 끝만 묻는다
- 어떤 카드가 유지인지 가르는 기준이 스킬에 한 줄로 적혀 있다
- 이미 보관된 카드는 고치지 않는다

## Next action

## Related truth

- 덜어낼 것을 고른 결정: DE-00000089 의 2번과 3번.
- 유지와 성취를 가르는 기준: `stage/docs/PHILOSOPHY.md` 의 `성취와 유지는 다르다`.
- 카드 칸의 계약: `stage/docs/SCHEMA_V5.md` 의 `Work record questions`.

## Progress

- 진행 중 카드 양식 세 개와 `start_work.py` 에서 `## Retrospective`, `## Promotion decision` 을 뺐다.
- `register_work.py --maintenance` 를 넣었다. 카드에 `maintenance: true` 를 적고 `## User value`,
  `## Risks`, `## Next action`, `## Related truth` 를 넣지 않는다. 계획된 카드로 등록했다가 시작해도 같다.
- `--maintenance` 는 `--milestone` 과 함께 쓰거나 에픽에 쓰면 거절한다. 유지는 마일스톤에 매달지 않는다는
  철학 문서의 내용을 따랐다.
- `stage-work` 스킬 맨 앞에 유지와 성취를 가르는 질문 하나와 유지 카드의 두 질문을 넣었다.
- `SCHEMA_V5.md`, 작업 로그 머리말, 변경 기록을 고쳤다. `SCHEMA_V5.md` 는 선언한 범위 밖이다.
- 이 저장소의 `.stage/work/current/` 양식 사본 세 개를 `refresh_guidance.py` 로 새 양식에 맞췄다. 감사가
  사본이 양식과 다르다고 경고했기 때문이다. 이것도 선언한 범위 밖이다.
- 테스트 9개를 먼저 썼다. 고치기 전에는 5개가 실패했다. 예전 칸을 확인하던 테스트 2개를 고쳤다.

## Verification

맥북(macOS)에서 코드 커밋 `8d0d4f88` 로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/scripts/tests -p test_card_sections.py` | 9개 통과 |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 450개 통과 |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 804개 통과, 2개 건너뜀 |
| `python3 stage/scripts/audit_stage.py` | 오류 0건, 경고 32건 |

- 유지 카드를 이 저장소에 실제로 등록해 보지는 않았다. 임시 프로젝트에서 등록하고 시작하는 테스트로 확인했다.
- 스킬을 읽은 새 세션이 유지와 성취를 실제로 가르는지는 확인하지 않았다.
- 사용자 확인 — 2026-11-21: 고친 것, 정한 것 세 가지, 범위 밖으로 나간 것, 확인하지 않은 것을 보고 "확인, 닫으세요" 라고 답했다.
- 닫을 때의 리뷰는 만든 쪽과 같은 모델(Claude)이 본다. Codex 를 쓰지 않는 환경이라 DE-00000087 에 따라 사용자 확인을 함께 받았다.

- Checks at close 2026-11-21: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_card_sections.py`; `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS, 4 PASS)

## Retrospective

## Promotion decision
