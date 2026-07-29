---
id: W-00000095
title: 드라이버가 관찰한 파일 목록이 리뷰 입력이 된다
kind: development
venue: codex
priority: 1
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000096
promotion: not_applicable
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/scripts/tests/test_drive_unattended.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, .stage/settings.json, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000095 드라이버가 관찰한 파일 목록이 리뷰 입력이 된다

## Purpose

DE-00000034 의 첫 층을 구현한다. 지금 리뷰어는 자기 명령 안에서 `git diff HEAD~1` 을 돌려
검사 자료를 만들고, 드라이버는 거기에 작업자가 쓰던 격리 인덱스를 환경 변수로 밀어 넣는다.
그 인덱스가 오염되면 리뷰 입력이 통째로 뒤집힌다 — 저장소 962개 파일 중 956개가 삭제로 읽힌
9MB 입력이 리뷰어를 죽였다(Q-00000001).

대신 드라이버가 실행 전후로 저장소를 자기 환경에서 관찰해 바뀐 파일 목록을 만들고, 그것을
리뷰 입력으로 준다. 리뷰어는 목록을 받아 저장소 파일을 직접 연다.

## Source

DE-00000034(decided). 사고 기록: Q-00000001, W-00000073, W-00000090.

## User value

codex venue 카드를 드라이버로 끝까지 돌릴 수 있다. 지금은 리뷰 단계에서 매번 죽는다.

## Scope

### Included

- 드라이버가 실행 전후 저장소를 자기 환경(격리 인덱스가 아닌 본래 상태)에서 관찰해, 이번
  스텝에서 바뀐 파일 목록을 만든다.
- 리뷰어에게 그 목록과 카드 경로를 넘긴다. 리뷰어 명령이 `git diff` 로 자료를 만들지 않게
  설정을 바꾼다.
- 리뷰어를 부르는 자리 **셋 전부**가 목록을 만들어 준다 (DE-00000034 의 자리 표). 드라이버
  스텝은 실행 전후 비교로, 카드를 닫는 두 자리는 그 커밋이 담은 파일로 만든다. 닫기 쪽이
  같은 리뷰어 명령을 쓰면서 목록을 안 주면 리뷰어가 없는 것을 읽으러 간다.
- 리뷰어에게 격리 인덱스를 물려주던 경로를 걷어낸다 (`prepare_reviewer_index` 와 그것이
  세운 방어 포함).

### Excluded

- 로그 파일은 W-00000096 이 갖는다. 이 카드에서 리뷰어는 아직 아무 데도 쓰지 않고, 지금처럼
  표준 출력으로 판정한다.
- 왕복과 상한은 W-00000097 이 갖는다.
- 작업자 쪽 격리 인덱스는 그대로 둔다. 사람이 드라이버 실행 중에 커밋해도 되게 하는
  방어(W-00000081)이고, 이 계약에서 유지 대상이다.

## Dependencies

없음. 이 카드만 들어가도 드라이버는 그 자체로 돈다.

## Risks

- 리뷰어가 파일 목록만 받고 실제로 파일을 안 열면 판정이 부실해진다. 프롬프트로 지시하되,
  열었는지 강제할 방법은 없다 — 기준마다 근거를 쓰게 해서 간접 확인한다.
- 무인 모드는 이 자리에서 리뷰어를 돌리지 않으므로(확인함) 감독 모드 경로만 바뀐다. 무인
  모드의 리뷰는 close_work 가 갖고 있어 별개다.

## Success criteria

- 리뷰어에게 격리 인덱스를 물려주는 코드가 없다. 리뷰어는 부르는 쪽이 만든 파일 목록을 받는다.
- 리뷰어를 부르는 세 자리가 전부 목록을 준다 — 드라이버 스텝, 무인 항목을 닫을 때, 단계
  리뷰로 닫을 때. 닫는 쪽 두 자리에도 확인 테스트가 있고, 고치기 전 코드에서 실패한다.
- 닫을 때 도는 리뷰 명령도 `git diff` 로 자료를 만들지 않는다.
- 작업자가 인덱스를 어떻게 만들어 놓든 리뷰 입력이 달라지지 않는다. 그것을 확인하는 테스트가
  있고, 고치기 전 코드에서 실패한다.
