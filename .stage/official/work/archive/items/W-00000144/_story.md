---
id: W-00000144
title: 보관된 v5 카드를 게이트가 다시 열 수 있다
kind: fix
venue: codex
milestone:
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000144
promotion: not_applicable
review: passed
scope: stage/hooks/stage_work.py, stage/hooks/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000144 보관된 v5 카드를 게이트가 다시 열 수 있다

## Purpose

보관된 카드를 고칠 방법이 없다. 보관 게이트가 v5 배치를 못 읽는다.

게이트는 아카이브 인텐트의 대상 경로에서 작업 항목 ID 를 뽑아 인텐트가 지목한 카드와 같은지 본다.
그 ID 를 **파일 이름**에서 뽑는다(`stage/hooks/stage_work.py:431` — `Path(relative).name` 에서
`.md` 를 떼어낸다). v4 는 `items/W-00000130.md` 였으므로 맞았다. v5 는 계층으로 옮기므로
`items/W-00000130/_story.md` 가 되고, 뽑히는 값이 `_story` 라서 **항상 어긋난다.**

`archive_work.py` 는 v5 구조로 정상 보관한다. 즉 **플러그인이 만든 결과물을 플러그인의 게이트가
못 받는다.** novel-workspace 가 감사 오류 한 건을 고치려다 여기 막혔고, 게이트를 우회하는 선례를
만들지 않기로 하고 오류를 남겨 뒀다. 이 저장소도 같은 상태다 — 오늘 보관한 카드들이 모두
`items/<id>/_story.md` 다.

## Actions

- `archive_target_item_id` 가 v5 계층 경로에서 ID 를 뽑게 한다. 인식할 모양:
  `items/<id>/_story.md`, `items/<epic>/<id>/_story.md`(에픽 안 스토리),
  `items/<epic>/<story>/<id>/_story.md`(액션), 그리고 에픽 자신의 `_epic.md`.
  **ID 는 파일 이름이 아니라 그 파일이 든 폴더 이름에서 나온다.**
- v4 경로(`items/<id>.md`)도 계속 인식한다. 아직 v4 인 프로젝트가 있다.
- `archive_target_retro_id` 는 회고가 여전히 `retrospectives/<id>.md` 라 그대로다. 그 사실을
  확인하고 바꿀 것 없음으로 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절에 항목을 더한다. 매니페스트 버전은 안 건드린다.

## Scope

`stage/hooks/stage_work.py`, `stage/hooks/tests/`, `stage/CHANGELOG.md`.

**안 하는 것**: 결정 하나를 카드 여럿이 참조하는 문제(감사 WORK015). 별개 논점이고
W-00000145 로 잡아 뒀다.

## Success criteria

- **회귀 시험**: v5 로 보관된 카드(`items/<id>/_story.md`)에 아카이브 인텐트를 내고 그 파일을
  수정하면 게이트가 통과한다. 고치기 전 같은 시험이 막히는 것을 먼저 보여야 한다.
- **회귀 시험**: 에픽 안에 든 스토리·액션의 보관 경로도 통과한다. 최상위만 되면 계층 보관에서
  다시 막힌다.
- **회귀 시험**: 인텐트가 지목한 것과 **다른** 카드를 고치려 하면 여전히 막힌다. 이 완화가
  게이트를 열어 버리면 안 된다.
- v4 경로도 여전히 통과한다.
- `python3 -m unittest discover -s stage/hooks/tests -q` 와
  `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절 아래에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- 실측 보고: novel-workspace, stage 0.54.4, 2026-07-30. `promote_intent.py --type archive` 로
  인텐트를 냈는데 편집이 "the items/ target filename must match the work_item ID" 로 막혔다.
- `stage/hooks/stage_work.py:423` `archive_target_item_id` — 파일 이름에서 ID 를 뽑는 자리.
- `stage/hooks/stage_runtime.py:444,460` — 그 함수를 불러 인텐트와 대조하는 자리.
- W-00000111 — 계층 보관의 인덱스 계약을 세운 카드. 보관이 계층으로 옮겨진 근거.

## Progress


## Verification


### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.065s

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
[W-00000001] completed on stage/driver/W-00000001-1785394821
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785394821. Human review + merge required; the base branch was not modified.
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
Ran 491 tests in 76.737s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.062s

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
[W-00000001] completed on stage/driver/W-00000001-1785394900
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785394900. Human review + merge required; the base branch was not modified.
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
Ran 491 tests in 77.983s

OK
```

### Independent review at close — 2026-07-30

```
Review report: .stage/.runtime/driver/logs/W-00000144.md
```

## Progress

- codex 실행자가 worktree 에서 구현하고, 인수 검사와 독립 리뷰가 통과했다(기준 6개 전부 PASS,
  `approved: true`).
- 감독자가 병합 전에 실제 보관 트리를 세어 확인했다. **카드에 적은 액션 경로가 틀렸고 코드가
  맞았다** — 액션은 폴더가 아니라 스토리 폴더 안의 낱개 파일(`<epic>/<story>/<action>.md`)이다.

## Verification

- 병합 결과에서 `stage/hooks/tests` 347개, `stage/scripts/tests` 491개 통과. 감사 0/0.

## Retrospective

[R-00000144](../../retrospectives/R-00000144.md) — 플러그인이 자기가 만든 배치를 자기 게이트가 못
받고 있었다.

## Promotion decision

FINAL: not_applicable. stage 플러그인 훅·테스트 변경이고 `.stage/official/` 로 승격할 산출물이
없다.
