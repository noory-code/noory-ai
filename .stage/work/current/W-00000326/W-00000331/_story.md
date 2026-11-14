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
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
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


## Verification


## Retrospective


## Promotion decision
