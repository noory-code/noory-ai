---
id: W-00000116
title: 대조가 드라이버의 지식과 카드 누적 기준으로 움직인다
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
retrospective_ref: R-00000113
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000116 대조가 드라이버의 지식과 카드 누적 기준으로 움직인다

## Purpose

DE-00000039 §1. 드라이버가 만들어 넘긴 작업 로그 경로는 드라이버가 대조에서 빼고(O-00000005), 대조 범위를 base_head 대비 누적으로 통일해 재시도가 어긋나지 않게 한다(O-00000006). 실행자 프롬프트 두 벌의 보고 문장도 같은 뜻으로 맞춘다.

## Actions

- 드라이버가 실행자에게 넘긴 작업 로그 경로를 주장·관측 대조에서 뺀다. 드라이버가 만들어
  넘긴 것이므로 드라이버가 안다 — 실행자 프롬프트에 "로그는 빼고 적어라"를 얹지 않는다.
- 대조 기준을 이번 스텝 전후가 아니라 **`base_head` 대비 누적**으로 바꾼다. 시도 기록이
  `base_head` 를 이미 들고 있다(`drive.py:1348-1354`). 그러면 실행자가 자연스럽게 적는 범위
  ("내가 이 카드에서 바꾼 것")와 뜻이 같아진다.
- 감독·무인 두 자리에 같은 기준을 적용한다 — `drive.py:1442`(감독), `drive.py:1990`(무인).
  둘 다 `changed_repository_paths` 를 부르고 `executor_report_error` 에 넘긴다.
- 실행자 프롬프트 두 벌(`.stage/settings.json` 의 `executors.claude`·`executors.codex`)의
  보고 문장을 새 기준과 같은 뜻으로 고친다. **같은 자리에서 DE-00000037 §2 가 요구한 조상
  읽기 문장도 넣는다** — 드라이버는 이미 `STAGE_WORK_ITEM_ANCESTOR_PATHS` 로 조상 경로를
  넘기는데(`drive.py:476`) 프롬프트는 아직 "카드가 지시 전부다"라고만 말한다. 코드는 실렸고
  설정이 안 따라온 자리다.
- 같은 문장을 새 프로젝트가 받는 `stage/templates/` 쪽에도 싣는다.
- `stage/CHANGELOG.md` 에 항목을 더하고 두 매니페스트 버전을 패치로 올린다.

## User value

정직하게 보고한 실행자가 실패로 기록되지 않는다. 재시도해도 앞 시도의 변경 때문에 불일치가
나지 않아, 재시도 경로가 실제로 쓸 수 있게 된다.

## Scope

### Included

- `stage/scripts/drive.py` 의 관측 기준과 두 호출 자리.
- `stage/skills/stage-retrospective/close_work.py` 의 `executor_report_error` — 대조 기준이
  바뀌면 이 함수가 받는 것도 같이 본다.
- `.stage/settings.json` 과 `stage/templates/` 의 실행자 프롬프트 두 벌.
- 테스트, CHANGELOG, 두 매니페스트 버전.

### Excluded

- 리뷰 판정을 파일로 받는 일 — W-00000117.
- 한계값과 사전 점검 — W-00000118.
- 상한 되돌리기 명령 — W-00000119.

## Risks

- 누적 기준으로 바꾸면 "이번 스텝에서 아무것도 안 바뀌었다"는 판정이 흐려질 수 있다. 그
  판정(`UNCHANGED_REPOSITORY_FAILURE`, `drive.py:1986`)은 지문 비교가 따로 쥐고 있으므로
  건드리지 않는다. 바뀌는 것은 **리뷰·대조에 넘기는 경로 목록**뿐이다.
- 리뷰어에게 넘기는 파일 목록도 같이 누적이 된다. 재시도에서 리뷰어가 앞 시도의 변경까지
  보게 되는데, 그것이 맞다 — 리뷰는 이 카드의 결과를 판정하지 한 시도의 증분을 판정하지
  않는다.

## Success criteria

- 실행자가 작업 로그 경로를 바뀐 파일 목록에 넣어도 대조가 통과한다. 그 경우를 고정하는
  테스트가 있다.
- 앞 시도에서 바뀌고 이번 시도에서 안 건드린 파일을 실행자가 목록에 넣어도 대조가 통과한다.
  재시도 상황을 고정하는 테스트가 있다.
- 감독 경로와 무인 경로가 같은 기준으로 목록을 만든다 — 두 자리 모두에 대해 위 두 성질을
  확인하는 테스트가 있다.
- `.stage/settings.json` 의 실행자 명령 두 벌과 `stage/templates/` 의 대응 자리가 같은 보고
  문장을 갖고, 그 문장이 조상 카드를 읽으라고 지시한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 전부 통과한다.
- `stage/CHANGELOG.md` 에 항목이 있고 두 매니페스트 버전이 같은 값으로 패치 올림돼 있다.

## Next action

