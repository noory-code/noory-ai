---
id: W-00000327
title: 등급 표 설계와 Agent 훅 실측 결과를 카드에 남긴다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000327
promotion: not_applicable
review: not_required
scope: .stage/work/current/W-00000326/
promotes:
decision_refs:
---

# W-00000327 등급 표 설계와 Agent 훅 실측 결과를 카드에 남긴다

## Purpose

구현 story 네 장이 같은 설계와 실측 사실에서 출발하게 한다

## Actions

이 카드는 하나의 기록 작업이라 action 으로 나누지 않는다.

## User value

구현 story 넷(W-00000328~331)이 이 카드 하나를 읽고 같은 설정 모양, 같은 등급 순서, 같은 기록 형식으로 일한다. 사용자가 고른 설계는 "A. 등급 표" 다(오케스트레이터 세션이 세 안을 비교했고 사용자가 A 를 골랐다).

## Design

### 설정: `model_tiers` (SSOT)

프로젝트의 `.stage/settings.json` 에 둔다. 등급 이름마다 venue 별로 그 venue 의 원래 모양 값을 그대로 적는다. Stage 는 venue 사이에 값을 번역하지 않는다.

```json
"model_tiers": {
  "scout":    {"claude": {"model": "haiku",  "effort": "low"},    "codex": {"model": "<codex 모델>", "effort": "low"}},
  "standard": {"claude": {"model": "sonnet", "effort": "medium"}, "codex": {"model": "<codex 모델>", "effort": "medium"}},
  "strong":   {"claude": {"model": "opus",   "effort": "high"},   "codex": {"model": "<codex 모델>", "effort": "high"}},
  "lead":     {"claude": {"model": "fable",  "effort": "high"}}
}
```

- 선언 순서가 비용 순서다. 앞이 싸고 뒤가 비싸다. 훅과 감사는 이 순서로만 "더 비싸다" 를 판단한다.
- 한 venue 칸에서 `model` 과 `effort` 는 각각 생략할 수 있다. 생략한 값은 넘기지도 채우지도 않는다.
- 등급에 어떤 venue 칸이 없으면 그 venue 로 돌 때 Stage 는 아무 값도 넘기지 않는다(그 venue 의 기본값으로 돈다).
- claude 칸의 `model` 은 Agent 도구가 받는 별칭(`haiku`, `sonnet`, `opus`, `fable`)으로 적는다. 이 세션의 Agent 도구 스키마가 이 네 값을 enum 으로 받는다. `opus[1m]` 같은 꼬리표는 `claude -p --model` 에는 통하지만 Agent 도구 enum 에는 없다.
- `lead` 는 계획·지시 쓰기·결과 확인 전용이다. 기본 `tier_routing` 은 어떤 kind 에도 `lead` 를 주지 않는다. 그래서 Fable 을 고른 Agent 호출은 이유 없이는 막힌다.
- 플러그인 템플릿(`stage/templates/project-stage/settings.json`)은 claude 칸만 채운 네 등급을 싣는다. codex·agy 모델 이름은 프로젝트마다 달라서 템플릿이 정하지 않는다.

### 설정: `tier_routing` (kind × 크기 → 등급)

```json
"tier_routing": {
  "*": "standard",
  "documentation": "standard",
  "development": {"story": "standard", "action": "standard", "*": "standard"}
}
```

- 값이 문자열이면 그 kind 의 모든 크기(epic/story/action)에 그 등급을 쓴다.
- 값이 객체면 크기 이름으로 찾고, 없으면 그 객체의 `"*"`, 그것도 없으면 맨 위 `"*"` 를 쓴다.
- 아무것도 맞지 않으면 등급을 정하지 않는다(카드에 `tier:` 를 쓰지 않는다).
- `model_tiers` 에 없는 등급 이름을 가리키면 설정 오류다. 등록은 거부하고 감사는 오류로 알린다.

### 공용 모듈: `stage/hooks/stage_model_tiers.py`

설정 읽기·등급 고르기·venue 값 꺼내기·등급 순서 비교를 이 모듈 하나가 맡는다. 등록, 드라이버, 훅, 감사 모두 이 모듈만 부른다. W-00000328 이 만들고 나머지 story 가 가져다 쓴다.

### 카드: frontmatter `tier:`

