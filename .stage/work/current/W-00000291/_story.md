---
id: W-00000291
title: 병렬 브랜치가 같은 기록 번호를 쓰지 않게 한다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/stage_record_ids.py, stage/scripts/tests/test_stage_record_ids.py, stage/skills/stage-work/register_work.py, stage/scripts/tests/test_register_work.py, stage/skills/stage-decision/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000081
---

# W-00000291 병렬 브랜치가 같은 기록 번호를 쓰지 않게 한다

## Purpose

여러 세션이 다른 브랜치에서 동시에 일해도 새 카드와 결정이 이미 쓰인 번호를 다시 쓰지 않게 한다.

## Actions

- 지금 동작: `register_work.py` 의 `existing_numbers()` 는 지금 체크아웃의 카드만 세어 다음 W 번호를 고른다.
  결정(DE)과 관측(O) 번호는 도구 없이 손으로 고른다. 2026-10-31 병렬 브랜치에서 W-00000286 과
  DE-00000076 이 실제로 겹쳤다.
- `stage/scripts/stage_record_ids.py` 가 지금 체크아웃과 모든 로컬·원격 추적 브랜치의 `.stage/` 에서 한
  접두사(W, DE, O 등)의 번호를 세고 다음 번호를 알려 준다. 브랜치는 이미 받아 둔 것만 본다.
- `register_work.py` 가 자동으로 번호를 고를 때 이 번호들을 함께 센다. 직접 준 `--id` 가 지금 체크아웃에
  없고 다른 브랜치에 있으면 그 브랜치 이름과 함께 거절한다. 지금 체크아웃에 있는 카드를 다시 등록하는
  재실행은 지금처럼 인덱스만 맞춘다.
- `stage/skills/stage-decision/SKILL.md` 가 결정 번호를 이 도구로 고르라고 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

여러 세션을 병렬로 돌려도 번호를 손으로 다시 매기거나 합칠 때 충돌을 풀 일이 줄어든다.

## Scope

### Included


### Excluded

- 원격을 새로 받아 오는 일(`git fetch`). 도구는 네트워크를 쓰지 않는다.
- 아직 push 하지 않은 다른 컴퓨터의 번호 — 볼 방법이 없다.

## Risks


## Success criteria

- 다른 로컬 또는 원격 브랜치에 이미 있는 W 번호를 등록 도구가 고르지 않고, 그 번호를 직접 주면 거절한다는 것을 테스트가 확인한다
- 결정과 관측 같은 다른 기록의 다음 번호를 브랜치를 넘어 알려 주는 도구가 있고, 결정 절차가 그 도구로 번호를 고르라고 적는다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
