---
id: W-00000106
title: 폴더가 계층을 갖는다 — 스키마 v5 토폴로지
kind: development
venue: codex
priority: 2
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000103
promotion: not_applicable
review: not_required
scope: stage/hooks/stage_record_paths.py, stage/hooks/stage_topology.py, stage/hooks/tests/, stage/scripts/lifecycle_paths.py, stage/scripts/audit_stage.py, stage/scripts/stage_schema_v4_migration.py, stage/scripts/tests/, stage/templates/, stage/operations/artifacts.md, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000106 폴더가 계층을 갖는다 — 스키마 v5 토폴로지

## Purpose

계층의 진실이 폴더 경로가 되게 한다. 지금은 상태마다 폴더 하나가 대응하고
(`card_location_for_status`), 그 폴더 안은 평평하다. 여기에 에픽 폴더와 스토리 폴더가 들어가고,
`_epic.md` 와 `_story.md` 가 그 묶음이 무엇을 이루려는지 쥔다.

`parent` 필드는 이 카드에서 없어진다. 문서 안에 부모를 또 적으면 폴더 경로와 어긋날 수 있다.

## Source

DE-00000035 — 세 규모, 폴더 계층, `parent` 제거.

## User value

카드를 어디에 놓았는지가 곧 규모 판단이 된다. 지금은 카드를 만들어도 그것이 무엇의 부분인지
아무 데도 안 남는다.

## Scope

### Included

- 상태별 폴더 하나를 돌려주던 경로 계약(`stage_topology.py`, `lifecycle_paths.py`)을 계층으로
  넓힌다.
- `_epic.md` / `_story.md` 템플릿을 만들고 액션 카드 템플릿에서 `parent` 를 뺀다.
  ko 로케일도 같이 간다.
- `operations/artifacts.md` 의 산출물 지도를 새 구조로 고친다. 이 문서는 세션이 시작될 때마다
  주입되므로 코드보다 늦으면 매 세션 틀린 안내가 깔린다. 그래서 이 카드 안에 있다.

### Excluded

- 등록할 때 규모를 묻고 액션을 막는 일 — W-00000107.
- 기존 카드를 옮기는 일 — W-00000110.

## Dependencies

W-00000105 — 카드를 찾는 일이 한 군데로 모인 뒤라야 이 카드가 한 자리만 고친다.

## Risks

- 이 카드가 끝나면 코드는 새 구조를 알지만 저장소의 카드는 아직 옛 모양이다. 그 사이 감사와
  가드가 깨지지 않아야 한다. 옮기는 것(W-00000110)까지 붙어서 한 덩어리로 나가야 할 수 있다.
- 액션 하나짜리 스토리가 자연스럽게 느껴져야 한다. 작은 일에도 폴더 둘이 생겨 무거우면
  사람이 안 쓴다.

## Success criteria

- 경로 계약이 에픽 폴더와 스토리 폴더를 알고, 최상위 항목 하나가 통째로 계획 → 진행 → 보관을
  지난다.
- `_epic.md` 와 `_story.md` 템플릿이 있고, 액션 템플릿에 `parent` 가 없다. ko 로케일도 같다.
- `operations/artifacts.md` 가 새 구조를 서술한다.
- W-00000105 의 회귀 테스트가 실제로 회귀를 막는다. 지금은 21개 중 5개 파일만 보고
  `.glob("*.md")` 리터럴만 잡는데, 실제로 쓰이는 모양은 `glob("W-*.md")`,
  `glob(f"{prefix}-*.md")` 라 누가 그 형태를 다시 들여와도 통과한다.
- 하위를 볼지 말지가 부르는 쪽마다 갈리지 않는다. 지금 `recursive=True` 를 쓰는 세 자리
  (`audit_stage.py:1103`, `stage_schema_v4_migration.py:644, 702`)가 각자 판단하고 있고,
  폴더가 깊어지면 그 판단이 결과를 가른다.
