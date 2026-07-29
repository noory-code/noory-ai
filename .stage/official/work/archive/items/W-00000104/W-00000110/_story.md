---
id: W-00000110
title: 카드 백 장을 v5 로 옮긴다
kind: development
venue: codex
priority: 6
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000107
promotion: not_applicable
review: not_required
scope: stage/, .stage/
promotes:
decision_refs:
---

# W-00000110 카드 백 장을 v5 로 옮긴다

## Purpose

옛 카드와 새 폴더가 같은 스캐너 안에서 같이 살 수 없다. 카드를 훑는 코드가 하나이기 때문이다.
그래서 스키마를 v5 로 올리고 보관된 카드 백여 장과 진행 중·계획 카드를 전부 새 모양으로 옮긴다.
스캐너는 새 모양 하나만 안다.

## Source

DE-00000035 — v5 로 올리고 전부 옮긴다. 스캐너에 분기를 남기지 않는다.

## User value

옛 카드도 새 구조 안에서 읽힌다. 그리고 이후의 모든 변경이 한 모양만 맞추면 된다.

## Scope

### Included

- v4 → v5 마이그레이션 스크립트. v3 → v4 때 쓴 `stage_schema_v4_migration.py` 와
  `stage-migrate` 스킬이 이미 그 자리를 닦아 놨으므로 같은 자리를 따른다.
- 옛 카드는 **독립 스토리**로 옮긴다. 보관된 카드 하나하나에 에픽을 지어 붙이는 것은 사실을
  지어내는 것이므로 안 한다. 이미 `parent` 를 가진 카드는 그 부모의 폴더 밑으로 들어간다.
- 이 저장소(`.stage/`)의 카드를 실제로 옮긴다.
- `docs/SCHEMA_V5.md`, `README.md`, `CHANGELOG.md`.

### Excluded

없다. 이 카드가 이 에픽의 마지막이다.

## Dependencies

W-00000106 (새 모양이 있어야 옮길 곳이 있다), W-00000109 (계층 위를 도는 것들이 맞아야 옮긴 뒤
감사가 통과한다).

W-00000106 이 끝나면 코드는 새 구조를 알지만 저장소의 카드는 옛 모양이다. 그 사이가 길면
저장소가 깨진 채로 있게 된다. 106 과 이 카드를 붙여서 한 덩어리로 내보내야 할 수도 있다 —
106 을 할 때 그 판단을 한다.

## Risks

- 마이그레이션이 중간에 끊기면 어떻게 되나. v3 → v4 스크립트가 이 자리를 어떻게 다뤘는지
  확인하고 같은 자리를 따른다. **확인 전에는 안전하다고 적지 않는다.**
- 보관된 카드는 이미 official 이다. 옮기려면 승격 의도(`promote_intent.py`)를 거쳐야 한다.
  카드 백 장에 대해 그것이 어떻게 도는지 미리 확인한다.

## Success criteria

- v4 → v5 마이그레이션이 있고, 중단됐을 때의 동작이 v3 → v4 와 같은 자리를 따른다.
- 이 저장소의 카드가 전부 새 모양이고, 스캐너에 v4 분기가 남지 않았다.
- 옛 카드가 독립 스토리로 있고, `parent` 를 갖던 카드는 부모 폴더 밑에 있다.
- 은퇴한 B 카드를 훑는 자리(`migrate_stage.py:232` 의 `glob("B-*.md")`)가 새 구조에서 어떻게
  되는지 한 번 보고 정한다. 작업 카드는 아니지만 레코드 성격이 있다.
- 인덱스 링크가 카드의 실제 위치를 가리킨다. 지금 경로를 만드는 함수가 루트의 절대·상대 여부로
  갈려서, 실제 카드는 찾아서 얻고 인덱스 링크는 평평하게 조립한다. 카드가 중첩 폴더로 가면 둘이
  어긋난다 (`close_work.py:115`/`:119`, `:483`/`:487`, `start_work.py:155`/`:250`,
  `archive_work.py:169`/`:257`).
- 옛 스키마에서 올라온 프로젝트가 `parent:` 없는 카드로 착지한다. 지금 v3 마이그레이션이 그
  필드를 써 넣는다 (`test_work_cards.py:340` 이 그대로 단언한다).
- 이 저장소의 감사 경고가 0 이다. 지금 12개가 난다 — `_epic.md`·`_story.md` 가 안 깔려서 6개,
  `README.md`·`_template.md` 가 옛 내용이라 6개.
- 보관함이 백 장을 넘은 상태에서 보관·닫기가 느려지지 않는다. 카드를 찾을 때마다 트리를 다시
  훑고 `archive_work.py:136` 이 루프 안에서 부른다. 옮긴 뒤 재어 보고 정한다.
- 두 테스트 모음 통과, 감사 errors=0, 플러그인 버전 + CHANGELOG.

다음 셋은 novel-workspace 가 v4 프로젝트에서 마이그레이션을 실전 실행하고 보낸 결함 보고에서
왔다 (2026-07-29). 셋 다 v3→v4 장치에서 물려받은 실패 경로이고, 보고자가 재현 시나리오를
회귀 시험으로 흡수해 달라고 부탁했다.

- **기존 빚은 마이그레이션을 못 막는다.** 사후 감사가 시작 전 기준선에 없던 **새 결함만** 실패로
  친다. 기존 경고(예: 옛 kind 의 KIND001 83건)는 통과시키고 목록으로 보고한다. 지금은 기준선
  개념이 없어서, 경고를 고치려면 마이그레이션이 필요하고 마이그레이션은 그 고침을 요구하는
  막다른 골목이 생긴다. 재현: 기존 KIND001 경고를 가진 v4 프로젝트가 v5 로 건너간다.
