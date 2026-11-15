---
id: W-00000329
title: 드라이버가 카드 등급의 모델과 에포트를 실행기와 리뷰어에 넘긴다
kind: development
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_driver_model_tier.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000329
promotion: not_applicable
review: passed
scope: stage/scripts/driver_environment.py, stage/scripts/driver_supervised.py, stage/scripts/driver_unattended.py, stage/scripts/driver_worklog.py, stage/skills/stage-drive/, stage/scripts/tests/test_driver_model_tier.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000329 드라이버가 카드 등급의 모델과 에포트를 실행기와 리뷰어에 넘긴다

## Purpose

드라이버가 부르는 실행기와 리뷰어가 명령에 모델을 박지 않고도 카드 등급의 모델과 에포트로 돌게 한다

## Actions

하나의 구현 단위라 action 으로 나누지 않는다.

## User value

실행기·리뷰어 명령에 `--model 'opus[1m]'` 같은 값을 박지 않고 `"$STAGE_MODEL"` `"$STAGE_EFFORT"` 를 쓰면 카드마다 맞는 모델로 돈다. 다시나의 실행기 명령은 지금 claude `--model 'opus[1m]'`, codex `--model gpt-6-astra --effort high`, agy `--model gemini-4-argon-medium --effort medium` 을 박아 두고 있다.

설계 SSOT: `.stage/work/current/W-00000326/W-00000327/_story.md` 의 `## Design` 중 "드라이버: STAGE_MODEL / STAGE_EFFORT" 를 먼저 읽는다. W-00000328 의 `stage/hooks/stage_model_tiers.py` 와 `WorkItem.tier` 를 쓴다.

## Scope

### Included

- `executor_environment` 에 실행기 venue 값, 리뷰어 환경(`driver_supervised.py` 의 `reviewer_env`, 무인 경로의 같은 자리)에 리뷰어 venue 값
- 작업 기록 `### Driver commands` 구역의 `Model tier (JSON):` 한 줄
- `stage/skills/stage-drive/` 에 두 환경 변수와 명령 작성법
- 시험: `stage/scripts/tests/test_driver_model_tier.py`
- `stage/CHANGELOG.md` 의 `## Unreleased` 한 줄

### Excluded

- 등록 시 `tier:` 기록(W-00000328), 훅(W-00000330), 감사가 기록을 읽는 일(W-00000331)
- 이 저장소의 `executors`·`review` 명령 변경

## Risks

- 무인 경로(`driver_unattended.py`)와 병렬 경로(`drive_parallel.py`)가 감독 경로와 다른 곳에서 환경을 만든다. 세 경로 모두 같은 함수를 거치는지 확인한다.
- 기록 줄 형식이 바뀌면 감사가 못 읽는다. 형식은 W-00000327 에 적힌 그대로 쓴다.


## Success criteria

- tier 가 적힌 카드를 드라이버가 돌리면 실행기 환경에 실행기 venue 의 STAGE_MODEL·STAGE_EFFORT 가, 리뷰어 환경에 리뷰어 venue 의 값이 들어가고, 명령이 "$STAGE_MODEL" 을 참조하면 그 값으로 돈다
- 드라이버 작업 기록에 시도마다 실행기와 리뷰어에 넘긴 모델·에포트가 남는다
- model_tiers 가 없거나 카드에 tier 가 없으면 두 환경 변수가 생기지 않는다

## Next action

W-00000328 이 끝난 뒤 이 세션의 Claude 가 local-no-codex 환경으로 직접 구현하고, 닫을 때 독립 리뷰를 받는다.

## Related truth


## Progress


### Executor report at close — 2026-11-14

