---
id: W-00000301
title: 보관한 뒤 대기 결정 목록을 옮겨진 카드에 맞춘다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-archive/archive_work.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000301 보관한 뒤 대기 결정 목록을 옮겨진 카드에 맞춘다

## Purpose

결정을 소유한 카드를 보관해도 대기 결정 목록이 옮겨진 카드를 가리켜 보관 직후 감사가 깨지지 않게 한다.

## Actions

- 지금 동작: `archive_work.py` 는 소진되는 venue 예외가 있을 때만 대기 결정 목록을 다시 그리고, 그것도 카드를 옮기기
  전에 그린다. 그래서 정책 결정처럼 소진되지 않는 대기 결정을 소유한 카드를 보관하면, 목록이 예전 경로를 가리키고
  감사가 DECISION004 를 낸다(2026-10-31 W-00000292 와 DE-00000082 보관에서 실제로 일어났다).
- 보관이 끝난 뒤 대기 결정 목록을 한 번 다시 그린다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 소진되지 않는 대기 결정을 소유한 카드를 보관하면 대기 결정 목록이 보관된 카드의 경로와 상태를 가리키고 감사가 통과한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
