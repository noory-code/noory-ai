---
id: W-00000153
title: 빈 목록 그릇을 갱신과 감사가 알아보게 한다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 stage/scripts/audit_stage.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/guidance_docs.py, stage/scripts/refresh_guidance.py, stage/scripts/tests/test_refresh_guidance.py, stage/docs/SCHEMA_V5.md, stage/skills/stage-audit/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000153 빈 목록 그릇을 갱신과 감사가 알아보게 한다

## Purpose

설명 문서 갱신은 프로젝트가 쌓은 내용을 표의 데이터 행으로만 알아본다. 그래서 관측 인덱스처럼
불릿으로 쌓는 문서는 기본 실행에서 빠지고, 플러그인이 설명글을 고쳐도 낡은 판으로 남는다.
DE-00000047 이 답을 정했다 — **빈 그릇의 뜻을 표에서 목록까지 넓힌다.** 템플릿은 이미 빈 불릿
하나를 배포하고 있으므로 템플릿은 안 고친다. 코드가 그것을 읽게 하는 일만 남았다.

지금 하는 이유: 자동 갱신이 줄어든 값을 다른 프로젝트가 먼저 치르고 있고(O-00000012), 이
저장소는 그 값을 `guidance_overrides` 로 가려 두었다. 코드가 고쳐지면 그 가림막이 필요 없어진다.

## Actions

- 목록 그릇 탐지를 붙인다. 항목 줄과 거기 딸려 들여쓰인 감김 줄까지가 한 항목이다.
- `template_mode` 를 표 모양이 아니라 그릇 모양으로 분류한다. 빈 그릇이 둘 이상이면 거절한다 —
  표 둘, 목록 둘, 표 하나와 목록 하나가 모두 같다.
- 합치기를 표 행에서 그릇 항목으로 넓힌다.
- 선언한 그릇이 프로젝트 파일에 없을 때의 판정을 `refused` 에서 `skipped` 로 바꾼다. 지금은
  경로를 집어도 열리지 않고 명령 전체가 실패로 끝난다.
- `guidance_matches` 가 같은 그릇을 보게 한다. 안 하면 감사가 영원히 낡음을 보고한다.
- 도움말·스키마 문서·감사 스킬의 갈래 서술을 그릇 어휘로 고친다.
- **채워진 목록에는 새 갈래를 만들지 않는다.** 만들면 깨끗한 프로젝트의 불변 조건 문서가 자동
  갱신을 조용히 잃는다.

## User value

플러그인이 설명글을 고치면 프로젝트가 손 안 대고 받는다. 지금은 낡음 보고를 읽고 사람이 경로를
하나씩 집어 줘야 하고, 안 집으면 프로젝트 문서가 낡은 판으로 남는다.

## Scope

### Included

- 갱신 판정 코드와 감사 쪽 짝.
- 도움말 한 줄, 스키마 문서의 갱신 안전 절, 감사 스킬의 갈래 목록.
- 회귀 시험.
- 미출시 절 릴리스 노트.

### Excluded

- 템플릿. 분류가 바뀌는 둘(`state/current.md` 영어·한국어)은 빈 불릿을 이미 배포한다.
- 마이그레이션. 옮길 데이터가 없다.
- `official/model/` 셋에 그릇을 주는 일. DE-00000047 이 열린 물음으로 남겼다.
- 이 저장소 `settings.json` 의 `guidance_overrides` 정리. 사용자 확인을 받고 따로 한다.

## Risks

- 빈 표 갈래는 본문이 한 줄로 뭉개진 결함 이력이 있고 재현 조건을 못 찾았다(R-00000142). 갈래를
  넓히면 그 결함에 닿는 문서가 늘어난다. 감김 줄 보존 시험이 그 자리를 지킨다.
- 그릇 밖 본문은 템플릿이 소유한다. 프로젝트가 그릇 밖에 쓴 문장은 갱신 때 템플릿 문장으로
  바뀐다. `state/current.md` 에서는 실측으로 잃는 줄이 0이지만, 다른 프로젝트에서는 확인된 값이
  아니다.
- 이 저장소에서는 관측 인덱스가 `guidance_overrides` 에 있어 기본 실행이 판정에 닿지 않는다.
  검증은 단위 시험으로 하고, 손 실측은 override 를 임시로 걷고 한다.

## Success criteria

- 쌓인 불릿이 살아남고 그릇 밖 템플릿 문장은 새 판으로 들어온다.
- 여러 줄로 감기는 항목이 한 줄로 안 뭉개진다.
- 그릇이 없는 프로젝트 파일은 `skipped` 로 나오고, 경로를 집으면 통째로 교체된다.
- 채워진 목록을 가진 문서는 오늘 동작을 그대로 유지한다 — 설명 안 되는 줄 시험을 받고, 깨끗한
  사본은 자동 갱신된다.
- 감사가 관측을 쌓은 관측 인덱스를 낡음으로 보고하지 않는다.
- 사람이 겪는 결과: 이 저장소에서 `guidance_overrides` 의 관측 인덱스 항목을 임시로 걷고 기본
  갱신을 돌렸을 때, 관측 항목이 하나도 안 사라지고 명령이 실패로 끝나지 않는다.

## Next action

`guidance_docs.py` 의 목록 그릇 탐지 시험을 먼저 쓴다.

## Progress

## Verification

### 리뷰 지적 판단 — 1회차 (승인, 막지 않는 지적 넷)

- **빈 목록 옆 채워진 목록이 조용히 합쳐진다 (표는 같은 자리에서 거절한다)** — **미룸.** 목록은
  설명글에 흔하게 쓰이므로, 표와 똑같이 거절하면 템플릿이 자기 그릇 위에 설명을 못 적는다. 지금
  `empty_list` 템플릿은 하나뿐이고 그 안에 목록도 하나라 위치 맞추기 규칙을 시험할 실제 사례가
  없다. 다른 판정을 일부러 고른 것이라고 문서와 시험에 남기고, 위치 맞추기 손질은 W-00000154 로
  옮겼다.
- **빈 표 옆 채워진 표를 거절하는 갈래에 회귀 시험이 없다** — **받음.** 이 카드가 분류 함수를
  다시 짰으므로 시험 없이 도는 갈래다. `test_empty_table_beside_populated_table_is_refused`
  추가.
- **성공 기준의 "관측 24줄" 이 낡았다** — **받음.** 설계 카드가 관측을 하나 더해서 숫자가
  변했다. 숫자를 박지 않고 "항목이 하나도 안 사라진다"로 고쳤다.
- **표가 섞인 경우 거절을 설명하는 문서가 없다** — **받음.** `stage/docs/SCHEMA_V5.md` 와 감사
  스킬에 두 모양을 다르게 다루는 이유까지 적었다.

## Retrospective

## Promotion decision
