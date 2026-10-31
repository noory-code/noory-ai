---
id: W-00000286
title: 닫기 리뷰가 판정 파일을 쓰게 하고 Codex 명령을 gpt-6-astra high로 고정한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/settings.json, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000286 닫기 리뷰가 판정 파일을 쓰게 하고 Codex 명령을 gpt-6-astra high로 고정한다

## Purpose

close_work 로 리뷰가 필요한 카드를 닫을 때 Codex 리뷰어가 판정 파일을 직접 써서 닫기가 통과하고, 드라이버와 리뷰의 Codex 명령이 사용자가 정한 gpt-6-astra 모델과 high 생각 깊이로 돈다.

## Actions

- 지금 동작: `.stage/settings.json` 의 `review.strengths` 프로필 명령 네 개(`light`, `standard`,
  `deep`, `red-team`)는 `codex-companion.mjs task ... --fresh` 로 돌고 `--write` 가 없다.
  `--write` 가 없으면 Codex 가 읽기 전용으로 돌아 `$STAGE_REVIEW_VERDICT_FILE` 을 쓰지 못한다.
  `close_work.py` 는 `review: pending` 카드를 닫을 때 `review.stages.implementation`
  (`standard`) 명령을 부르므로, 지금은 리뷰가 승인해도 "review verdict file is missing" 으로
  닫기가 막힌다. 2026-10-31 W-00000268 닫기에서 실제로 이렇게 막혔다.
- 드라이버용 리뷰 명령 `review.reviewers.codex` 에는 2026-08-03 커밋 `e4e96af9` 에서
  `--write` 가 들어갔다. 프로필 명령 네 개에는 2026-07-12 처음 생길 때부터 없었다.
- 고칠 것 1: 프로필 명령 네 개의 `task` 인자에 `--write` 를 넣는다. 지시문 문장은 바꾸지 않는다.
- 고칠 것 2: Codex 명령 여섯 개의 `--model gpt-6-sol` 을 `--model gpt-6-astra --effort high` 로
  바꾼다. 여섯 개는 `executors.codex`, `review.reviewers.codex`, `review.strengths` 의 네 개다.
  `preflights.codex` 와 `cancel` 명령은 모델을 쓰지 않으므로 그대로 둔다.
- 사용자가 2026-10-31 "코덱스 아스트라 하이로 적극 사용하세요" 라고 정했다. 이것은 2026-10-15
  `gpt-6-sol` 고정 결정(W-00000285)을 대신한다. 같은 날 `gpt-6-astra` 에 `--effort high` 를 준
  companion task 호출이 정상 응답을 돌려준 것을 확인했다.
- `stage/scripts/tests/test_template_v4.py` 의
  `test_project_pins_the_current_model_in_all_eight_driver_commands` 기대값을 고친다. Codex 명령
  여섯 개에 `--model gpt-6-astra` 와 `--effort high` 가 모두 있는지 본다. 프로필 명령 네 개에
  `--write` 가 있는지 보는 시험을 더한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다(영어).

## User value

리뷰가 필요한 카드를 `close_work.py` 로 닫을 수 있다. W-00000268·W-00000269·W-00000270 이 모두
이 길로 닫힌다. Codex 실행과 리뷰가 사용자가 고른 모델과 깊이로 돈다.

## Scope

### Included

- 프로필 리뷰 명령 네 개가 판정 파일을 쓸 수 있게 하는 것
- Codex 명령 여섯 개의 모델과 생각 깊이
- 그 두 가지를 지키는 시험과 변경 기록 한 줄

### Excluded

- Claude 명령 두 개(`executors.claude`, `review.reviewers.claude`)의 모델
- 지시문 문장, 리뷰 단계 설정(`review.stages`), 시도 한도(`limits`)
- `stage/templates/` 의 설정 템플릿. 이 카드는 이 저장소 설정만 바꾼다.
- `close_work.py` 의 리뷰 제한 시간(W-00000270 몫)

## Risks

- 이 카드를 드라이버로 돌리는 동안 실행자가 `executors.codex` 를 바꾸면, 두 번째 시도부터는 바뀐
  모델로 돈다. `gpt-6-astra` 호출은 확인했으므로 실패 원인이 되지는 않는다.
- 리뷰어에게 쓰기 권한을 주면 리뷰어가 판정 파일 말고 다른 파일도 고칠 수 있다. 드라이버 리뷰
  명령은 이미 `--write` 로 돌고 있고, `close_work.py` 는 HEAD 커밋의 경로만 리뷰 대상으로 넘긴다.

## Success criteria

- 닫을 때 쓰는 리뷰 프로필 명령 네 개(light, standard, deep, red-team)가 모두 --write 를 가져 판정 파일을 쓸 수 있다는 것을 시험이 확인한다
- Codex 명령 여섯 개(실행, 드라이버 리뷰, 프로필 리뷰 네 개)가 모두 --model gpt-6-astra --effort high 로 돈다는 것을 시험이 확인하고, Claude 명령 두 개의 모델 고정은 그대로다

## Next action

Codex 드라이버로 실행한다. 닫을 때 `close_work.py` 의 `standard` 리뷰가 고친 명령으로 처음
돈다. 판정 파일이 써져 닫기가 통과하면 그것이 끝에서 끝까지 확인한 증거다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