- 경로를 계산하는 함수가 프로세스의 현재 디렉터리를 안 읽는다. 리뷰가 임시 폴더에서 재현했다 —
  `retrospective_locations` 와 `resolve_artifact_reference` 가 상대 경로를 넘기고, 받는 쪽이
  그것을 현재 디렉터리 기준으로 뒤진다. 지금은 훅이 프로젝트 루트에서 돌아 잠복해 있지만
  W-00000110 이 계층을 만들면 엉뚱한 트리를 가리키는 경로가 나온다. 재현 상황을 테스트로 고정
  한다.
- 두 테스트 모음 통과, 감사 errors=0, 플러그인 버전 + CHANGELOG.

## Next action

`card_location_for_status` 가 지금 무엇을 약속하는지 읽고, 계층이 들어갔을 때 그 약속이 무엇으로
바뀌어야 하는지 정한다.

## Progress

폴더 경로가 계층의 유일한 진실이 됐다. 에픽과 스토리는 `_epic.md`·`_story.md` 를 품은 폴더이고,
액션은 혼자 못 서는 잎이다. 최상위 하나가 통째로 계획 → 진행 → 보관을 지난다. 액션 템플릿에서
`parent` 가 빠졌다. 카드를 찾을 때 항상 하위로 내려가며, `recursive` 인자를 기본값으로 두지 않고
없애서 옛 선택을 되살릴 수 없게 했다.

바뀐 파일 35개, 플러그인 0.51.0. 영문·한국어 계층 템플릿 12개가 새로 생겼다.

드라이버를 두 번 돌렸다. 첫 번째는 명령당 15분 제한이 이 카드보다 짧아 실행자가 잘렸다 — 일은
끝나 있었는데 판정만 실패로 남았다. 두 번째는 제한을 45분으로 올려 돌렸고, 리뷰가 기준 7개를
전부 통과시켰으나 드라이버가 실패로 기록했다. 리뷰어가 `CRITERIA VERDICT:` 를 콜론 없는 제목으로
써서 기계가 못 읽었다. 판정 내용이 아니라 형식 문제다.

## Verification

실행자 codex, 리뷰어 claude (venue 가 서로 다름).

- `python3 -m unittest discover -s stage/hooks/tests -q` — 336개 통과.
- `python3 -m unittest discover -s stage/scripts/tests -q` — 391개 통과.
- `python3 stage/scripts/audit_stage.py --project-root .` — errors=0, warnings=12.

리뷰어가 완료 기준 일곱 개를 전부 PASS 로 판정하고 APPROVED 를 냈다. 중간에 받은 기준(경로
함수가 현재 디렉터리를 안 읽는다)은 리뷰어가 임시 폴더에서 재현 상황을 직접 눌러 확인했다.

경고 12개는 이 저장소에 깔린 템플릿 복사본이 플러그인 쪽 변경을 안 따라와서 난다. 여섯은 새
`_epic.md`·`_story.md` 가 아직 없어서, 여섯은 `README.md`·`_template.md` 가 옛 내용이어서다.
카드가 미리 적어 둔 위험("코드는 새 구조를 아는데 저장소는 옛 모양인 구간") 그대로이고
W-00000110 이 해소한다.

### 기준 밖 지적의 처리

이번 회차에 새로 나온 셋.

- **`record_path` 가 루트의 절대·상대 여부로 동작이 갈린다** — **미룸 → W-00000110.** 같은
  시그니처인데 절대 루트면 트리를 뒤지고 상대 루트면 경로를 조립한다. 카드가 실제로 중첩
  폴더로 가면 파일은 중첩 경로에 있는데 인덱스 링크는 평평한 경로를 가리켜 어긋난다. 오늘은
  두 결과가 같아 잠복이다. 옮기는 카드가 인덱스 링크를 실제 경로로 맞춰야 하므로 그 카드의
  기준에 넣었다.