- 작업자가 새로 만든 파일(아직 git 이 모르는 파일)도 목록에 들어간다. 그것을 확인하는
  테스트가 있다 (W-00000073 이 세운 보장을 잃지 않는다).
- 커밋도 인덱스도 없는 저장소에서 지금처럼 계속 돈다.
- 인수 검사 두 개가 통과한다. 플러그인 버전을 올리고 CHANGELOG 에 적는다.

## Review limit

이번이 마지막 리뷰 라운드다. 위 성공 기준 밖의 지적은 받지 말고 로그에 적기만 한다.

## Next action

`start_work.py` 로 시작한다.

## Progress

- 카드와 DE-00000034를 읽고, 이미 `active` 상태로 시작된 항목임을 확인했다.
- 기존 작업 트리의 다른 Stage 계획 변경은 이 항목과 분리해 그대로 보존한다.
- RED: 실행자 격리 인덱스를 비운 회귀 테스트에서 리뷰어가
  `STAGE_CHANGED_PATHS_FILE`을 받지 못해 `KeyError`로 종료했고, 1개 테스트가 예상대로
  실패했다.
- GREEN: 드라이버가 실행 전후의 실제 인덱스 메타데이터와 작업 트리 내용을 경로별로
  비교하고, 정렬한 JSON 목록을 자체 임시 파일에 써 `STAGE_CHANGED_PATHS_FILE`로 넘기게
  했다. 리뷰어 환경에서는 `GIT_INDEX_FILE`을 제거했다.
- 프로젝트의 codex/claude 감독 리뷰 명령은 Git diff를 만들지 않고 카드와 JSON 목록을 읽어
  각 파일을 직접 열도록 바꿨다. 실행자 쪽 격리 인덱스는 유지했다.
- 집중 회귀와 `test_drive.py` 37개 테스트가 통과했다.
- 버전 SSOT 둘을 `0.45.0`으로 맞추고 CHANGELOG를 갱신했다.
- 최종 인수 검사 두 개가 통과했다. Stage 감사의 `WORK015` 1건은 이 카드의 성공 기준 밖인
  DE-00000034의 기존 `work_item: W-00000094` 연결에 관한 관찰이므로 수정하지 않았다.
- 커밋을 위해 범위 파일을 하나씩 추가하려 했으나, 이 세션의 `.git` 쓰기 권한이 없어 첫
  `git add`가 `index.lock: Operation not permitted`로 거부됐다. 인덱스와 HEAD는 바뀌지
  않았다.
- 확장 라운드 RED: 닫기 리뷰 두 자리를 겨냥한 테스트 2개를 먼저 추가해 실행했고,
  무인 항목 닫기와 단계 리뷰 닫기 모두 리뷰 명령 안에서
  `KeyError: 'STAGE_CHANGED_PATHS_FILE'`로 실패했다 (`Ran 2 tests`, `FAILED
  (failures=2)`).
- GREEN: `close_work.py`가 `HEAD` 커밋이 담은 저장소 상대 경로를 정렬한 JSON 목록으로
  자체 임시 파일에 쓰고, 무인 항목 닫기와 단계 리뷰 닫기 양쪽에
  `STAGE_CHANGED_PATHS_FILE`로 넘긴다. 집중 테스트는 `Ran 2 tests`, `OK`였다.
- `review.strengths.standard`와 `review.strengths.red-team`은 카드와 JSON 경로 목록을 읽고
  목록의 파일을 직접 열며, Git diff나 index 상태에서 리뷰 자료를 만들지 않게 바꿨다.
  기준별 PASS/FAIL, 실패 기준에만 `[P1]`, 비차단 기준 밖 관찰, 판정이 없을 때 `BLOCK:`
  보장은 유지했다.
- Stage 플러그인 manifest 둘을 `0.45.1`로 올리고 CHANGELOG를 갱신했다.
- 확장 구현 뒤 `test_close_work.py` 39개가 통과했다. 최종 인수 검사는 scripts 359개,
  hooks 327개가 모두 통과했다.

