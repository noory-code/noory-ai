---
id: W-00000111
title: 계층 보관의 인덱스 계약을 한쪽으로 정한다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000125
promotion: not_applicable
review: not_required
scope: stage/skills/stage-archive/, stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000111 계층 보관의 인덱스 계약을 한쪽으로 정한다

## Purpose

계층 보관의 첫 실사용(에픽 W-00000104, 7 레코드)에서 보관 도구와 감사가 인덱스 계약을 서로
다르게 알고 있는 것이 드러났다. 도구는 최상위 행 하나만 적었고, 감사(ARCHIVE001)는 안쪽 스토리
여섯도 각자 행을 요구해 오류 6이 났다. 그 자리에서는 여섯 행을 손으로 채워 넘겼다.

계약을 한쪽으로 정하고 도구·감사·테스트를 그쪽으로 맞춘다. 갈림은 둘이다 — 인덱스가 이동
단위(최상위)만 적는가(계층은 폴더가 쥐므로 SSOT 에 맞음), 레코드 전부를 적는가(찾기가 한 번에
됨). 정하면 반대쪽을 고치고, 손 채움 행들도 계약에 맞게 정리한다.

**2026-07-29 재발.** 에픽 W-00000123(스토리 여섯)을 보관하며 같은 오류 여섯이 다시 났고 다시
손으로 채웠다. 계층 보관을 쓸 때마다 나므로 우연이 아니다. 손 채움 대상은 이제 두 에픽
(W-00000104, W-00000123)의 열두 행이다.


## Actions

- 계약을 한쪽으로 정한다. **이동 단위(최상위)만 적는 쪽을 권한다** — 계층의 진실은 폴더가
  쥔다는 DE-00000035 와 같은 방향이고, 안쪽 행은 폴더를 보면 나오는 것을 베껴 적는 일이다.
  다른 쪽을 고르면 그 근거를 카드에 적는다.
- 정한 쪽으로 보관 도구(`archive_work.py`)와 감사(`audit_stage.py` 의 ARCHIVE001)를 맞춘다.
  지금 둘이 서로 다르게 알고 있어서 계층을 보관할 때마다 오류가 난다.
- 손으로 채운 행들을 계약에 맞게 정리한다. 두 에픽(W-00000104, W-00000123)의 열두 행이다.
- 테스트로 고정한다 — 계층을 보관하면 감사가 오류 0 이다.

## User value

계층을 보관할 때마다 사람이 인덱스 행을 손으로 채우지 않는다. 오늘 두 번 그랬고, 그때마다
보관 직후 감사가 오류 여섯을 냈다.

## Scope

### Included

`stage/skills/stage-archive/` 의 보관 도구, `stage/scripts/audit_stage.py` 의 ARCHIVE001,
그 둘의 테스트, CHANGELOG 미출시 절.

### Excluded

이미 보관된 기록의 본문. 인덱스 행만 정리한다. 매니페스트 버전은 안 건드린다(W-00000124 가
정한 새 규칙).

## Risks

- 최상위만 적는 쪽으로 정하면 ID 로 보관 기록을 찾을 때 폴더를 뒤져야 한다. 감사와 도구가
  이미 폴더를 뒤지므로 사람만 불편해지는데, 인덱스가 최상위 링크를 주므로 한 단계다.

## Success criteria

- 계약이 한쪽으로 정해져 카드에 근거와 함께 적혀 있다.
- 보관 도구와 감사가 같은 계약을 쓴다. 계층(에픽 + 스토리 여럿)을 보관하고 감사하면 오류가
  0 이다. 테스트가 고정한다.
- 두 에픽의 손 채움 행이 계약에 맞게 정리돼 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

- 보관 인덱스는 계층 레코드마다가 아니라 최상위 이동 단위(에픽 또는 독립 스토리)마다 한 행을
  소유한다. 계층 관계의 SSOT는 폴더 배치이고, 하위 행은 같은 사실의 중복이므로 적지 않는다.

## Verification

병합 뒤 본 체크아웃에서 스크립트 스위트 477개 전부 통과, 감사 errors=0 · warnings=0 —
손 채움 열두 행이 걷힌 상태로 깨끗하다. 첫 병렬 실전 카드로 자기 트리에서 돌았고, 드라이버
실패 두 번은 둘 다 카드와 무관했다(1라운드: 물려받은 프로젝트 변수의 오염, 2라운드: 변수가
어떤 값이든 hermetic 테스트를 깨는 것 — 변수 없는 환경 전체 통과를 직접 확인). 상세 처분은
R-00000125.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (193 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785336068
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785336068. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 71.203s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (193 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785336140
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785336140. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 71.170s

OK
```

## Retrospective

[R-00000125](../../retrospectives/R-00000125.md)

## Promotion decision

not_applicable — 플러그인 소스 수정.
