---
id: W-00000140
title: v4 프로젝트가 자기 기존 결함 때문에 v5 마이그레이션에 막히지 않는다
kind: fix
venue: codex
milestone:
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000140
promotion: not_applicable
review: passed
scope: stage/scripts/migrate_stage.py, stage/scripts/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000140 v4 프로젝트가 자기 기존 결함 때문에 v5 마이그레이션에 막히지 않는다

## Purpose

v4 프로젝트가 v5 로 넘어갈 때, 마이그레이션이 만들지도 않은 자기 기존 결함 때문에 막힌다.

마이그레이션은 "내가 새로 만든 결함만 막는다"는 계약을 갖고, 그것을 이동 전 감사 결과를
기준선으로 삼아 판정한다(`migrate_stage.py:526` — `strict_audit_findings` 를 이동 전에 부른다).
그런데 **기준선을 찍는 감사기는 v5 감사기**다. v5 감사기는 납작한 `items/W-xxx.md` 를 작업
항목으로 인식하지 않으므로, 카드마다 나오는 결함(예: `kind` 기준이 `operations/verification.md`
에 없다는 경고)을 기준선에서 아예 못 본다. 카드가 `W-xxx/_story.md` 로 옮겨진 뒤에야 보이니
전부 "마이그레이션이 새로 만든 것"으로 판정된다.

novel-workspace 가 stage 0.54.4 에서 실제로 막혔다. 이월로 인정된 것은 경로가 안 바뀌는
`GOV002` 한 건뿐이었고, 그 프로젝트는 kind 기준 네 줄을 손으로 추가해 우회한 뒤 마이그레이션을
마쳤다. **우회를 아는 사람만 넘어간다** — 다른 v4 프로젝트는 같은 자리에 갇힌다.

## Actions

- 기준선을 찍는 시점을 옮긴다: **카드를 v5 배치로 이동한 직후, 스탬프 전.** 그 시점의 트리는
  v5 감사기가 읽을 수 있으므로 기존 빚이 기준선에 정상적으로 들어온다.
- 비차단 코드 목록(KIND001 등을 예외로 나열하는 방식)은 **쓰지 않는다.** 코드마다 사람이
  판단해서 유지해야 하는 목록이 하나 더 생기고, 마이그레이션이 진짜로 만든 결함이 그 목록에
  섞이면 조용히 통과한다.
- 이월된 빚을 지금처럼 보고에 남긴다. 판정에서 빼는 것이지 숨기는 것이 아니다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절에 항목을 더한다. **매니페스트 버전은 안 건드린다.**

## Scope

`stage/scripts/migrate_stage.py`, `stage/scripts/tests/`, `stage/CHANGELOG.md`.

**안 하는 것**: v5 감사기가 납작한 카드를 읽게 만드는 일. v4 배치를 v5 감사기가 이해하게 하는
것은 마이그레이션이 없애려는 배치를 되살리는 일이다. 이 카드는 판정 시점만 고친다.

## Success criteria

- **회귀 시험 하나**: 납작한 v4 카드가 있고 그 카드의 `kind` 기준이
  `operations/verification.md` 에 없는 프로젝트를 만들어 v5 마이그레이션을 돌리면 통과한다.
  지금 코드에서는 막히는 것을 같은 시험이 먼저 보여야 한다(고치기 전 실패 확인).
- **회귀 시험 둘**: 마이그레이션이 새로 만든 결함(예: 링크가 깨진 상태로 옮겨진 기록)은 여전히
  막는다. 앞의 완화가 이 시험을 통과시키면 안 된다.
- 이월된 빚이 보고 출력에 그대로 나온다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절 아래에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- 실측 보고: novel-workspace, stage 0.54.4, 2026-07-30. 이월 인정 1건(`GOV002`), 우회는
  `operations/verification.md` 에 kind 기준 4종(feature·bug·refactor·docs) 손 추가.
- `stage/scripts/migrate_stage.py:526` — 기준선을 이동 전에 찍는 자리.
- `stage/scripts/migrate_stage.py:369` `post_migration_audit_findings` — 기준선과 대조해
  introduced 를 가리는 자리.
- DE-00000011 — 마이그레이션은 사용자 대면 스킬이고 어떤 버전도 v3 사용자를 갇히게 하지 않는다.
  이 카드는 그 결정이 v4→v5 에서 깨진 자리를 고친다.

## Progress

- codex 실행자가 기준선 채취 시점을 카드 지시대로 옮겼다. `migrate_to_v5` 가 baseline 인자를
  받는 대신 스스로 모으고, `relocate_work_records` 직후에 v5 감사기로 기준선을 찍는다.
  회귀 시험 둘을 `test_schema_v5_migration.py` 에 세웠다.
- **드라이버는 이 시도를 실패로 판정했다. 일의 실패가 아니다.** 드라이버가 관찰한 변경 목록에
  감독자가 같은 체크아웃에서 그 사이에 커밋한 `.stage` 기록 17개가 섞였다(실행자 주장 3개 대
  관찰 20개). 원인은 O-00000013 에 남겼다.
- 따라서 검증은 감독자가 직접 돌렸다. 아래 기록이 그것이다.

## Verification


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
[W-00000001] completed on stage/driver/W-00000001-1785388454
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785388454. Human review + merge required; the base branch was not modified.
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
Ran 486 tests in 77.199s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 345 tests in 1.104s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 345 tests in 1.113s

OK

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
[W-00000001] completed on stage/driver/W-00000001-1785388539
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785388539. Human review + merge required; the base branch was not modified.
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
Ran 486 tests in 81.688s

OK
```

### Independent review at close — 2026-07-30

```
Review report: .stage/.runtime/driver/logs/W-00000140.md
```

## Retrospective

[R-00000140](../../retrospectives/R-00000140.md) — 기준선을 언제 찍느냐가 마이그레이션의 통과
여부를 정했다.

## Promotion decision

FINAL: not_applicable. stage 플러그인 코드·테스트·CHANGELOG 변경이고 `.stage/official/` 로
승격할 산출물이 없다.