끝나면 사람이 `work_record_scale` 이 아니라 **관측 기준을 읽는 자리 전수**를 세어 카드
`## Verification` 에 적는다. 작업 로그는 `.gitignore` 가 무시하므로 셈을 그쪽에 두지 않는다
(R-00000112 의 학습).

## Progress

드라이버 감독 실행, 2026-07-29. 첫 시도는 카드와 무관하게 죽었다 — 0.54.2 올림으로 코덱스가
캐시해 둔 0.54.1 훅 폴더가 사라져 실행자가 첫 읽기에서 막혔다(P-00000001 재발). 캐시를 맞춘
뒤 두 번째 시도가 기준 여섯을 전부 통과하고 리뷰도 APPROVED 를 냈다. 플러그인 0.54.3.

## Verification

인수 검사 통과 — 스크립트 422개, 훅 343개. 리뷰 판정: 기준 여섯 전부 PASS, APPROVED.

### 관측 기준을 읽는 자리 (전수)

작업 로그가 아니라 여기에 적는다 — `.stage/.runtime/` 는 `.gitignore:59` 가 무시한다
(R-00000112 의 학습).

| 자리 | 무엇 |
|---|---|
| `drive.py:300` `repository_path_snapshot` | 관측의 정의. 저장소 경로마다 지문을 만든다 |
| `drive.py:326` `changed_repository_paths` | 두 스냅샷을 비교해 바뀐 경로를 낸다 |
| `drive.py:1421` (감독) / `drive.py:1966` (무인) | 카드 시작 때 기준 스냅샷을 한 번 찍어 시도 기록에 넣는다 |
| `drive.py:1469` (감독) / `drive.py:2032` (무인) | 실행자가 끝난 뒤 스냅샷을 다시 찍는다 |
| `drive.py:1471` (감독) / `drive.py:2033` (무인) | 기준 대비 누적으로 목록을 만든다 |
| `drive.py:1489` (감독) / `drive.py:2061` (무인) | 드라이버가 만든 로그 경로를 대조에서 뺀다 |
| `close_work.py:161, 200` `executor_report_error` | 뺄 경로를 받아 주장·관측 양쪽에서 지운다 |

감독과 무인이 자리마다 짝을 이룬다. 한쪽만 고치면 실행 방식마다 계약이 갈리므로 여섯 쌍
전부 같이 움직였다.

### 리뷰 지적 처분 (기준 밖 넷)

- **누적 기준에 사람이 스텝 사이에 바꾼 것이 섞인다 — 받는다, 후속 카드로.** 확인했다.
  기준 스냅샷을 첫 시도에 한 번만 찍고(`drive.py:1420` 의 `if "base_repository_paths" not
  in item_state`) 계속 쓰므로, 그 뒤 사람이 고치고 커밋한 것까지 목록에 남는다. 감독 흐름은
  스텝 사이에 사람이 카드를 고치고 커밋하는 것을 **전제**하므로 다음 재시도에서 바로 터진다.
  이 카드가 O-00000005·6 을 고치면서 같은 모양의 셋째 구멍을 열었다 — 실행자가 안 한 일을
  주장하게 만드는 것은 같다. 에픽 안에 W-00000121 로 세운다(DE-00000038: 실행이 설계를
  되돌린다).
- **플러그인 테스트가 운영자 설정을 읽는다 — 받는다, 같은 후속 카드로.** 확인했다.
  `test_template_v4.py:117` 이 `PLUGIN_ROOT.parent / ".stage/settings.json"` 을 연다. 설치본
  에는 그 파일이 없어 스위트가 죽고, 플러그인 테스트가 운영자 설정에 묶인다. 이번 변경이
  들여온 것이므로 같은 카드에서 걷는다.
- **감독·무인의 지적 처분 계약이 다르다 — 미룬다.** 감독 쪽은 `executor_report_error` 에
  지적 목록을 안 넘기고 빈 경로 목록을 바로 실패로 만든다. 프롬프트가 약속한 "이유 있는
  decline/defer 는 빈 배열을 주장해도 된다"가 무인에서만 참이다. 이 카드가 만든 것이 아니고,
  리뷰 판정 계약을 다시 쓰는 W-00000117 의 자리다. 그 카드에 근거로 넘긴다.
- **비용: 시도마다 저장소 전체를 훑고 그 지도를 시도 기록에 쓴다 — 안 받는다.** 규모 비용만
  남고 안전 문제는 없다(형태 검증이 있다). 이 저장소 크기에서 실측 부담이 안 보이므로
  실제로 느려지는 것을 보고 나서 다룬다(AHA).

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785305705 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785305705
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785305705. Human review + merge required; the base branch was not modified.
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
Ran 422 tests in 58.786s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785305764 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785305764
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785305764. Human review + merge required; the base branch was not modified.
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
Ran 422 tests in 58.750s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 0.985s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000113](../../../retrospectives/R-00000113.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.
