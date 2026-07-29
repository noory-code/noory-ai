---
id: W-00000099
title: 값을 쓸 자리가 없으면 조용히 넘어가는 것을 막는다
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
retrospective_ref: R-00000098
promotion: not_applicable
review: not_required
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/scripts/start_work.py, stage/scripts/tests/test_register_work.py, stage/templates/v4/project-stage/work/planned/_template.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000099 값을 쓸 자리가 없으면 조용히 넘어가는 것을 막는다

## Purpose

2026-07-27, W-00000096 을 무인으로 돌려 닫았다. 독립 리뷰가 실제로 돌았고 통과했고 그 증거가
카드 `## Verification` 에 남았는데, 카드의 `review` 상태는 안 적혔다. 감사가 "자율 작업인데
독립 리뷰가 not_required" 로 막았다.

원인은 두 겹이다.

- 카드를 닫는 도구가 상태를 쓸 때 쓰는 함수(`set_field`)가 **그 칸이 없으면 아무것도 안 하고
  성공을 돌려준다.** 값을 못 썼는데 못 썼다는 사실이 아무 데도 안 남는다.
- 계획으로 잡아둔 카드를 시작하면 `review` 칸이 안 생긴다. 그래서 무인으로 도는 카드는 통과해도
  기록될 자리가 없다.

첫 번째가 근본이다. Fail Fast 위반이고, 같은 함수가 `verification`, `promotion`, `status` 도
쓴다 — 어느 칸이든 없으면 같은 일이 난다.

## Scope

- `set_field` 가 대상 칸을 못 찾으면 실패하게 한다. 부르는 쪽은 그 실패를 삼키지 않는다.
- 계획 카드를 시작할 때 `review` 칸이 생기게 한다. 계획 카드 템플릿에도 넣는다.
- 이미 닫힌 W-00000096 의 `review` 를 통과로 보정한다 (리뷰는 실제로 돌았고 증거가 카드에 있다).

범위 밖: 감사 규칙은 그대로 둔다. 지금도 옳게 막았다.

## Success criteria

- 쓸 칸이 없는 상태로 카드를 닫으려 하면 실패한다. 그것을 확인하는 테스트가 있고, 고치기 전
  코드에서는 조용히 통과한다.
- 계획으로 잡은 카드를 시작하면 `review` 칸이 있다. 확인 테스트가 있다.
- 무인으로 닫힌 자율 카드의 `review` 가 `passed` 로 적힌다. 확인 테스트가 있다.
- W-00000096 의 `review` 가 보정되어 감사 오류가 0 이다.
- 인수 검사 두 개가 통과한다. 버전을 올리고 CHANGELOG 에 적는다.

## Review limit

이번이 마지막 리뷰 라운드다. 위 기준 밖의 지적은 받지 말고 기록만 남긴다.

## Related truth

DE-00000034 규칙 2 — 밖에서 온 말은 판정 근거가 아니다. 이 결함은 그 안쪽 판이다. 도구가
자기 성공을 스스로 확인하지 않으면 같은 일이 난다.


## Progress

- 2026-07-27 RED:
  - `python3 stage/scripts/tests/test_close_work.py -k missing_lifecycle_field -v` —
    누락된 `verification` 칸이 있는데도 종료 코드가 0 이어서 실패했다 (`1 != 0`).
  - `python3 stage/scripts/tests/test_register_work.py -k starting_legacy_planned_card -v` —
    시작된 카드에 `review: not_required` 가 없어서 실패했다.
- `set_field` 가 한 줄도 바꾸지 못하면 `ValueError` 를 내고, 닫기 호출부는 카드와 인덱스를 쓰기
  전에 오류와 `work item unchanged` 를 반환하도록 고쳤다.
- 기존 계획 카드 시작 시 `review: not_required` 를 보충하고, 계획 카드 템플릿에도 같은 칸을
  추가했다. Stage 플러그인 버전 두 곳을 `0.46.1` 로 맞추고 CHANGELOG 를 갱신했다.
- 실제 독립 리뷰 증거가 있는 W-00000096 의 `review` 를 `passed` 로 보정했다.
- focused GREEN 세 건이 통과했다. 자율 카드의 반대 venue 리뷰 승인 후 `review: passed` 가
  남는 기존 통합 테스트도 포함했다.
- 전체 검사: scripts 368 tests OK, hooks 327 tests OK. Stage 감사 결과는
  `errors=0, warnings=1` 이며 경고는 로컬 planned 템플릿 guidance 차이(`TEMPLATE004`)다.

## Verification

사람이 직접 확인했다 (실행자 진술을 근거로 쓰지 않는다 — DE-00000034 규칙 2).

- 값을 쓸 칸이 없으면 이제 `ValueError` 를 낸다 (`close_work.py:94`). 조용히 통과하던 자리가
  막혔다.
- 계획으로 잡은 카드를 시작하면 `review` 칸이 생기고, 계획 카드 템플릿에도 들어갔다. 이 프로젝트
  사본은 `refresh_guidance.py` 로 맞췄다.
- W-00000096 의 `review` 가 `passed` 로 보정됐다. 그 카드에는 리뷰어 승인 증거가 이미 있었다.
- 감사 오류 0, 경고 0.
- 인수 검사를 직접 돌렸다: scripts 368개 OK, hooks 327개 OK. 이전보다 9개 늘었다.
- 버전 SSOT 둘 다 0.46.1, CHANGELOG 갱신됨.

기준 밖 관찰 (받지 않음, 기록만):

- 코덱스 세션은 `.git` 을 못 써서 커밋은 사람이 했다. 세 번째 시도에서야 코드가 나왔다 —
  첫 번째는 커밋 권한이 없다는 이유로 구현조차 안 했고(지시가 모호했다), 두 번째는 다른
  코덱스 작업이 43분째 매달려 있어 시작을 못 했다.
- 드라이버가 무인으로 끝나도 자기가 띄운 실행자 작업이 남는다. 그 껍데기가 다음 위임을 전부
  막는다. 이 카드 범위 밖이라 별도로 잡는다.

### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137419
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137419. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137419 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137419. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137421 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137421
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137421. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137421 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137421. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 59.201s

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
[W-00000001] completed on stage/driver/W-00000001-1785137479
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137479. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137480 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137480. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137481 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137481
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137481. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137482 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137482. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 59.064s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.982s

OK
```

## Retrospective


## Promotion decision
