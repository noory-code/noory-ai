---
id: W-00000127
title: 새 버전 규칙이 여섯 플러그인 전부에서 참이 되게 한다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000117
promotion: not_applicable
review: not_required
scope: CLAUDE.md, stage/scripts/release_plugin.py, stage/scripts/tests/, stage/skills/stage-handoff/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000127 새 버전 규칙이 여섯 플러그인 전부에서 참이 되게 한다

## Purpose

W-00000124 가 세운 릴리스 시점 버전 규칙이 지금 세 자리에서 어긋난다. 첫째가 급하다 — 루트 CLAUDE.md 는 여섯 플러그인 전부에 릴리스 명령을 쓰라고 하는데, evonest 는 pyproject.toml 을 버전의 유일한 자리로 선언했고(evonest/CLAUDE.md:36-44) 명령은 매니페스트만 고친다. 지금 그대로 따르면 버전의 진실이 둘로 갈린다. 명령이 pyproject 를 함께 보게 하거나 규칙이 적용 대상을 밝히거나 둘 중 하나. 둘째, 릴리스 뒤 미출시 절을 누가 다시 여는지 규칙이 안 말한다(두 번 연속 돌리면 멈춘다). 셋째, stage-handoff/SKILL.md:76 의 'every change ships a version bump' 이 이제 거짓이다.

## Actions

- **여섯 플러그인의 버전 자리를 먼저 센다.** `evonest/`, `rag/`, `stage/`, `plainly/`,
  `flutter-cask/`, `pencil_m3_flutter/` 각각에서 버전이 어디에 적히는지(매니페스트 둘,
  `pyproject.toml`, `pubspec.yaml` 등) 확인하고, 하위 `CLAUDE.md`·`AGENTS.md` 가 그 주제를
  이미 정했는지 본다. 센 결과를 작업 로그에 적는다.
- 그 셈을 근거로 정한다: 릴리스 명령이 플러그인마다 다른 버전 자리를 함께 옮기게 하거나,
  루트 규칙이 적용 대상을 밝히거나. **어느 쪽이든 지금처럼 "여섯 전부에 쓰라"고 두지
  않는다** — 지금 그 지시를 따르면 evonest 의 버전 진실이 둘로 갈린다.
- 릴리스 뒤 미출시 절을 누가 다시 여는지 정하고 그대로 만든다. 명령이 직접 열든, 규칙이
  다음 카드에게 맡기든 한쪽으로 정한다.
- `stage/skills/stage-handoff/SKILL.md:76` 의 "every change ships a version bump" 을 새 규칙에
  맞게 고친다.
- 매니페스트를 다시 쓸 때 기존 들여쓰기를 보존한다 — 지금은 통째로 다시 써서 정규화된다.

## Scope

`CLAUDE.md`(루트 규칙), `stage/scripts/release_plugin.py` 와 그 테스트,
`stage/skills/stage-handoff/SKILL.md`, `stage/CHANGELOG.md` 의 미출시 절.

**안 하는 것**: `evonest/CLAUDE.md` 를 고치는 일. 그 문서는 evonest 가 자기 버전 규칙을 정한
자리이고, 루트가 하위 규칙을 덮어쓰는 것이 아니라 루트가 하위를 인정해야 한다.

## Success criteria

- 여섯 플러그인의 버전 자리와 그것을 정한 하위 규칙이 세어져 작업 로그에 적혀 있다.
- 루트 `CLAUDE.md` 의 Plugin Changes 절이 그 셈과 어긋나지 않는다 — evonest 처럼 자기 버전
  규칙을 가진 플러그인에서 그대로 따라도 진실이 갈리지 않는다.
- 릴리스를 두 번 연속 돌려도 두 번째가 정상 동작한다(미출시 절이 다시 열려 있다). 또는
  규칙이 누가 여는지 명시하고 그 지시가 실제 절차와 맞는다. 어느 쪽이든 테스트가 고정한다.
