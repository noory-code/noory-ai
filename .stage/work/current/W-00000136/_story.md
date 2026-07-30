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
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000135
promotion: not_applicable
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

병렬 2차 페어로 자기 트리에서 실행, 2026-07-30. 실행자(codex)는 한 바퀴에 완성 — O-00000011
이 원인·재현·방향을 쥐고 있어 조사 없이 구현으로 직행했다.

## Verification

스텝의 리뷰어(claude)가 세션 한도로 못 떠서 — 인프라 실패, 시도 안 깎임 — 감독자가 headline
기준을 그대로 실행해 검증하고 수동으로 닫는다: 오염 변수 셋(`CLAUDE_PROJECT_DIR`·
`PROJECT_ROOT`·`STAGE_WORK_ITEM_PATH`)을 박은 채 스크립트 483(병합 후 484)·훅 345 전부 통과.
걷는 자리가 헬퍼 하나임을 diff 로 확인. **독립 LLM 리뷰는 없었다** — 사실로 남긴다.

### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (197 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785374633
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785374633. Human review + merge required; the base branch was not modified.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 484 tests in 68.478s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 345 tests in 1.000s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 345 tests in 0.997s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000135](../../retrospectives/R-00000135.md)

## Promotion decision

not_applicable — 플러그인 테스트 수정.