- **abort 가 옛 일지에 안 속는다.** 일지가 자기 마이그레이션과 짝이 맞을 때만 abort 대상이고,
  옛 일지(v3→v4 잔재)는 "무시함"으로 보고하며, 성공적으로 끝난 마이그레이션은 일지를 정리한다.
  novel-workspace 에서 옛 일지의 HEAD 와 비교한 오탐으로 "커밋됐으니 git revert 하라"는 거짓
  안내가 나왔다 — 믿고 따르면 사고다. 재현: 옛 v4 일지가 남은 프로젝트에서 v5 abort.
- **유지보수 표식의 잠금이 그 프로젝트에만 미친다.** 지금 가드는 표식이 있으면 대상 경로와
  무관하게 모든 쓰기를 막아서(스크래치패드·다른 저장소 포함), 마이그레이션이 실패로 멈춘
  상태에서는 복구 시도조차 막힌다. 잠금 범위를 governed 경로 + `.stage` 로 좁히고 스킬 문서에
  명시한다.

## Next action

`stage_schema_v4_migration.py` 가 중단 처리를 어떻게 했는지 읽는다.

## Progress

스키마가 v5 가 됐고 이 저장소의 기록 110장이 전부 새 모양으로 옮겨졌다. 옛 카드는 독립 스토리
폴더로, 열려 있는 에픽 밑으로 완료된 자식 여섯이 다시 모였다. 스캐너는 한 모양만 알고,
마이그레이션은 일지를 남기는 가역 방식이다. 감사가 처음으로 오류 0 · 경고 0.

도중에 novel-workspace 가 v4 프로젝트에서 마이그레이션을 실전 실행하고 결함 셋(기존 빚에 갇힘,
옛 일지가 abort 를 속임, 실패 표식이 전부 잠금)을 보고했다. 셋 다 기준으로 올려 이 카드에서
닫았고 재현이 회귀 시험으로 들어갔다. 플러그인 0.54.1.

드라이버 세 회차. 1회차는 45분 제한 초과(일은 완성, O-00000003 재발), 2회차는 실행자의 설치
플러그인(0.53.0, v4 강제)이 v5 가 된 이 저장소의 쓰기를 전부 막아 정직하게 멈춤 — P-00000001
계열의 새 얼굴이다. 선례대로 코덱스 쪽 플러그인을 한 회차 끄고 3회차에 통과, 직후 다시 켰다.

## Verification

실행자 codex, 리뷰어 claude (venue 가 서로 다름).

- `python3 -m unittest discover -s stage/hooks/tests -q` — 342개 통과.
- `python3 -m unittest discover -s stage/scripts/tests -q` — 416개 통과.
- `python3 stage/scripts/audit_stage.py --project-root .` — errors=0, **warnings=0**.

리뷰가 기준 12개 전부 PASS + APPROVED. 리뷰어가 직접 재측정한 것 둘 — 보관함 101장 전체 스캔
1회 3.3ms(성능 기준), 표식 잠금이 스키마 3/4/5 전부에서 governed·`.stage` 만 거부하고 다른
저장소는 허용.

### 기준 밖 지적의 처리

- **감사 기준선이 메시지 문자열에 기대서, 경로가 메시지에 박히는 결함은 이동 후 "새 결함"으로
  오인될 수 있다** — **미룸 → O-00000008.** 알려진 실전 사례(KIND001)는 메시지에 경로가 없어
  안전하지만, 잠복 경계라 관측으로 남긴다.
- **abort 가 무관한 일지만 무시하고 아무것도 복원 안 했을 때도 exit 0** — **안 받음.** 아무것도
  할 일이 없던 abort 가 성공으로 끝나는 것은 멱등의 자연스러운 뜻이고, 그 exit 코드를 "복원됨"
  으로 읽는 자동화가 이 저장소에 없다.
- **abort 도중 스냅샷 항목 하나가 깨지면 반쯤 지운 트리에서 물러날 길이 없다** — **안 받음.**
  일지는 자기 자신이 기록한 값이라 확률이 낮고, `.stage` 는 git 이 추적하므로 최악에도 checkout
  으로 돌아온다.
- **인라인 인터프리터 쓰기를 별도 게이트가 막는 것 확인** — 결함 아님, 확인 사실.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 342 tests in 0.951s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (118 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785286011 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785286011. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785286012 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785286012
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785286012. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785286013 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785286013. Human review + merge required; the base branch was not modified.
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
Ran 416 tests in 54.190s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 342 tests in 0.981s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (118 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785286067 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785286067. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785286068 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785286068
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785286068. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785286069 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785286069. Human review + merge required; the base branch was not modified.
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
Ran 416 tests in 54.610s

OK
```

## Retrospective

[R-00000107](../../retrospectives/R-00000107.md) 가 본문을 쥔다.

같은 모양의 갇힘을 하루에 세 번 봤다 — 기존 빚이 마이그레이션을 막고 그 빚은 마이그레이션 없이
못 고치는 것(보고 ①), 실패 표식이 복구 시도까지 막는 것(보고 ③), 설치 플러그인의 스키마 강제가
앞서간 저장소를 잠그는 것(우리 2회차). 전부 "고치려면 X 가 필요한데 X 가 그 고침을 요구한다".
탈출구 없는 fail-closed 는 안전이 아니라 감금이다.

## Promotion decision

**official 로 안 올린다.** 계약은 DE-00000035 가 쥔다. 이 스토리는 에픽 W-00000104 가 닫힐 때
에픽과 통째로 보관된다 — 이 카드가 만든 규칙의 첫 적용이다.
