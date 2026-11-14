---
id: W-00000329
title: 드라이버가 카드 등급의 모델과 에포트를 실행기와 리뷰어에 넘긴다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_driver_model_tier.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
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

W-00000328 이 끝난 뒤 드라이버가 Codex 실행기로 돌린다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
