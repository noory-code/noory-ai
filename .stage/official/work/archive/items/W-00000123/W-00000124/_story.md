---
id: W-00000124
title: 버전을 카드가 아니라 릴리스가 정한다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000116
promotion: not_applicable
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/CHANGELOG.md, stage/skills/, CLAUDE.md
promotes:
decision_refs:
---

# W-00000124 버전을 카드가 아니라 릴리스가 정한다

## Purpose

DE-00000040 §1. 플러그인 카드가 버전을 올리지 않는다 — CHANGELOG 의 미출시 절에만 적고, 릴리스 명령이 버전을 정해 매니페스트 둘을 고친다. 이것이 병렬을 여는 열쇠다: 두 카드가 같은 다음 버전을 집는 충돌이 사라지고, 무엇보다 도는 동안 버전이 안 바뀌어 마켓플레이스 재당김이 돌던 작업을 죽이는 사고(P-00000001, 오늘 두 번)가 원천 차단된다. CLAUDE.md 의 Plugin Changes 규칙을 같이 고친다 — 사용자 확인 완료(2026-07-29).

## Actions

- 릴리스 명령을 만든다(`stage/scripts/` 아래, 파이썬). 플러그인 이름을 받아 `CHANGELOG.md` 의
  미출시 절을 읽고, 다음 버전을 정해 그 절에 제목을 붙이고, `.claude-plugin/plugin.json` 과
  `.codex-plugin/plugin.json` 의 `version` 을 같은 값으로 고친다.
- 버전 단계는 미출시 절의 내용이 아니라 **인자**로 받는다(patch/minor/major). 산문에서 의도를
  읽어내면 O-00000004 가 보인 함정을 되풀이한다.
- 미출시 절이 비어 있으면 거절한다. 낼 것이 없는데 버전을 올리는 것은 사실이 아니다.
- `stage/CHANGELOG.md` 맨 위에 미출시 절을 만든다. 다른 플러그인의 CHANGELOG 는 이 카드가
  안 건드린다 — 그쪽 작업이 시작될 때 같은 모양으로 연다.
- `CLAUDE.md` 의 Plugin Changes 절을 고친다: 카드는 미출시 절에만 적고, 버전과 매니페스트
  둘은 릴리스 명령이 정한다. 사람 확인 완료(2026-07-29, DE-00000040).
- 테스트를 쓴다.

## User value

두 작업이 동시에 돌아도 같은 다음 버전을 집어 부딪히지 않는다. 무엇보다 **도는 동안 버전이
안 바뀌므로**, 마켓플레이스가 다시 당기면서 옛 캐시 폴더가 사라져 돌던 작업이 죽는 사고가
없어진다 — 오늘 두 번 겪고 카드 시도 하나를 날린 그 사고다.

## Scope

### Included


### Excluded


## Risks

- 지금 매니페스트 버전(0.54.4)과 CHANGELOG 의 마지막 절이 어긋나면 다음 릴리스가 엉뚱한
  버전을 낸다. 명령이 매니페스트의 현재 값을 기준으로 다음을 정하고, CHANGELOG 의 마지막
  출시 절과 다르면 거절한다.
- 규칙을 바꾸는 동안 다른 창이 옛 규칙대로 버전을 올릴 수 있다. `CLAUDE.md` 수정이 같은
  커밋에 들어가야 두 진실이 공존하는 창이 안 생긴다.

## Success criteria

- 릴리스 명령이 미출시 절에 제목을 붙이고 매니페스트 둘을 같은 값으로 고친다. 그 동작을
  고정하는 테스트가 있다.
- 미출시 절이 비면 거절하고, 매니페스트와 CHANGELOG 의 현재 버전이 어긋나도 거절한다. 두
  거절을 각각 고정하는 테스트가 있다.
- 버전 단계를 인자로 받는다 — 산문에서 추측하지 않는다.
- `stage/CHANGELOG.md` 에 미출시 절이 서 있고, 그 위에 이 카드의 항목이 적혀 있다.
- `CLAUDE.md` 의 Plugin Changes 절이 새 규칙을 말한다 — 카드는 미출시 절에만 적고 버전은
  릴리스가 정한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.

## Next action

끝나면 사람이 `stage` 외 다섯 플러그인의 CHANGELOG 를 언제 같은 모양으로 열지 정한다. 지금
여는 것은 쓰지 않는 문서를 미리 고치는 일이라 이 카드가 안 한다.

## Progress

드라이버 감독 실행 한 바퀴, 2026-07-29. 기준 여섯 전부 PASS, 리뷰 APPROVED. 매니페스트는
0.54.4 에 그대로 두고 미출시 절만 열었다 — 이 카드가 세운 규칙을 이 카드부터 지킨다.

드라이버는 실패로 판정했다. 판정 내용이 아니라 판정을 읽는 방식 때문이다(아래).

## Verification

인수 검사 통과 — 스크립트 426개. 리뷰 판정: 기준 여섯 전부 PASS, APPROVED.

### 드라이버가 실패로 판정한 이유

O-00000004 의 여섯 번째다. 리뷰어가 마지막 줄에서 "판정은 `### Reviewer report` 에 이미
붙였고 실제 파서로 통과를 확인했다"고 적었다. **파서로 확인까지 하고**, 그 사실을 설명하며
절 이름을 입에 담아 걸렸다.

**받지 않는다 — 일은 통과했다.** 이 사례가 W-00000117 의 여섯째 근거다. 리뷰어가 자기 판정을
검증해도 그 검증을 말하는 순간 깨진다면, 고칠 것은 리뷰어가 아니라 읽는 방식이다.

### 리뷰 지적 처분 (기준 밖 셋)

- **새 규칙이 evonest 의 불변식을 깬다 — 받는다, W-00000127 로.** 확인했다.
  `evonest/CLAUDE.md:36-44` 는 `pyproject.toml` 을 버전의 유일한 자리로 두고 매니페스트가
  거기 맞춰야 한다고 못박는데, 새 명령은 매니페스트만 고친다. 그런데 루트 규칙
  (`CLAUDE.md:105`)은 여섯 플러그인 전부에 쓰라고 한다. **지금 이 순간 틀린 지시가 서 있다** —
  다음 사람이 evonest 에서 그대로 따르면 버전의 진실이 둘로 갈린다. 급하다.
- **릴리스 뒤 미출시 절을 다시 여는 주체가 없다 — 받는다, 같은 카드로.** 두 번 연속 돌리면
  "found 0" 으로 멈춘다. 막히는 방향이라 안전하지만, 누가 절을 다시 여는지 규칙이 안 말한다.
- **`stage-handoff/SKILL.md:76` 의 "every change ships a version bump" 이 이제 거짓 —
  받는다, 같은 카드로.** 이 카드가 만든 낡은 문장이다. scope 안이었는데 어느 기준도 이 파일을
  안 지목해서 실행자가 못 봤다 — 내가 기준을 좁게 썼다.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785309758 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785309758
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785309758. Human review + merge required; the base branch was not modified.
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
Ran 426 tests in 57.953s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785309816 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785309816
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785309816. Human review + merge required; the base branch was not modified.
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
Ran 426 tests in 57.704s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000116](../../../retrospectives/R-00000116.md)

## Promotion decision

not_applicable — 플러그인 소스와 저장소 규칙 수정이고 `.stage/official/` 로 올릴 것이 없다.