- `register_work.py` 는 `model_tiers` 가 있을 때 `tier_routing` 으로 등급을 골라 `venue:` 바로 뒤에 `tier: <이름>` 을 쓴다. `--tier <이름>` 으로 직접 줄 수 있고, `model_tiers` 에 없는 이름이면 거부한다. `model_tiers` 가 없으면 `tier:` 줄을 만들지 않고 `--tier` 도 거부한다.
- `start_work.py` 는 나중에 하려고 적어 둔 카드(planned)를 시작할 때 `tier:` 가 비어 있으면 같은 규칙으로 채운다. 이미 있으면 건드리지 않는다.
- 사람이 카드의 `tier:` 를 고치면 그 값이 이긴다. 드라이버와 훅은 실행할 때마다 카드를 다시 읽는다.
- `WorkItem` 에 `tier` 필드를 더한다.

### 드라이버: `STAGE_MODEL` / `STAGE_EFFORT`

- 실행기 환경(`executor_environment`)에는 카드 `tier` 의 **실행기 venue** 값을, 리뷰어 환경에는 같은 등급의 **리뷰어 venue** 값을 넣는다. 리뷰어 venue 는 드라이버가 이미 구하는 `resolve_independent_reviewer_venue` 의 결과다.
- 값이 없는 키는 환경에 넣지 않는다. 카드에 `tier` 가 없거나 `model_tiers` 가 없으면 두 변수 모두 없다.
- 실행기·리뷰어 명령은 `"$STAGE_MODEL"` `"$STAGE_EFFORT"` 를 참조해 쓴다. 명령에 박힌 `--model` 은 그대로 동작한다(바꾸지 않아도 된다).
- 작업 기록의 `### Driver commands` 구역에 한 줄을 더한다: `Model tier (JSON): {"tier": ..., "executor": {"venue", "model", "effort", "command_uses_model_env", "command_uses_effort_env"}, "reviewer": {...}}`. `command_uses_*_env` 는 명령 문자열이 `STAGE_MODEL`/`STAGE_EFFORT` 를 참조하는지다. 참조하지 않으면 등급이 실제로 적용되지 않았다는 뜻이다.

### 훅: Agent 호출 (Claude Code 전용)

`stage_guard.py` 의 `handle_event` 는 PreToolUse 의 `Agent` 호출과 `SubagentStop` 을 새 모듈 `stage/hooks/stage_agent_tier.py` 로 넘기는 몇 줄만 더한다. 현재 카드 목록은 `stage_guard.active_work_chains` 의 leaf 를 인자로 넘긴다(leaf 고르는 규칙을 두 번 쓰지 않는다). `append_purpose_context` 는 고치지 않는다.

- 현재 카드: 드라이버가 `STAGE_WORK_ITEM_PATH` 를 줬으면 그 카드, 아니면 열린(active) leaf 카드들. 그중 `tier` 가 있는 카드만 센다.
- 아무 일도 안 하는 경우: `model_tiers` 가 없거나, `tier` 가 있는 현재 카드가 없을 때.
- 상한: 현재 카드 등급 가운데 가장 비싼 등급.
- 빠진 값(사용자 결정: 채운다): `model` 이나 `effort` 가 빠졌고 현재 카드 등급이 하나뿐이면, 그 등급 claude 칸의 값으로 채운다. `hookSpecificOutput.updatedInput` 에 원래 키를 모두 담고 빠진 키만 더한다. 채운 값은 `additionalContext` 로 알린다. 현재 카드 등급이 둘 이상이면 채울 값을 고를 수 없으므로 막고, 직접 적으라고 알린다.
- 비싼 모델(사용자 결정: 이유는 `description` 에): 고른 `model` 이 상한보다 비싼 등급에 속하면 막는다. 단 `description` 에 `[over-tier: <비어 있지 않은 이유>]` 가 있으면 통과시키고 그 이유를 기록에 남긴다. 표의 어느 등급에도 없는 모델은 비용을 판단할 수 없으므로 상한보다 비싼 것으로 본다.
- 에포트는 채우기만 하고 상한 판단에는 쓰지 않는다(완료 기준이 "비싼 모델" 만 말한다).
- 기록: `SubagentStop` 때 `.stage/.runtime/model-usage/<session>.jsonl` 에 한 줄을 쓴다: 시각, `session_id`, `agent_id`, `agent_type`, 현재 카드 id 들, 기대 등급, 실제 모델, 실제 에포트. 통과시킨 over-tier 호출은 PreToolUse 때 같은 파일에 이유와 함께 한 줄을 쓴다.
- 훅은 실패해도 도구 호출을 깨뜨리지 않는다. 설정·기록을 읽거나 쓰다 오류가 나면 아무것도 출력하지 않는다.

### 감사