```
What changed: driver_environment.py gained model_tier_environment and model_tier_record and stops inheriting STAGE_MODEL/STAGE_EFFORT; executor_environment exports the executor venue's tier values; the supervised reviewer environment and close_work.py's close review get the reviewer venue's values; supervised and unattended rounds add a "Model tier (JSON):" line to the Driver commands log entry; resolve_independent_reviewer_venue moved to stage_paths.py (driver_venues re-exports it); SCHEMA_V4, SCHEMA_V5, the stage-drive skill, the v4 settings template comment, and the CHANGELOG describe the variables; 11 tests in stage/scripts/tests/test_driver_model_tier.py.
Why: The card's purpose is that executors and reviewers run with the card tier's model and effort without fixing a model in their commands, and the audit needs each round's record.
Decisions made: Executed in this Claude session under environment local-no-codex (user decision after the Codex executor rejected gpt-6-astra). Scope boundary crossings: stage/skills/stage-retrospective/close_work.py (the close review is the unattended reviewer path and also runs at manual close, so it must receive the reviewer venue's values), stage/hooks/stage_paths.py and stage/scripts/driver_venues.py (moved resolve_independent_reviewer_venue because driver_venues imports close_work, so close_work importing driver_venues would cycle), stage/docs/SCHEMA_V4.md and SCHEMA_V5.md (the driver environment contract lives in SCHEMA_V4 and the tier contract in SCHEMA_V5), stage/templates/v4/project-stage/settings.jsonc (its executor comment told projects to hardcode --model). The record's command_uses_*_env flags test whether the command text names the variable. Inherited STAGE_MODEL/STAGE_EFFORT are dropped so a card without a tier never runs with a stale value. Confirmed the tests discriminate by removing the executor export (4 tests failed) and the reviewer export (3 tests failed), then restoring both. The unattended path is covered through the shared executor_environment and close_review_environment functions, not by an end-to-end unattended run.
Work not done: None
```

## Verification

- 닫기 리뷰는 Codex 를 쓸 수 없어 `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 대역으로 돌린 같은 모델(Claude) 리뷰다. venue 를 건너간 리뷰가 아니다.


### Executed at close — 2026-11-14

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_driver_model_tier.py -q
[exit 0]
----------------------------------------------------------------------
Ran 11 tests in 1.855s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 418 tests in 5.641s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794629323
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794629323. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpex6w1l2_/unattended/W-00000001-1794629323
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
Ran 747 tests in 154.844s

OK (skipped=2)
```

### Review at close — 2026-11-14

```
Review report: .stage/.runtime/driver/logs/W-00000329.md
Criteria:
- PASS: tier 가 적힌 카드를 드라이버가 돌리면 실행기 환경에 실행기 venue 의 STAGE_MODEL·STAGE_EFFORT 가, 리뷰어 환경에 리뷰어 venue 의 값이 들어가고, 명령이 "$STAGE_MODEL" 을 참조하면 그 값으로 돈다
  Reason: Ran python3 -m unittest discover -s stage/scripts/tests -p test_driver_model_tier.py -q (11 tests OK); executor_environment adds the item venue's tier values, the supervised reviewer_env and close_work.close_review_environment (used by the unattended close review) add the reviewer venue's values, drive_parallel reaches these by spawning driver.py, and a real supervised round test shows the executor got codex-large/medium, the reviewer sonnet/medium, and a printf "$STAGE_MODEL" prefix expanded to codex-large/medium.
- PASS: 드라이버 작업 기록에 시도마다 실행기와 리뷰어에 넘긴 모델·에포트가 남는다
  Reason: Both run_supervised_round and run_unattended pass model_tier_record (built from the same model_tier_environment the roles receive) into append_driver_commands_to_work_log on every round, which writes one Model tier (JSON) line with tier plus executor and reviewer venue, model, effort; the supervised round test in the 11-test run reads that line back from the log.
- PASS: model_tiers 가 없거나 카드에 tier 가 없으면 두 환경 변수가 생기지 않는다
  Reason: model_tier_environment returns empty without a tier or tier config, project_environment and close_review_environment pop inherited STAGE_MODEL/STAGE_EFFORT, and in the 11-test run the inherited-leak test and the no-model_tiers supervised round showed neither variable in executor or reviewer environments and no Model tier line in the log.
```

## Retrospective


## Promotion decision
