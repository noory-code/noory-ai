---
id: W-00000349
title: --scope 를 여러 번 넘기면 모든 경로를 카드에 담기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_register_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_work.py, stage/skills/stage-work/register_work.py, stage/scripts/start_work.py, stage/scripts/tests/test_register_work.py, stage/skills/stage-work/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000349 --scope 를 여러 번 넘기면 모든 경로를 카드에 담기

## Purpose

register_work 와 start_work 에 --scope 를 여러 번 넘기면 경고 없이 마지막 경로만 카드에 남는 것을 고쳐, 넘긴 경로가 모두 카드 범위에 들어가게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- register_work 에 --scope 를 두 번 넘기면 카드의 scope 줄에 두 경로가 모두 쉼표로 이어져 들어간다.
- start_work 에 --scope 를 두 번 넘겨도 두 경로가 모두 카드에 들어간다.
- 쉼표로 이은 값 하나를 넘기는 기존 방식은 그대로 동작한다.

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
