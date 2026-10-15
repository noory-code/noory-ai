---
id: W-00000285
title: Codex 드라이버 명령에 gpt-6-sol 모델을 다시 적는다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage.scripts.tests.test_template_v4 -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: .stage/settings.json, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000285 Codex 드라이버 명령에 gpt-6-sol 모델을 다시 적는다

## Purpose

드라이버가 사용자 홈 설정과 상관없이 정해진 Codex 모델로 돌고, 그 사실을 지키는 Stage 시험이 다시 통과한다.

## Actions

1. `.stage/settings.json`에서 `executors.codex`, `review.reviewers.codex`, `review.strengths`의 `light`·`standard`·`deep`·`red-team` 명령 여섯 개의 `codex-companion.mjs" task` 뒤에 `--model gpt-6-sol`을 넣는다. 나머지 문장은 바꾸지 않는다. preflight·reaper 명령은 바꾸지 않는다.
2. `stage/scripts/tests/test_template_v4.py`의 `test_project_pins_the_current_model_in_all_eight_driver_commands`가 Codex 명령에 `--model gpt-6-sol`을 기대하게 한다.
3. `stage/CHANGELOG.md` Unreleased에 한 줄 적는다.

## User value

2026-10-12 커밋 `5dcc858d`가 Codex 명령의 모델 고정(`gpt-5.6-sol`, 용량 부족으로 거절됨)을 빼서 홈 설정을 따르게 했다. 그 뒤 Stage 시험 6개가 실패하고 있었다. 플러그인 템플릿은 "모든 명령에 모델을 직접 적고 홈 기본값에 기대지 않는다"고 한다. 사용자가 2026-10-15 지금 홈 설정의 모델인 `gpt-6-sol`로 다시 고정하기로 정했다.

## Scope

### Included


### Excluded


## Risks


## Success criteria

- 이 저장소 .stage/settings.json의 Codex 실행 명령, Codex 리뷰 명령, 리뷰 강도 명령 4개(light, standard, deep, red-team)가 모두 --model gpt-6-sol을 담고, Claude 명령 두 개는 지금처럼 --model 'opus[1m]'을 담는다
- test_template_v4의 모델 고정 시험이 gpt-6-sol을 기대하고, python3 -m unittest discover -s stage/scripts/tests -q 전체가 통과한다
- stage CHANGELOG Unreleased에 이 변경이 적힌다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
