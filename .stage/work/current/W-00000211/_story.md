---
id: W-00000211
title: 설명 문서 갱신이 설명 못 하는 줄을 안 덮게 한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_refresh_guidance.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/refresh_guidance.py, stage/scripts/tests/test_refresh_guidance.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000211 설명 문서 갱신이 설명 못 하는 줄을 안 덮게 한다

## Purpose

설명 문서 갱신의 기본 실행이 프로젝트가 쌓은 내용을 빈 템플릿으로 갈아치운 적이 있으므로, 현행 템플릿에 없는 줄이 있는 문서를 기본 실행이 건드리지 않고 보고하게 한다

## Actions

없음 — 판정 규칙 하나를 `refresh_guidance.py` 에 싣고 회귀 시험을 더하는 한 덩어리다.

## User value

인자 없는 기본 실행이 프로젝트가 쌓은 인덱스와 표를 더는 못 지운다. novel-workspace 에서
관측 인덱스 22행과 모델 표들을 실제로 잃었고, `.stage/` 를 커밋하지 않는 프로젝트라면 복구
수단도 없다.

## Scope

### Included

- **판정 규칙을 싣는다** (DE-00000042 가 정했고 코드에는 아직 없다): 대상 파일의 비어 있지
  않은 줄 중 현행 템플릿에 같은 줄이 없는 줄이 하나라도 있으면, 인자 없는 기본 실행은 그
  파일을 건드리지 않고 무엇을 왜 뺐는지 보고한다. 표 구분선과 빈 줄은 세지 않는다.
- 사람이 경로를 인자로 콕 집으면 지금처럼 통째로 교체한다.
- 빈 표 갈래(표의 데이터 행을 프로젝트 것으로 알아보고 합치는 길)는 그대로 둔다.
- 새 동작의 회귀 시험을 `test_refresh_guidance.py` 에 더한다.

### Excluded

- 쌓이는 자리를 빈 표로 배포하는 후속안(DE-00000042 의 D 안)은 이 카드가 안 한다.
- `guidance_overrides` 설정의 뜻은 안 바꾼다 — 규칙이 실리면 덜 필요해질 뿐이다.

## Risks

- 판정이 너무 넓으면 갱신이 아무것도 못 덮는다. 템플릿이 문장을 고치면 옛 문장이 전부
  "설명되지 않는 줄"이 되므로, 그 경우 기본 실행이 빼고 보고하는 것까지가 결정된 동작이다.
- O-00000012 를 닫을 근거가 되는 카드라, 보고 문구가 사람이 다음 행동(경로 지정 실행)을 알
  수 있게 적혀야 한다.

## Success criteria

- 현행 템플릿으로 설명되지 않는 줄이 있는 문서는 인자 없는 기본 실행이 건드리지 않고, 무엇을 왜 뺐는지 알려 준다
- 사람이 경로를 인자로 지정하면 지금처럼 통째로 교체한다
- 빈 표 문서의 자동 합치기는 그대로 돈다

## Next action

`refresh_guidance.py` 의 기본 실행 갈래에서 대상 파일을 고르는 자리를 찾아 판정 시험을 끼운다.

## Related truth

- DE-00000042 — 갱신이 설명하지 못하는 줄은 프로젝트 것으로 본다 (판정 시험의 원문).
- O-00000012 — novel-workspace 실측 피해 기록. 이 카드가 닫히면 그 관측을 닫는다.


## Progress


## Verification


## Retrospective


## Promotion decision