- **새 회귀 테스트가 후보 경로를 한 자리만 고정한다** — **안 받음.** 리뷰어 자신이 나머지
  인덱스도 같은 코드 경로를 탄다고 확인했다. 자리를 늘려도 같은 코드를 다시 누르는 것이다.
- **CHANGELOG 0.51.0 에 이번 수정이 안 적혀 있다** — **받음, 이 카드에서 고쳤다.** 현재
  디렉터리 의존을 없앤 것이 항목으로 들어갔다. 기록이 사실과 달라지는 것을 두면 안 된다.

앞 회차에서 올렸고 아직 남은 일곱.

- **v3 마이그레이션이 여전히 `parent:` 를 써 넣는다** — **미룸 → W-00000110.** 옛 스키마에서
  올라온 프로젝트가 새 템플릿이 없앤 필드를 가진 카드로 착지한다. 옮기는 카드가 정리한다.
- **`start_work.py` 가 시작하는 모든 카드에 빈 `parent:` 줄을 넣는다** — **미룸 → W-00000107.**
  그 카드가 등록·시작 진입점을 소유한다. 지우려면 필드 순서와 마일스톤 삽입 위치 두 자리를
  같이 봐야 한다.
- **`parent` 계층 게이트가 공중에 뜬다** — **미룸 → W-00000107.** 템플릿에서 필드가 빠졌는데
  폴더 계층을 보는 게이트는 아직 없다. 그 카드까지 계층 검사가 안 걸리는 구간이 생긴다.
  그 카드의 본체가 이것이다.
- **회귀 테스트의 집합 중복 제거 구멍** — **안 받음.** 이미 예외로 등록된 파일 안에 똑같은
  문자열의 호출이 하나 더 느는 경우다. 그 상황이 이 저장소에 오려면 누가 예외 파일을 골라
  같은 줄을 복사해야 한다.
- **ko 계층 템플릿의 `parent` 부재는 테스트가 안 본다** — **안 받음.** 리뷰어가 파일을 직접
  확인했고 실제로 없다. ko 는 액션 템플릿이 영문으로 폴백하는 구조라 갈릴 자리가 아니다.
- **이 저장소의 감사 경고 12개** — **미룸 → W-00000110.** 위에 적은 그대로다.
- **패턴 조회가 트리 전체를 읽는다** — **미룸 → W-00000110.** 보관함이 백 장을 넘고
  `archive_work.py` 가 루프 안에서 부르므로 옮긴 뒤 비용이 눈에 띌 수 있다. 그때 재어 보고
  정한다.

### Executed at close — 2026-07-28

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 336 tests in 1.019s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785238986
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785238986. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785238986 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785238986. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785238988 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785238988
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785238988. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785238988 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785238988. Human review + merge required; the base branch was not modified.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 391 tests in 56.443s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 336 tests in 0.968s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785239044
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785239044. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785239044 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785239044. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785239046 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785239046
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785239046. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785239046 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785239046. Human review + merge required; the base branch was not modified.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 391 tests in 56.598s

OK
```

## Retrospective

[R-00000103](retrospectives/R-00000103.md) 가 본문을 쥔다.

앞 카드가 만든 경계 덕분에 계층을 넣는 변경이 실제로 한 자리에서 이뤄졌다. 시도 셋 중 둘은
카드가 아니라 드라이버 계약의 빈틈에 썼다 — 명령당 15분 제한이 카드 크기와 무관하게 고정이고,
리뷰 판정의 기계 판독이 글자 하나(`CRITERIA VERDICT:` 의 콜론)에 걸린다. 둘 다 이 에픽과 범위가
달라 따로 세운다.

## Promotion decision

**official 로 안 올린다.** 계약은 DE-00000035 가 쥐고 있고 이 카드는 그것을 코드로 옮겼다.
카드와 회고는 보관으로 간다.
