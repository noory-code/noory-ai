---
id: W-00000100
title: 무인 모드가 실패했을 때 그 사실을 제대로 남긴다
kind: fix
venue: codex
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000099
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive_unattended.py, stage/scripts/tests/test_drive.py, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000100 무인 모드가 실패했을 때 그 사실을 제대로 남긴다

## Purpose

무인 모드의 실패 경로가 이 저장소에서 한 번도 실제로 돌지 않았다. W-00000096 은 성공해서 그 길을
안 탔고, W-00000097 이 처음 타면서 두 군데가 동시에 드러났다.

- **왜 실패했는지 아무 데도 안 남는다.** 실행자가 세 번 다 실패했는데 드라이버 출력에는
  `executor failed; retry n/3` 한 줄뿐이다. 실행자가 무엇을 말하고 죽었는지 사람이 볼 방법이
  없다. 정작 공용 작업 로그에는 실행자가 "다 했다" 고 두 라운드를 적어 놓았다 — 실행자와
  드라이버의 판단이 갈렸는데 그 근거가 사라진다.
- **실패를 기록하려는 커밋이 막힌다.** 에스컬레이션을 커밋할 때 `.stage` 를 통째로 add 하는데,
  그 안의 `.stage/.runtime` 이 무시 대상이라 git 이 거부한다 (`drive.py:898`). 재현했다.
  결국 사람에게 올리지도 못하고 끝난다.

두 번째가 특히 나쁘다. 실패를 남기려다 실패하면 아무 흔적도 안 남는다.

## Scope

- 실행자가 실패했을 때 그 출력을 남긴다 — 사람이 원인을 볼 수 있는 자리에. 공용 작업 로그가
  이미 그 자리다 (DE-00000034).
- 에스컬레이션 커밋이 무시 대상 폴더 때문에 막히지 않게 한다.
- 리뷰어가 실패했을 때도 같다.

범위 밖: 실행자가 왜 실패했는지 자체는 이 카드가 아니다. 남기는 쪽만 고친다. 드라이버가 자기가
띄운 실행자를 안 거두는 문제는 W-00000101.

## Success criteria

- 실행자가 실패하면 그 출력이 공용 작업 로그에 남는다. 확인 테스트가 있고, 고치기 전 코드에서
  실패한다.
- 리뷰어가 실패해도 같다.
- 무시 대상 폴더가 있어도 에스컬레이션 커밋이 성공한다. 확인 테스트가 있고, 고치기 전 코드에서
  실패한다.
- 인수 검사 두 개가 통과한다. 버전을 올리고 CHANGELOG 에 적는다.

## Review limit

이번이 마지막 리뷰 라운드다. 위 기준 밖의 지적은 받지 말고 기록만 남긴다.

## Related truth

DE-00000034 의 C4 층이다. 계약의 "한 바퀴가 실패하면 무엇이 남는가" 절이 규칙 2 와 4 를 갖는다 —
실패 이유와 그때의 출력은 공용 로그에 남고, 사람에게 올리는 커밋은 반드시 성공한다.


## Progress

- 2026-07-27: 실행자 실패 출력, 리뷰어 BLOCK 출력, ignored `.stage/.runtime`이 있는 lifecycle
  커밋의 회귀 테스트 3개를 먼저 추가했다. 기존 코드에서 각각 공용 로그에 실패 기록이 없거나
  Git이 ignored 경로를 거부하는 기대한 이유로 RED를 확인했다.
- 2026-07-27: 드라이버가 기존 실패 판정을 바꾸지 않고 이유와 `run_check` evidence를 카드별
  공용 로그에 append하게 했다. lifecycle 커밋은 tracked `.stage` 갱신과 non-ignored untracked
  경로를 따로 stage하며 runtime은 제외한다. 같은 회귀 테스트 3개가 GREEN이다.
- 2026-07-27: 최종 인수 검사에서 scripts 371개와 hooks 327개가 모두 통과했다.

## Verification

사람이 직접 확인했다 (실행자 진술을 근거로 쓰지 않는다 — DE-00000034 규칙 2).

- 실패가 공용 로그에 남는다. 실패를 로그에 붙이는 자리가 드라이버 네 곳(감독·무인, 실행자·리뷰어)
  에 들어갔다 (`append_failure_to_work_log`, drive.py:487).
- 로그에 붙이지 못하면 그 자체를 오류로 낸다 (drive.py:510). 실패를 남기려다 조용히 실패하는
  자리가 없다.
- 사람에게 올리는 커밋이 무시 대상 경로를 피한다 — 추적 중인 `.stage` 변경과, 무시되지 않은
  미추적 파일을 따로 골라 담는다 (drive.py:924·930·940). `git add -f` 를 쓰지 않아 runtime
  폴더는 그대로 커밋 밖에 있다.
- 확인 테스트가 여섯 개 늘었다 — 실행자 실패 출력이 로그에 남는지, 무시된 runtime 폴더가 있어도
  기록 커밋이 되는지, 그 커밋이 실패하면 실행이 멈추는지.
- 인수 검사를 직접 돌렸다: scripts 371개 OK, hooks 327개 OK. 감사 오류 0.
- 버전 SSOT 둘 다 0.47.0, CHANGELOG 갱신됨.

기준 밖 관찰 (받지 않음, 기록만):

- 코덱스 세션은 `.git` 을 못 써서 커밋은 사람이 했다.

### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137539
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137539. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137540 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137540. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137541 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137541
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137541. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137542 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137542. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 59.148s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.976s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137599
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137599. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137600 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137600. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137602 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137602
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137602. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137602 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137602. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.906s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.964s

OK
```

## Retrospective


## Promotion decision