- `stage/skills/stage-handoff/SKILL.md` 에 버전 올림을 매 변경의 전제로 말하는 문장이 없다.
- 릴리스 명령이 매니페스트의 기존 들여쓰기를 바꾸지 않는다. 테스트가 고정한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- 이 카드의 항목이 `stage/CHANGELOG.md` 의 미출시 절에 적혀 있다. **매니페스트 버전은 안
  건드린다** — 새 규칙이 그렇게 정했다.

## Related truth

- [DE-00000040](../../../official/decisions/records/DE-00000040.md) — 버전 규칙의 소유자
- [R-00000116](../../../work/retrospectives/R-00000116.md) — 이 어긋남이 생긴 경위
- `evonest/CLAUDE.md:36-50` — evonest 가 선언한 버전 SSOT

## Next action

`release_plugin.py` 를 다음에 만지는 사람이 볼 것: 줄바꿈 판별 갈래(`release_plugin.py:168`
부근)가 죽어 있다. 파일을 읽을 때 이미 `\n` 으로 바뀌므로 CRLF 갈래를 못 탄다. Windows 에서
CRLF 체크아웃을 릴리스하면 전체가 LF 로 바뀐다. 지금은 닿을 길이 없어 안 고쳤다.


## Progress

드라이버 감독 실행 한 바퀴, 2026-07-29. **드라이버 판정까지 통과했다** — 오늘 처음이다.
기준 일곱 전부 PASS, 리뷰 APPROVED, 스크립트 테스트 428개 OK.

## Verification

인수 검사 통과 — 스크립트 428개. 리뷰 판정: 기준 일곱 전부 PASS, APPROVED. 드라이버도
통과로 판정했다.

### 여섯 플러그인의 버전 자리 (셈 결과)

| 플러그인 | 버전의 자리 | 릴리스 방법 |
|---|---|---|
| `evonest/` | `pyproject.toml` (자기 CLAUDE.md 가 SSOT 로 선언) | 공용 명령 안 씀. 매니페스트 둘 + `uv.lock` 을 함께 옮긴다 |
| `rag/` | `server/pyproject.toml` + `uv.lock` | 공용 명령 안 씀. `rag/server/` 에서 `uv lock` 을 돌린다 |
| `stage/`, `plainly/`, `flutter-cask/` | 매니페스트 둘 | 공용 명령 |
| `pencil_m3_flutter/` | 매니페스트 둘 + Dart `pubspec.yaml` | 호스트 플러그인은 공용 명령. Dart 쪽은 별도 흐름 |

리뷰어가 공용 명령으로 보낸 넷의 최신 릴리스 제목이 실제로 명령의 파서에 걸리는지까지
확인했다 — 규칙이 가리키는 명령이 그 자리에서 실제로 돈다.

### 리뷰 지적 처분 (기준 밖 둘)

- **CRLF 분기가 죽은 코드다 — 안 받는다, 다만 자리를 남긴다.** 파일을 읽을 때 이미 `\n` 으로
  바뀌므로 `\r\n` 갈래를 못 탄다. 결과적으로 Windows 에서 CRLF 로 체크아웃한 파일을 릴리스
  하면 전체가 LF 로 바뀐다. 이 저장소 파일은 전부 LF 이고 지금 작업자는 macOS 하나라 닿을
  길이 없다. 조용히 망가지는 것이 아니라 커밋 diff 로 바로 보이므로 겪은 뒤에 고친다(AHA).
  아래 Next action 에 자리를 적어 다음 사람이 찾게 한다.
- **릴리스 기록이 하나도 없는 플러그인은 공용 명령이 못 돈다 — 안 받는다.** 미출시 절 아래에
  기존 릴리스 제목이 없으면 멈춘다. 여섯 플러그인 전부 기존 릴리스가 있으므로 새 플러그인을
  만들 때나 닿는다. 막히는 방향이고 메시지가 이유를 말한다.


### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785311104 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785311104
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785311104. Human review + merge required; the base branch was not modified.
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
Ran 428 tests in 58.000s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785311162 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785311162
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785311162. Human review + merge required; the base branch was not modified.
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
Ran 428 tests in 57.679s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000117](../../../retrospectives/R-00000117.md)

## Promotion decision

not_applicable — 플러그인 소스와 저장소 규칙 수정이고 `.stage/official/` 로 올릴 것이 없다.
