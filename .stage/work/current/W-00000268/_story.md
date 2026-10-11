---
id: W-00000268
title: 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다
kind: fix
venue: codex
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

# W-00000268 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다

## Purpose

카드 폴더에 둔 증거 파일이 보관과 함께 말없이 사라지지 않게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 카드 폴더에 .md 가 아닌 파일이나 하위 폴더가 있는 카드를 보관하면 그 파일이 보관함의 같은 상대 위치에 그대로 남는다는 것을 테스트가 확인한다
- 기록 파일은 지금처럼 status archived 로 바뀌고 기존 보관 테스트가 모두 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
