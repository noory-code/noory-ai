---
id: W-00000142
title: 갱신이 설명하지 못하는 줄을 지우지 않는다
kind: fix
venue: codex
milestone:
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/guidance_docs.py, stage/scripts/refresh_guidance.py, stage/scripts/tests/, stage/docs/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000142 갱신이 설명하지 못하는 줄을 지우지 않는다

## Purpose

DE-00000042 를 코드에 싣는다. 설명 문서를 갱신하는 명령의 기본 실행이, 현행 템플릿으로 설명되지
않는 줄을 가진 파일을 건드리지 않고 보고한다. 지금은 표가 없는 문서를 통째로 교체하므로 프로젝트가
불릿으로 쌓은 인덱스가 사라진다 — 다른 프로젝트가 관측 22행을 실제로 잃었다(O-00000012).

같은 보고가 가져온 둘째 결함도 이 카드가 받는다. 빈 표 갈래에서 `official/work/archive/index.md`
의 본문 문단이 한 줄로 뭉개졌다. 이쪽은 결정과 어긋나는 구현 결함이다 — 그 갈래는 표의 데이터
행만 옮기고 나머지는 템플릿대로 두어야 한다.

## Actions

- `guidance_docs.py` 에 판정 함수를 세운다: 대상 파일의 비어 있지 않은 줄 중 현행 템플릿에 같은
  줄이 없는 것을 센다. 표 구분선과 빈 줄은 세지 않는다.
- `plan_refresh` 의 표 없는 갈래가 그 판정을 본다. 설명되지 않는 줄이 있고 사람이 지정하지
  않았으면 `skipped` 를 이유와 함께 돌려준다. 지정했으면 지금처럼 교체한다.
- **빈 표 갈래에는 이 판정을 적용하지 않는다.** 대신 그 갈래의 행 합치기가 표 밖 본문을 뭉개는
  결함을 고친다.
- `refresh_guidance.py` 의 도움말을 고친다. 지금 "채워진 표를 가진 파일만 명시했을 때 교체된다"고
  약속하는데, 그 약속이 표 없는 파일을 안 지킨다.
- `stage/docs/` 의 갱신 서술에 좁힌 조건을 반영한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절에 항목을 더한다. **매니페스트 버전은 안 건드린다.**

## Scope

`stage/scripts/guidance_docs.py`, `stage/scripts/refresh_guidance.py`, `stage/scripts/tests/`,
`stage/docs/`, `stage/CHANGELOG.md`.

**안 하는 것**: 템플릿을 고쳐 쌓이는 자리를 빈 그릇으로 배포하는 일. DE-00000042 가 그것을 후속
(W-00000143)으로 분리했다 — 이미 배포된 프로젝트의 목록을 옮기는 마이그레이션이 딸려 온다.

## Success criteria

- **회귀 시험 하나**: 관측을 불릿으로 쌓은 `state/current.md` 를 가진 프로젝트에서 인자 없는
  기본 실행이 그 파일을 안 건드리고 건너뛴 이유를 출력한다. 고치기 전 같은 시험이 데이터가
  사라지는 것을 먼저 보여야 한다.
- **회귀 시험 둘**: 사람이 그 경로를 인자로 지정하면 통째로 교체된다. 안전 장치가 지정 경로까지
  막으면 갱신 명령 자체가 성립하지 않는다.
- **회귀 시험 셋**: 템플릿과 똑같은 파일(갓 만든 프로젝트)은 기본 실행에서 그대로 갱신된다.
  판정이 모든 파일을 건너뛰게 만들면 안 된다.
- **회귀 시험 넷**: 빈 표 갈래 문서에서 표 밖 본문 문단이 원형을 유지한다. 지금 뭉개지는 것을
  같은 시험이 먼저 보여야 한다.
- `refresh_guidance.py` 의 도움말이 실제 동작과 같은 말을 한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절 아래에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- DE-00000042 — 판정 규칙과 적용 자리 표. 이 카드가 그 표를 코드로 옮긴다.
- DE-00000029 — 세 갈래를 세운 결정. 이 카드는 첫 갈래만 좁히고 나머지 둘은 안 건드린다.
- O-00000012 — 다른 프로젝트가 데이터를 잃은 관측. 이 카드가 닫히면 그 관측이 닫힌다.
- `stage/scripts/guidance_docs.py:125` `plan_refresh` — 갈래 판정이 서 있는 자리.

## Progress


## Verification


## Retrospective


## Promotion decision