- 설정 검사: `model_tiers`·`tier_routing` 모양이 틀렸거나 없는 등급을 가리키면 오류. 카드의 `tier:` 가 `model_tiers` 에 없는 이름이면 오류.
- 드라이버 기록: current 카드의 작업 기록에서 마지막 `Model tier (JSON)` 줄을 읽는다. 그 `tier` 가 카드의 지금 `tier` 와 다르거나, 넘긴 모델·에포트가 지금 표의 값과 다르거나, 명령이 환경 변수를 참조하지 않았으면 경고한다. 경고에는 카드 id 와 기대값·실제값을 함께 적는다.
- 하위 에이전트 기록: `model-usage` 줄의 실제 모델·에포트가 기대 등급의 claude 칸 값과 다르면 경고한다. 같은 세션에 같은 모델의 over-tier 이유가 있으면 그 이유를 경고에 함께 적는다.
- 모델 비교 규칙: 실제 모델 id(예: `claude-haiku-5-5`)에 표의 별칭(예: `haiku`, `[...]` 꼬리표는 떼고)이 들어 있으면 같은 것으로 본다.
- `model_tiers` 가 없으면 이 검사들은 아무 경고도 내지 않는다.

## Probe evidence

### 확인한 사실

오케스트레이터 세션(2026-11-14, Claude Code 2.1.321, `claude -p` 세 번):
- 훅에 들어오는 도구 이름은 `Agent` 다.
- model·effort 를 적은 호출의 `tool_input` 키는 `description, effort, model, prompt, run_in_background, subagent_type` 이고 값이 그대로 들어온다.
- 적지 않은 호출에는 `model`·`effort` 키가 아예 없다.
- `updatedInput` 으로 빠진 `model: "haiku"` 를 채우면 하위 에이전트가 `claude-haiku-5-5` 로 돈다. 채우지 않으면 부모 모델을 물려받아 `claude-fable-5-2` 로 돈다. `updatedInput` 은 입력 전체를 바꾸므로 원래 키를 모두 담아야 한다.
- `SubagentStop` 입력 맨 위 `effort.level` 에 실제 에포트가 있다. 실제 모델은 입력에 없고 `agent_transcript_path` 파일의 assistant 줄 `message.model` 에 있다.

이 세션(2026-11-14, Claude Code 2.1.321, 부모 `--model haiku`, scratchpad 시험 프로젝트에서 두 번):
- `permissionDecision` 없이 `hookSpecificOutput.updatedInput` 과 `additionalContext` 만 내도 채움이 적용됐다. `model: "sonnet"` 을 채우자 하위 에이전트가 `claude-sonnet-5-5` 로 돌았다.
- `effort` 도 채움이 적용된다. `effort: "low"` 를 채우면 `SubagentStop` 의 `effort.level` 이 `low`, `"high"` 를 채우면 `high` 였다. 부모 설정과 다른 값이 그대로 나왔으므로 채운 값이 적용된 것이다.
- `SubagentStop` 입력 키: `agent_id, agent_transcript_path, agent_type, background_tasks, cwd, effort, hook_event_name, last_assistant_message, permission_mode, prompt_id, scratchpad_dir, session_crons, session_id, stop_hook_active, transcript_path`. Agent 호출의 `description` 은 들어 있지 않다.

### 확인하지 않은 사실

- Agent 도구가 `opus[1m]` 같은 꼬리표 붙은 모델 값을 받는지. 받지 않는다고 보고 설계했다(enum 에 없다).
- 에이전트 정의 파일의 `model`·`CLAUDE_CODE_SUBAGENT_MODEL`·`CLAUDE_CODE_EFFORT_LEVEL` 이 훅이 채운 값과 겹칠 때 무엇이 이기는지. 공식 문서(https://code.claude.com/docs/en/sub-agents)는 `CLAUDE_CODE_EFFORT_LEVEL` 이 Agent 입력 `effort` 보다 우선한다고 적는다.
- Stage 의 PreToolUse 훅(matcher `*`)과 다른 플러그인 훅이 같은 Agent 호출에 각자 `updatedInput` 을 낼 때의 동작.

## Scope

### Included

- 이 카드 본문(설계와 실측 사실)

### Excluded

- 코드 변경 (W-00000328~331 몫)

## Risks

- 실측은 한 버전(2.1.321)에서만 했다. 다른 버전에서 입력 모양이 다를 수 있다.

## Success criteria

- 카드 본문만 읽고도 등급 표·tier_routing·카드 tier·환경 변수·훅·감사가 각각 무엇을 읽고 쓰는지, 그리고 claude -p 실측으로 확인한 사실과 확인하지 않은 사실이 무엇인지 알 수 있다

## Next action

감사로 확인하고 닫는다. 그다음 W-00000328 부터 드라이버로 돌린다.

## Related truth


## Progress


## Verification


### Executed at close — 2026-11-14

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective


## Promotion decision
