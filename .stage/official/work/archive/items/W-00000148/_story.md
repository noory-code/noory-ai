---
id: W-00000148
title: 두 번째 바퀴의 리뷰를 좁힌 범위로 돌린다
kind: fix
venue: codex
milestone:
priority: 1
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000148
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/templates/, stage/docs/, stage/CHANGELOG.md, .stage/settings.json
promotes:
decision_refs:
---

# W-00000148 두 번째 바퀴의 리뷰를 좁힌 범위로 돌린다

## Purpose

W-00000146 이 정할 결정을 코드로 옮긴다. 두 번째 바퀴부터 리뷰가 지난 판정에서 통과한 기준을
이어받고, 다시 보는 것은 지난 판정에서 어긋난 기준과 그 사이 바뀐 구간으로 좁힌다.

**W-00000149 와 같은 설정 항목을 건드린다** — `.stage/settings.json` 의 `review.reviewers` 두 벌과
`review.strengths` 네 벌, 템플릿의 `settings.jsonc`, `drive.py` 의 리뷰 단계. 두 카드를 따로 돌리면
같은 줄을 두 번 고치고 두 번째가 첫 번째를 덮을 위험이 있다. **한 바퀴에 같이 돌리는 것이 기본이고,
따로 돌릴 이유가 생기면 그때 순서를 정한다.**

시작 전 조건: W-00000146 의 결정이 `decided` 여야 한다. 결정 없이 시작하면 실행자가 판정 파일의
모양을 스스로 정한다.


## Actions

DE-00000043 이 규칙을 정했다. **설계를 다시 하지 말고 그 결정을 읽고 옮긴다.**

- `drive.py` 의 리뷰 단계가 **지난 판정 파일이 읽히는지** 본다. 읽히면 좁힌 재리뷰로, 없으면 지금처럼
  전체 리뷰로 간다. 시도 계수로 가르지 않는다 — DE-00000039 가 인프라 실패에서 시도를 안 깎기로
  정했으므로 계수는 "리뷰가 몇 번 돌았나"와 어긋난다.
- 좁힌 재리뷰에 넘기는 것: 지난 판정에서 `FAIL` 인 기준 목록과, 지난 판정 뒤에 바뀐 경로.
- 재리뷰 프롬프트를 `.stage/settings.json` 의 `review.reviewers` **두 벌**과 `review.strengths`
  **네 벌**에 넣는다. **한쪽만 고치면 실행 surface 마다 계약이 갈린다.**
- 판정 파일 계약은 유지한다: `criteria` 가 모든 기준을 담고 `approved` 는 전부 통과일 때만 참.
  이어받은 기준은 지난 `verdict` 와 `reason` 을 옮기되 **이번 바퀴에 본 것이 아님이 파일에서
  읽혀야 한다.** 필드 이름은 구현이 고른다.
- 템플릿 `settings.jsonc` 에 같은 내용을 반영한다.
- `stage/docs/` 의 드라이버 절에 두 바퀴의 차이를 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절에 항목을 더한다. **매니페스트 버전은 안 건드린다.**

## User value

카드가 두 번째 바퀴를 돌 때 리뷰어가 처음부터 전부 다시 읽지 않는다. 리뷰어 입력이 340만 토큰까지
간 적이 있고(Q-00000001), claude venue 리뷰어가 900초를 넘긴 적이 있다(R-00000127).

## Scope

### Included

`stage/scripts/drive.py`, `stage/scripts/tests/`, `stage/templates/`, `stage/docs/`,
`stage/CHANGELOG.md`, `.stage/settings.json`.

### Excluded

- **닫기의 구현 단계 리뷰는 안 좁힌다.** 최종 코드를 한 번은 전체가 본다 — DE-00000043 이 그것을
  안전망으로 지정했다.
- **인수 검사도 안 좁힌다.** 매 바퀴 전부 돈다.
- 모델을 명령에 못 박는 일(DE-00000044)은 W-00000149 몫이다. 같은 설정 항목을 건드리므로 이 카드가
  닫힌 뒤에 이어서 돈다.

## Risks

이어받은 통과가 거짓이 되는 것. 고침이 통과했던 기준을 깨뜨리는 경우다. 세 겹으로 막혀 있다 —
인수 검사가 매 바퀴 돌고, 재리뷰가 바뀐 구간의 새 파손을 찾고, 닫기의 전체 리뷰가 최종 코드를 본다.
**구현이 그 세 겹 중 하나라도 무력화하면 이 카드는 목적을 못 세운다.**

## Success criteria

- **회귀 시험**: 지난 판정 파일이 있고 그 안에 `FAIL` 기준이 있을 때, 재리뷰가 그 기준만 다시
  판정한다. 통과했던 기준이 다시 판정 대상에 안 들어간다.
- **회귀 시험**: 판정 파일이 없으면(첫 바퀴이거나 지난 바퀴가 판정을 못 남겼을 때) 전부 다시 본다.
  이것이 fail-safe 방향이다.
- **회귀 시험**: 두 번째 바퀴의 판정 파일이 **모든 기준**을 담고 `approved` 가 전부 통과일 때만
  참이다. 이어받은 기준이 빠지면 안 된다.
- **회귀 시험**: 이어받은 기준이 "이번 바퀴에 본 것이 아님"으로 구분된다. 파일만 읽고 알 수 있다.
- `.stage/settings.json` 의 `review.reviewers` 두 벌과 `review.strengths` 네 벌이 **모두** 같은
  계약을 담는다. 한 벌이라도 빠지면 실패다.
- 템플릿 `settings.jsonc` 가 같은 내용을 담는다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절 아래에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

codex 실행자가 worktree 에서 구현했다. 첫 시도가 900초 제한에 잘렸는데 일은 그 안에 끝나 있었고,
45분으로 다시 건 시도는 바꿀 것이 없어 끝났다. 드라이버가 그 상태를 알아보고 사람이 직접 닫으라고
안내했다.

## Verification

- 병합 결과에서 `stage/scripts/tests` 493개, `stage/hooks/tests` 347개 통과.
- 좁힌 재리뷰 계약이 리뷰어 두 벌과 강도 네 벌 **여섯 자리 모두**에 들어갔다. 템플릿과 문서도 같다.
- 판정 파일이 기준마다 몇 번째 바퀴에 판정됐는지 담고, 통과 표시는 모든 기준이 통과할 때만 참으로
  검사한다(`drive.py` 의 판정 읽기·병합 자리).
- 읽을 판정 파일이 없으면 전부 다시 본다.

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
[W-00000001] completed on stage/driver/W-00000001-1785398552
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785398552. Human review + merge required; the base branch was not modified.
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
Ran 493 tests in 74.935s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.064s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.073s

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
[W-00000001] completed on stage/driver/W-00000001-1785398630
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785398630. Human review + merge required; the base branch was not modified.
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
Ran 493 tests in 73.843s

OK
```

## Retrospective

[R-00000148](../../retrospectives/R-00000148.md) — 결정이 시험까지 정해 두면 실행자가 헤매지 않는다.

## Promotion decision

FINAL: not_applicable. 플러그인 코드·설정·문서 변경이고 승격할 산출물이 없다.
