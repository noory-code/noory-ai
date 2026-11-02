---
id: W-00000318
title: 실행을 요구하는 기준의 판정에 실제로 돌렸는지를 남긴다
kind: fix
venue: claude
environment: cloud
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
scope: .stage/settings.json, stage/templates/v4/project-stage/settings.jsonc, stage/scripts/tests/test_template_v4.py, .stage/state/observations/O-00000055.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000318 실행을 요구하는 기준의 판정에 실제로 돌렸는지를 남긴다

## Purpose

리뷰어가 실행을 요구하는 기준을 돌리지 않고 통과시켜도, 판정 사유만 보고 그 사실을 알 수 있게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 리뷰 명령 여섯 개와 v4 템플릿 안내가 모두, 실행이나 동작 관찰을 요구하는 기준이면 실제로 돌린 명령과 결과 또는 돌리지 않았다는 사실을 판정 사유에 적으라고 요구한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
