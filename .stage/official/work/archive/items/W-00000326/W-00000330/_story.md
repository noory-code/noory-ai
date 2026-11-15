---
id: W-00000330
title: Agent 호출의 모델과 에포트를 카드 등급에 맞추는 훅을 넣는다
kind: development
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_agent_tier.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000330
promotion: not_applicable
review: passed
scope: stage/hooks/stage_model_tiers.py, stage/hooks/stage_agent_tier.py, stage/hooks/stage_guard.py, stage/hooks/hooks.json, stage/hooks/README.md, stage/hooks/tests/test_agent_tier.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000330 Agent 호출의 모델과 에포트를 카드 등급에 맞추는 훅을 넣는다

## Purpose

세션 안에서 Agent 도구로 맡기는 일이 부모의 비싼 모델을 물려받지 않고 카드 등급의 모델과 에포트로 돌게 한다

## Actions

하나의 구현 단위라 action 으로 나누지 않는다.

## User value

Claude 가 세션 안에서 Agent 도구로 일을 맡길 때 모델·에포트를 빠뜨려도 부모의 Fable 을 물려받지 않고 카드 등급으로 돈다. 이유 없이 비싼 모델을 고르면 막힌다.

설계 SSOT: `.stage/work/current/W-00000326/W-00000327/_story.md` 의 `## Design` 중 "훅: Agent 호출" 과 `## Probe evidence` 를 먼저 읽는다. 사용자가 정한 것: 빠진 값은 카드 등급으로 채운다. 비싼 모델의 이유는 `description` 의 `[over-tier: <이유>]` 로 받는다.

## Scope

### Included

- 새 모듈 `stage/hooks/stage_agent_tier.py`: PreToolUse Agent 채움·막음, PreToolUse over-tier 통과 기록, SubagentStop 실제 모델·에포트 기록
- `stage/hooks/stage_guard.py` 의 `handle_event` 에 Agent·SubagentStop 을 넘기는 몇 줄과 `subagent-stop` 이벤트 이름
- `stage/hooks/hooks.json` 의 `SubagentStop` 항목, `stage/hooks/README.md`
- 시험: `stage/hooks/tests/test_agent_tier.py`
- `stage/CHANGELOG.md` 의 `## Unreleased` 한 줄

### Excluded

- `stage_guard.py` 의 `append_purpose_context` 와 작업 맥락 블록 (다른 세션이 줄이는 중이다)
- `claude -p` 로 하위 에이전트를 띄워 실제 모델을 확인하는 일 (에픽 W-00000326 을 닫을 때 Claude 가 맡는다)

## Risks

- 훅이 예외로 죽으면 모든 Agent 호출이 깨질 수 있다. 오류는 삼키고 아무것도 출력하지 않는다.
- `updatedInput` 에 원래 키를 빠뜨리면 호출 내용이 바뀐다.
- Codex 호스트도 같은 `hooks.json` 을 읽는다. Codex 에 없는 이벤트·도구 이름이 Codex 훅 실행을 실패로 만들지 않는지 확인한다.


## Success criteria

- 훅에 Agent 호출 입력을 넣어 돌리면, model·effort 를 적지 않은 호출은 카드 등급의 claude 값으로 채운 updatedInput(원래 키를 모두 담음)이 나오고, 카드 등급보다 비싼 모델을 description 의 [over-tier: 이유] 없이 고른 호출은 거부가 나온다
- 하위 에이전트가 끝날 때 실제로 돈 모델과 에포트가 .stage/.runtime 아래 기록에 남는다
- model_tiers 가 없으면 훅이 Agent 호출에 아무것도 하지 않는다

## Next action

W-00000328 이 끝난 뒤 이 세션의 Claude 가 local-no-codex 환경으로 직접 구현하고, 닫을 때 독립 리뷰를 받는다. 구현은 W-00000327 의 설계를 읽고 `stage_agent_tier.py` 와 시험부터 만든다.

## Related truth


## Progress


### Executor report at close — 2026-11-14

```
What changed: Added stage/hooks/stage_agent_tier.py: at PreToolUse an Agent call missing model or effort gets them filled from the current card tier's claude values through updatedInput (all original keys kept), a model costlier than the tier ceiling (or in no tier) is denied unless the description holds [over-tier: <reason>], open cards with different tiers deny a call that needs filling, and an allowed over-tier call is recorded; PostToolUse records agent_requested (agent id, requested model and effort, reason) for every Agent call including background launches; a new SubagentStop hook in hooks/hooks.json records agent_finished with the model and effort every subagent actually ran with, foreground or background. stage_guard.py gained current_leaves(), Agent dispatch in the pre/post branches, and a subagent-stop branch in handle_event; append_purpose_context is untouched. hooks/README.md, SCHEMA_V5, and the CHANGELOG describe it; 23 tests in stage/hooks/tests/test_agent_tier.py.
Why: The card's purpose is that Agent calls inside a session run on the card tier instead of inheriting the parent's costly model, and that what each subagent actually ran with is recorded when it finishes.
Decisions made: Executed in this Claude session under environment local-no-codex (user decision). The user chose to fill missing values and to take the over-tier reason from the description. The finish record uses SubagentStop as designed, because PostToolUse fires at launch for background calls; PostToolUse keeps the request record, joined on agent_id. SubagentStop can fire before the subagent's final assistant line is written, so the model is read from the last api-request line (params.model) of agent_transcript_path, overridden by an assistant line's message.model when present; effort comes from the event's effort.level. Codex reads the same hooks.json; the strings of the installed Codex 0.167.0 binary list SubagentStop among its hook event names (string evidence, not a Codex run), so the new key is not unknown to it, and the handler writes nothing when the payload lacks tiered context. Scope boundary crossings: stage/hooks/tests/test_gate_inventory.py (documented gate count 14 to 15 for the model-tier gate row) and stage/docs/SCHEMA_V5.md (the tier contract). Tests discriminate: disabling the fill, the ceiling check, or the record each failed tests and passed after restoring. Live checks in a scratch Stage project wired to this worktree's hooks, a standard-tier card, parent haiku (Claude Code 2.1.321): a call without model or effort ran as claude-sonnet-5-5/medium; a model opus call without a reason was denied; opus with [over-tier: ...] ran as claude-opus-5-5 with the reason recorded; a background call without model or effort recorded agent_requested (async_launched) and agent_finished claude-sonnet-5-5/medium; a foreground haiku/high call recorded agent_finished claude-haiku-5-5/high.
Work not done: None
```

