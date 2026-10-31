---
id: W-00000291
title: 병렬 브랜치가 같은 기록 번호를 쓰지 않게 한다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000291
promotion: not_applicable
review: passed
scope: stage/scripts/stage_record_ids.py, stage/scripts/tests/test_stage_record_ids.py, stage/skills/stage-work/register_work.py, stage/scripts/tests/test_register_work.py, stage/skills/stage-decision/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000081
---

# W-00000291 병렬 브랜치가 같은 기록 번호를 쓰지 않게 한다

## Purpose

여러 세션이 다른 브랜치에서 동시에 일해도 새 카드와 결정이 이미 쓰인 번호를 다시 쓰지 않게 한다.

## Actions

- 지금 동작: `register_work.py` 의 `existing_numbers()` 는 지금 체크아웃의 카드만 세어 다음 W 번호를 고른다.
  결정(DE)과 관측(O) 번호는 도구 없이 손으로 고른다. 2026-10-31 병렬 브랜치에서 W-00000286 과
  DE-00000076 이 실제로 겹쳤다.
- `stage/scripts/stage_record_ids.py` 가 지금 체크아웃과 모든 로컬·원격 추적 브랜치의 `.stage/` 에서 한
  접두사(W, DE, O 등)의 번호를 세고 다음 번호를 알려 준다. 브랜치는 이미 받아 둔 것만 본다.
- `register_work.py` 가 자동으로 번호를 고를 때 이 번호들을 함께 센다. 직접 준 `--id` 가 지금 체크아웃에
  없고 다른 브랜치에 있으면 그 브랜치 이름과 함께 거절한다. 지금 체크아웃에 있는 카드를 다시 등록하는
  재실행은 지금처럼 인덱스만 맞춘다.
- `stage/skills/stage-decision/SKILL.md` 가 결정 번호를 이 도구로 고르라고 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

여러 세션을 병렬로 돌려도 번호를 손으로 다시 매기거나 합칠 때 충돌을 풀 일이 줄어든다.

## Scope

### Included


### Excluded

- 원격을 새로 받아 오는 일(`git fetch`). 도구는 네트워크를 쓰지 않는다.
- 아직 push 하지 않은 다른 컴퓨터의 번호 — 볼 방법이 없다.

## Risks


## Success criteria

- 다른 로컬 또는 원격 브랜치에 이미 있는 W 번호를 등록 도구가 고르지 않고, 그 번호를 직접 주면 거절한다는 것을 테스트가 확인한다
- 결정과 관측 같은 다른 기록의 다음 번호를 브랜치를 넘어 알려 주는 도구가 있고, 결정 절차가 그 도구로 번호를 고르라고 적는다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Added stage/scripts/stage_record_ids.py, which counts one id prefix across the working tree's .stage records (through stage_record_paths.record_paths, skipping .runtime and the all-zero template ids) and every local and remote-tracking branch (git for-each-ref plus git grep per ref), and prints the next free id; register_work.py now folds the W numbers on other branches into automatic allocation, refuses an explicit --id that exists on another branch but not in this checkout (naming the branch on the current-card path), and still reconciles a rerun of a card present in this checkout; the stage-decision skill tells authors to take DE numbers from the helper; tests cover template and runtime exclusion, local and remote-tracking branches for W, DE, and O, the non-git fallback, the CLI, automatic allocation past a branch's card for both branch kinds, explicit-id refusal on the current and planned paths, and a rerun of a local card that is also on a remote branch.
Why: W-00000291 - parallel sessions must not create records that collide when their branches merge.
Decisions made: Read only refs already fetched and never run git fetch, so registration stays offline and fast, and the decision skill asks authors to fetch first; let a local card win over a branch match so reruns keep reconciling instead of being refused after a push; keep allocation's O_EXCL loop and add branch numbers only to the starting set; give DE and O ids a helper instead of a full allocator because their records are still authored by hand from templates; scan the working tree through record_paths because the hooks suite forbids Markdown record scans outside that boundary.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `87726a00` 의 worktree 로 닫았다. 실행 보고는
`import_executor_report.py` 로 그 커밋 본문에서 작업 로그로 옮겼다. 이 세션에는 codex 가 없어,
`STAGE_CODEX_COMPANION` 을 `claude -p` 로 같은 프롬프트를 돌리는 대역 스크립트로 두고 이 프로젝트의
`implementation` 리뷰 명령을 설정 변경 없이 썼다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q
[exit 0]
----------------------------------------------------------------------
Ran 4 tests in 0.413s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 47 tests in 6.328s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793435123
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793435123. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp66pxa7ng/unattended/W-00000001-1793435123
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
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
Ran 694 tests in 119.520s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000291.md
Criteria:
- PASS: 다른 로컬 또는 원격 브랜치에 이미 있는 W 번호를 등록 도구가 고르지 않고, 그 번호를 직접 주면 거절한다는 것을 테스트가 확인한다
  Reason: existing_numbers now unions branch_record_numbers so automatic allocation skips branch W numbers (test_auto_id_skips_numbers_used_on_other_branches covers refs/heads and refs/remotes), and an explicit --id present only on another branch is refused on both current and --backlog paths (test_explicit_id_used_on_another_branch_is_refused) while a local rerun still reconciles; the planned path refuses without naming the branch, which the executor disclosed in What changed and the criterion does not require.
- PASS: 결정과 관측 같은 다른 기록의 다음 번호를 브랜치를 넘어 알려 주는 도구가 있고, 결정 절차가 그 도구로 번호를 고르라고 적는다
  Reason: stage/scripts/stage_record_ids.py counts any 1-3 letter prefix across the working tree and every local and remote-tracking ref via git grep without fetching, tests cover DE and O on local and remote branches plus the CLI, and stage-decision/SKILL.md line 157 tells authors to take DE numbers from that helper.
```

## Retrospective

[R-00000291](../../retrospectives/R-00000291.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000081)뿐이므로 `not_applicable`이다.
