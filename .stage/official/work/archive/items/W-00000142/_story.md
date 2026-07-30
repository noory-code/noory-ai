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
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000142
promotion: not_applicable
review: passed
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
[W-00000001] completed on stage/driver/W-00000001-1785394005
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785394005. Human review + merge required; the base branch was not modified.
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
Ran 491 tests in 77.811s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.125s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.070s

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
[W-00000001] completed on stage/driver/W-00000001-1785394084
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785394084. Human review + merge required; the base branch was not modified.
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
Ran 491 tests in 75.351s

OK
```

### Independent review at close — 2026-07-30

```
Review report: .stage/.runtime/driver/logs/W-00000142.md
```

## Progress

- codex 실행자가 worktree 에서 구현하고, 인수 검사와 독립 리뷰가 통과했다(기준 7개 전부 PASS,
  `approved: true`). 감독자가 병합 전에 코드와 시험을 직접 읽고 받았다.
- 병합에서 `stage/CHANGELOG.md` 미출시 절만 부딪혔고 양쪽 항목을 다 살렸다.

## Verification

- 병합 결과에서 `python3 -m unittest discover -s stage/scripts/tests -q` 491개, `-s
  stage/hooks/tests -q` 347개 통과. 감사 0/0.

## Retrospective

[R-00000142](../../retrospectives/R-00000142.md) — 결정이 시험을 미리 써 두니 실행자가 설계를
다시 하지 않았다.

## Promotion decision

FINAL: not_applicable. stage 플러그인 코드·문서·테스트 변경이고 `.stage/official/` 로 승격할
산출물이 없다. DE-00000042 는 W-00000141 이 이미 승격했다.