## Verification

- 닫기 리뷰는 Codex 를 쓸 수 없어 `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 대역으로 돌린 같은 모델(Claude) 리뷰다. venue 를 건너간 리뷰가 아니다.
- 실측(2026-11-14, Claude Code 2.1.321): scratchpad 의 새 Stage 프로젝트에 이 worktree 의 `stage_guard.py` 를 PreToolUse·PostToolUse 훅으로 걸고, `standard` 등급 카드 하나를 열고, 부모 `--model haiku` 로 `claude -p` 를 세 번 돌렸다. model·effort 없이 부른 호출은 하위 에이전트가 `claude-sonnet-5-5`/`medium` 으로 돌았고 `agent_finished` 기록이 남았다. 이유 없이 `opus` 를 고른 호출은 막혔다. `[over-tier: verifying the over-tier path]` 를 단 `opus` 호출은 `claude-opus-5-5` 로 돌았고 `over_tier_allowed`·`agent_finished` 기록에 이유가 남았다.
- 첫 닫기 리뷰 지적(accept): 기록을 PostToolUse 로 옮긴 탓에 백그라운드로 띄운 하위 에이전트는 끝나도 기록되지 않았고, 실행 보고가 이 공백을 밝히지 않았다. 설계대로 `SubagentStop` 훅을 더해 끝난 기록(`agent_finished`)을 모든 하위 에이전트에 남기고, PostToolUse 는 요청 기록(`agent_requested`)만 남기게 했다. `SubagentStop` 순간에는 마지막 assistant 줄이 아직 없어서 모델을 `api-request` 줄에서 읽는다. 다시 실측했다. 백그라운드 호출은 `claude-sonnet-5-5`/`medium`, 포그라운드 haiku/high 호출은 `claude-haiku-5-5`/`high` 로 기록됐다.
- Codex 도 같은 `hooks.json` 을 읽는다. 설치된 Codex 0.167.0 실행 파일의 문자열에 `SubagentStop` 이 훅 이벤트 이름으로 들어 있다. Codex 로 실제로 돌려 확인하지는 않았다.


### Executed at close — 2026-11-14

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_agent_tier.py -q
[exit 0]
----------------------------------------------------------------------
Ran 20 tests in 0.048s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 438 tests in 5.537s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794630752
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794630752. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpcw975rjr/unattended/W-00000001-1794630752
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
Ran 747 tests in 148.701s

OK (skipped=2)
```

### Review at close — 2026-11-14

```
Review report: .stage/.runtime/driver/logs/W-00000330.md
Criteria:
- PASS: 훅에 Agent 호출 입력을 넣어 돌리면, model·effort 를 적지 않은 호출은 카드 등급의 claude 값으로 채운 updatedInput(원래 키를 모두 담음)이 나오고, 카드 등급보다 비싼 모델을 description 의 [over-tier: 이유] 없이 고른 호출은 거부가 나온다
  Reason: Ran python3 -m unittest discover -s stage/hooks/tests -p test_agent_tier.py -v (20 tests OK): handle_event pre-tool-use returns updatedInput equal to the original input plus the tier's model and effort, and a costlier model without a reason (or with an empty one) is denied; append_purpose_context returns its input unchanged for an Agent call without a scope boundary, so the dispatch is reached.
- PASS: 하위 에이전트가 끝날 때 실제로 돈 모델과 에포트가 .stage/.runtime 아래 기록에 남는다
  Reason: A SubagentStop hook in hooks.json now calls stage_guard.py subagent-stop, which writes agent_finished with model from the subagent transcript and effort from effort.level to .stage/.runtime/model-usage/<session>.jsonl; the record tests pass, and the executor's live probe files in its scratchpad show a background (async_launched) call finishing as claude-sonnet-5-5/medium and a foreground call as claude-haiku-5-5/high under the same parent; I read those files but did not rerun claude -p myself.
- PASS: model_tiers 가 없으면 훅이 Agent 호출에 아무것도 하지 않는다
  Reason: _review_call and _tiered_cards return early when config.tiers is None, and test_without_model_tiers_the_hook_does_nothing plus test_without_model_tiers_or_a_tiered_card_nothing_is_recorded passed in the run above, showing no output and no usage file.
```

## Retrospective


## Promotion decision
