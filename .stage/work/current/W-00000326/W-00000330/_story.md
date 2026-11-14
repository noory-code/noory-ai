---
id: W-00000330
title: Agent 호출의 모델과 에포트를 카드 등급에 맞추는 훅을 넣는다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_agent_tier.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
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

W-00000328 이 끝난 뒤 드라이버가 Codex 실행기로 돌린다. 실행기는 W-00000327 의 설계를 읽고 `stage_agent_tier.py` 와 시험부터 만든다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