## Verification

드라이버 밖에서 사람이 직접 확인했다 (실행자 진술을 근거로 쓰지 않는다 — DE-00000034 규칙 2).

- 리뷰어에게 인덱스를 물려주던 코드가 없다: `prepare_reviewer_index` 와 그 방어가 사라졌고,
  `GIT_INDEX_FILE` 은 실행자에게 넘길 때 한 번, 리뷰어 환경에서 지울 때 한 번만 나온다.
- 리뷰어 명령이 저장소 파일을 직접 열게 바뀌었다. `git diff` 를 쓰지 말라는 지시가 명령에
  들어 있고, 드라이버가 쓴 JSON 목록 경로를 받는다.
- 실행자가 만든 새 파일이 목록에 들어가는지 확인하는 테스트가 있다
  (`test_reviewer_opens_executor_created_file_from_observed_path_list`).
- 실행자가 인덱스를 비워도 리뷰 입력이 흔들리지 않는지 확인하는 테스트가 있다
  (`test_reviewer_receives_driver_observed_paths_without_executor_index`).
- 커밋도 인덱스도 없는 저장소가 계속 도는지 확인하는 테스트가 그대로 있다
  (`test_execute_passes_in_unborn_repository_without_an_index`).
- 인수 검사 두 개를 직접 돌렸다: scripts 357개 OK, hooks 327개 OK.
- 버전 SSOT 둘 다 0.45.0, CHANGELOG 갱신됨.

### 확장 라운드 확인 (리뷰 자리 셋)

첫 라운드는 리뷰어가 도는 세 자리 중 하나만 고쳤고, 그 과정에서 두 번째 자리를 깨뜨렸다 —
드라이버 스텝과 무인 항목 닫기가 **같은 리뷰어 명령**을 쓰는데, 그 명령이 받을 것을 바꿔놓고
닫는 쪽은 안 줬다. 계약(DE-00000034)에 자리를 세어 적는 절을 넣고 카드 범위를 넓혀 셋을 다
맞췄다.

- `close_work.py` 가 커밋이 담은 파일 목록을 자기 손으로 만들어 리뷰어에게 준다 (204 행).
  무인 항목을 닫을 때와 단계 리뷰로 닫을 때 양쪽에 준다.
- 닫을 때 도는 리뷰 명령에서 `git diff` 가 사라졌다 — 설정 전체에 `HEAD~1` 이 0 회.
- 닫기 두 자리를 겨냥한 테스트가 있다
  (`test_staged_review_receives_close_owned_committed_path_list`,
  `test_autonomous_review_receives_close_owned_committed_path_list`). 고치기 전 코드에서는
  둘 다 `KeyError: 'STAGE_CHANGED_PATHS_FILE'` 로 실패했다.
- 인수 검사를 다시 직접 돌렸다: scripts 359개 OK, hooks 327개 OK. 감사 오류 0.
- 버전 SSOT 둘 다 0.45.1.

기준 밖 관찰 (받지 않음, 기록만 남긴다):

- Codex 세션에 `.git` 쓰기 권한이 없어 두 라운드 모두 커밋은 사람이 했다. 위임 경로의
  제약이지 이 카드의 결함이 아니다.

- RED: `python3 stage/scripts/tests/test_drive.py
  DriveTest.test_reviewer_receives_driver_observed_paths_without_executor_index` — 리뷰어의
  `STAGE_CHANGED_PATHS_FILE` `KeyError`, `Ran 1 test`, `FAILED (failures=1)`.
- GREEN: 같은 집중 명령 — `Ran 1 test`, `OK`.
- `python3 -m unittest discover -s stage/scripts/tests -q` — `Ran 357 tests in 37.364s`,
  `OK`.
- `python3 -m unittest discover -s stage/hooks/tests -q` — `Ran 327 tests in 0.882s`,
  `OK`.

### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137178
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137178. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137179 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137179. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137180 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137180
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137180. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137181 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137181. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.868s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.962s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137238
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137238. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137239 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137239. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137240 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137240
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137240. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137241 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137241. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.949s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.967s

OK
```

## Retrospective

## Promotion decision
