---
id: W-00000114
title: 계층 게이트가 카드 아닌 표면을 카드로 오판하지 않는다
kind: fix
venue: codex
milestone:
priority: 1
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000112
promotion: not_applicable
review: not_required
scope: stage/hooks/, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000114 계층 게이트가 카드 아닌 표면을 카드로 오판하지 않는다

## Purpose

수명 주기 폴더 루트의 index.md·README.md·_template.md 등 카드가 아닌 파일을 계층 게이트가 카드 모양 검사에 태워 도구 편집을 전부 거부한다(O-00000009). 계획 인덱스에 선언된 rejected 상태로 갈 길이 없다. 게이트가 카드 아닌 표면을 검사에서 빼거나 계획 카드 반려를 스크립트가 맡게 하고, 그 갈림의 근거를 남긴다. 끝나면 W-00000092 를 DE-00000039 의 판정대로 반려 처리한다.

## Actions

- 계층 게이트가 수명 주기 루트(계획·진행·보관) 바로 밑 깊이 1 의 `.md` 파일을 카드 모양
  검사에 태우지 않게 한다. v5 에서 카드는 항상 폴더다 — 최상위 카드도 `W-xxx/_story.md`
  (깊이 2)로 산다. 깊이 1 `.md`(index.md, README.md, _template.md, 루트 템플릿 `_epic.md`·
  `_story.md`)는 카드일 수 없으므로 검사 대상이 아니다.
- `work_record_scale` 을 부르는 자리를 전부 세고(`stage/hooks/stage_guard.py`,
  `stage/hooks/stage_work.py`), 자리마다 고쳤는지 그대로 뒀는지와 그 이유를 작업 로그에 적는다.
- 게이트 테스트에 "계획 인덱스(`work/planned/index.md`) 편집이 허용된다"를 고정하는 케이스를
  더한다.
- `stage/CHANGELOG.md` 에 항목을 더하고 두 매니페스트(`stage/.claude-plugin/plugin.json`,
  `stage/.codex-plugin/plugin.json`)의 버전을 패치로 올린다.

## User value

계획 카드를 반려(`rejected`)하거나 수명 주기 인덱스·템플릿을 고치는 일이 게이트에 막히지
않는다. 선언된 상태 값이 실제로 도달 가능해진다.

## Scope

### Included

- `stage/hooks/` 의 계층 게이트 판정과 그 테스트.
- CHANGELOG 항목과 두 매니페스트의 패치 버전 올림.

### Excluded

- W-00000092 의 반려 처리 자체 — 이 수정이 끝난 뒤 사람이 한다.
- 계획 카드 반려를 스크립트로 만드는 일 — 손 편집이 열리면 지금은 충분하다(AHA).
- 감사(`audit_stage.py`)의 판정 — 감사는 이미 깊이 1 파일을 카드로 안 읽는다.

## Risks

- 검사를 너무 넓게 빼면 진짜 카드가 검사를 피해 갈 수 있다. 깊이 1 로만 한정하고, 깊이 2·3
  카드의 기존 검사와 부모 게이트가 그대로임을 기존 테스트 전부로 확인한다.

## Success criteria

- 깊이 1 `.md` 파일 편집이 계층 게이트를 통과한다 — `work/planned/index.md` 편집 허용을
  고정하는 게이트 테스트가 있다.
- 깊이 2·3 의 진짜 카드에 대한 카드 모양 검사와 부모 게이트는 그대로다 — 기존 훅·스크립트
  테스트가 전부 통과한다.
- `work_record_scale` 호출 자리 전부에 대해 고침/유지와 이유가 작업 로그에 적혀 있다.
- `stage/CHANGELOG.md` 에 이 수정 항목이 있고 두 매니페스트 버전이 같은 값으로 패치 올림돼
  있다.

## Next action

수정이 끝나면 사람이 W-00000092 를 DE-00000039 의 판정대로 반려 처리한다(O-00000009 의
잠금이 풀렸는지 그 편집으로 확인된다).

## Progress

드라이버 한 바퀴(코덱스 실행자 → 인수 검사 둘 → claude 리뷰어), 2026-07-29. 게이트가 수명
주기 루트 바로 밑 `.md` 를 카드 모양 검사 앞에서 건너뛴다(`stage_guard.py:458-459`, 두 줄).
기준 넷 중 셋 통과, 기준 3(호출 자리 전수)에서 리뷰어가 P1 을 냈다.

