---
id: W-00000136
title: 훅을 띄우는 테스트가 프로젝트 변수를 스스로 걷는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/tests/, stage/scripts/tests/test_schema_v4_consumers.py, stage/scripts/tests/test_migrate_stage_v4.py, stage/scripts/tests/test_migrate_stage_v4_adversarial.py, stage/scripts/tests/test_roadmap_closure_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000136 훅을 띄우는 테스트가 프로젝트 변수를 스스로 걷는다

## Purpose

훅을 스폰하는 테스트들이 세션에 실려 온 CLAUDE_PROJECT_DIR·PROJECT_ROOT·STAGE_WORK_* 변수를 그대로 물려줘서, 에이전트 세션 안에서 손으로 스위트를 돌리면 가짜 실패 8개가 난다(O-00000011). 오늘 리뷰 세 번이 연달아 같은 오염을 만나 각자 원인 추적을 했다. hermetic 은 테스트가 자기 손으로 지킨다 — 훅 스폰 헬퍼 자리에서 변수를 걷고 띄우며, 테스트마다 반복하지 않는다.

## Actions

- 훅 스폰 헬퍼 자리에서 `CLAUDE_PROJECT_DIR`·`PROJECT_ROOT` 와 `STAGE_WORK_*` 류 변수를
  걷고 띄운다. 테스트마다 반복하지 않는다 — 헬퍼가 자리다.
- 오염 상황을 고정하는 테스트를 넣는다.

## Scope

`stage/hooks/tests/` 와 훅을 스폰하는 스크립트 테스트 넷, CHANGELOG 미출시 절. 제품 코드는
안 건드린다 — 훅이 변수를 읽는 우선순위는 호스트 계약이다(W-00000134 가 확정).

## Success criteria

- 두 프로젝트 변수를 엉뚱한 값으로 박아 놓고 훅·스크립트 전체 스위트를 돌려도 전부 통과한다.
  그 상황을 고정하는 테스트가 있다.
- 걷기가 훅 스폰 헬퍼 자리에 있다 — 테스트마다 반복하지 않는다.
- 두 스위트가 통과한다. CHANGELOG 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- [O-00000011](../../state/observations/O-00000011.md) — 이 카드가 닫는 관측
- [R-00000128](../../work/retrospectives/R-00000128.md) — 드라이버 쪽 계약(박기/걷기)의 경위


## Progress


## Verification


## Retrospective


## Promotion decision
