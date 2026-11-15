---
id: W-00000331
title: 카드 등급과 실제로 돈 모델·에포트가 다르면 감사가 경고하게 한다
kind: development
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_model_tier.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000331
promotion: not_applicable
review: passed
scope: stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_model_tier.py, stage/skills/stage-audit/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000331 카드 등급과 실제로 돈 모델·에포트가 다르면 감사가 경고하게 한다

## Purpose

카드에 적힌 등급과 실제로 쓴 모델·에포트가 어긋난 것을 사람이 감사에서 보게 한다

## Actions

하나의 구현 단위라 action 으로 나누지 않는다.

## User value

카드에 `standard` 라고 적었는데 실행기가 박힌 `--model opus` 로 돌았거나 하위 에이전트가 Fable 로 돌았으면, 사람이 감사 한 번으로 그 사실을 본다.

설계 SSOT: `.stage/work/current/W-00000326/W-00000327/_story.md` 의 `## Design` 중 "감사" 를 먼저 읽는다. 읽을 기록은 W-00000329 의 작업 기록 `Model tier (JSON):` 줄과 W-00000330 의 `.stage/.runtime/model-usage/<session>.jsonl` 이다.

## Scope

### Included

- `stage/scripts/audit_stage.py`: 설정 모양 검사, 카드 `tier:` 이름 검사, 드라이버 기록 비교, 하위 에이전트 기록 비교
- `stage/skills/stage-audit/` 에 새 경고 코드 설명
- 시험: `stage/scripts/tests/test_audit_model_tier.py`
- `stage/CHANGELOG.md` 의 `## Unreleased` 한 줄

### Excluded

- 기록을 남기는 쪽(W-00000329, W-00000330)
- 보관된(archived) 카드의 지난 기록 비교 (지난 기록에 경고를 내면 고칠 수 없는 경고만 쌓인다)

## Risks

- 기록이 없거나 깨진 줄이 있을 때 감사가 죽으면 안 된다. 읽을 수 없는 줄은 건너뛰고 경고로 알린다.
- 경고 코드가 기존 코드와 겹치지 않게 한다.


## Success criteria

- 드라이버 작업 기록이나 하위 에이전트 기록에 남은 모델·에포트가 카드 tier 의 값과 다르면 audit_stage.py 가 그 카드와 두 값을 적은 경고를 낸다
- 값이 같거나 model_tiers 가 없으면 경고가 없다

## Next action

W-00000329 와 W-00000330 이 끝난 뒤 이 세션의 Claude 가 local-no-codex 환경으로 직접 구현하고, 닫을 때 독립 리뷰를 받는다.

## Related truth


## Progress


### Executor report at close — 2026-11-14

```
What changed: Added stage/scripts/audit_model_tier.py with codes TIER001-TIER005 and one call from Audit.run in audit_stage.py: invalid tier settings (TIER001) and a current card naming an undeclared tier or a tier without model_tiers (TIER002) are errors; for current-zone cards it warns when the latest "Model tier (JSON)" driver line ran on another tier or other model/effort values than the card's tier gives now, or a command did not read STAGE_MODEL/STAGE_EFFORT (TIER003), when an agent_finished model-usage record differs from the tier's claude model or effort, quoting an over-tier reason joined from agent_requested on agent_id (TIER004), and when a record line is unreadable (TIER005). The stage-audit skill lists the codes, SCHEMA_V5 the rules, CHANGELOG an entry; 10 tests in stage/scripts/tests/test_audit_model_tier.py.
Why: The card's purpose is that a person sees in the audit when the model and effort actually used differ from the card's tier.
Decisions made: Executed in this Claude session under environment local-no-codex (user decision). Put the checks in a new module stage/scripts/audit_model_tier.py instead of growing audit_stage.py (already over 2,000 lines; SoC), a scope boundary crossing, as is stage/docs/SCHEMA_V5.md (the tier contract). Only current-zone cards are compared, so archived history raises nothing. Cards whose records name several tiers are checked only for a model costlier than the highest tier. The Report type alias avoids X | Y syntax so the module imports on Python 3.9 (checked with /usr/bin/python3 3.9.6). Tests discriminate: disabling the driver check failed 2 tests and disabling the subagent check failed 3, both passing after restoring. Ran the audit on the scratch Stage project from W-00000330's live probes: the explicit haiku/high foreground call got two TIER004 warnings and the tier-filled background call none.
Work not done: None
```

## Verification

- 닫기 리뷰는 Codex 를 쓸 수 없어 `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 대역으로 돌린 같은 모델(Claude) 리뷰다. venue 를 건너간 리뷰가 아니다.
- 실제 기록 확인: W-00000330 실측 때 남은 scratchpad 프로젝트 기록으로 감사를 돌렸다. 직접 haiku/high 로 부른 호출에는 TIER004 경고 두 건(모델, 에포트)이 나왔다. 등급대로 sonnet/medium 으로 돈 백그라운드 호출에는 경고가 없었다.


### Executed at close — 2026-11-14

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_audit_model_tier.py -q
[exit 0]
----------------------------------------------------------------------
Ran 10 tests in 2.226s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 438 tests in 5.491s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794631317
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794631317. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpc_3prlah/unattended/W-00000001-1794631317
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
Ran 757 tests in 149.813s

OK (skipped=2)
```

### Review at close — 2026-11-14

```
Review report: .stage/.runtime/driver/logs/W-00000331.md
Criteria:
- PASS: 드라이버 작업 기록이나 하위 에이전트 기록에 남은 모델·에포트가 카드 tier 의 값과 다르면 audit_stage.py 가 그 카드와 두 값을 적은 경고를 낸다
  Reason: Ran python3 -m unittest discover -s stage/scripts/tests -p test_audit_model_tier.py -q (10 tests OK); a probe driver log with executor model cx-small and reviewer effort high under tier standard produced two TIER003 warnings naming W-00000001 with the received and expected model/effort, and the subagent tests show TIER004 warnings naming the card, the tier value, and the actual model or effort.
- PASS: 값이 같거나 model_tiers 가 없으면 경고가 없다
  Reason: test_matching_records_raise_nothing and test_without_model_tiers_nothing_is_checked pass, a probe with matching driver and subagent values printed no findings, and python3 stage/scripts/audit_stage.py --project-root . on this repo (no model_tiers) printed no TIER lines and no traceback; a card naming a tier without model_tiers yields a TIER002 error, which is the design's separate settings check, not a warning.
```

## Retrospective


## Promotion decision