## Verification

인수 검사 둘 통과 — 훅 343개, 스크립트 416개 모두 OK. 리뷰 판정: 기준 1·2·4 PASS,
기준 3 FAIL [P1].

### 리뷰 지적 처분

**기준 3 (호출 자리 전수) — 받는다.** 실행자가 로그에 "호출 2곳"이라 적었고 실제로는 12곳이다.
직접 다시 세어 확인했다. 이 프로젝트가 DE-00000035 에서 얻은 규칙("적용 자리는 세고 나서
쓴다")을 그대로 어긴 것이므로 지적이 옳다.

**기준 3 이 가리킨 자리를 카드로 바꾼다.** 기준을 쓸 때 "작업 로그에 적혀 있다"고 했는데,
작업 로그는 `.stage/.runtime/` 에 살고 이 경로는 `.gitignore:59` 가 무시한다. 즉 로그에만
적힌 셈은 커밋에 안 남아 다음 사람이 못 본다 — 기준을 채워도 목적이 안 서는 길이었다.
셈을 아래 표로 카드에 남긴다.

| 호출 자리 | 이번에 | 왜 |
|---|---|---|
| `hooks/stage_guard.py:461` | **고침** | 이 카드가 고친 자리. 앞에서 깊이 1 을 건너뛴다 |
| `hooks/stage_work.py:252` | 유지 | `try/except ValueError` 안이라 카드 아닌 파일은 `parent = ""` 로 흘러간다. 막지 않는다 |
| `hooks/stage_roadmap_closure.py:183` | 유지 | 같은 모양으로 `ValueError` 를 잡아 그 파일을 건너뛴다 |
| `hooks/stage_record_paths.py:117` | 유지 | 모듈 자기 안의 호출. 판정 주체가 아니라 판정 자체 |
| `scripts/audit_stage.py:361, 631` | 유지 | 감사는 카드 아닌 파일을 애초에 안 넘긴다. 오히려 게이트가 놓친 것을 여기서 잡는다 |
| `scripts/escalate_work.py:252` | 유지 | 인자로 받은 카드 하나에만 부른다 |
| `scripts/start_work.py:215` | 유지 | 같음 — 옮길 카드 하나 |
| `scripts/stage_schema_v5_migration.py:198, 553, 682` | 유지 | 마이그레이션은 옛 평평한 모양을 알아야 하므로 이 검사가 필요하다 |
| `skills/stage-work/register_work.py:156` | 유지 | 부모로 지목된 카드 하나를 검사한다 |

**기준 밖 지적 셋의 처분.**

- **은퇴한 평평한 카드가 게이트를 통과한다 — 미룬다.** 사실이다. 다만 등록·시작 도구가 전부
  폴더로만 카드를 만들고, 마이그레이션이 옛 모양을 옮기므로 손으로 만들지 않는 한 안 생긴다.
  생겨도 감사가 `WORK026` 으로 잡는다. 리뷰어가 준 좁히는 법(깊이 1 예외에서 `W-\d+\.md`
  이름만 빼기)이 한 줄이라 값은 싸지만, 이 카드의 venue 는 codex 이고 지금 창은 claude 다.
  후속 카드 W-00000120 으로 넘긴다.
- **회귀 테스트가 Write 만 덮는다 — 안 받는다.** 예외가 경로로 판정되고 Write·Edit 가
  `hierarchy_item_targets` 의 같은 갈래(`file_path` 추출 → 같은 `targets`)를 지나므로 판정이
  같다. 도구 이름마다 핀을 박는 것은 같은 것을 세 번 세는 일이다.
- **`stage_work.py:252` 유지 이유가 부정확 — 받는다.** 위 표에 정확한 이유(`ValueError` 를
  잡아 `parent = ""` 로 흘림)로 적었다.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.030s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (118 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785303332 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785303332. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785303334 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785303334
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785303334. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785303334 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785303334. Human review + merge required; the base branch was not modified.
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
Ran 416 tests in 58.686s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.055s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (118 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785303392 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785303392. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785303394 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785303394
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785303394. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785303394 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785303394. Human review + merge required; the base branch was not modified.
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
Ran 416 tests in 58.980s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000112](../../retrospectives/R-00000112.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.
