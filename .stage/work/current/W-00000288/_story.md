---
id: W-00000288
title: 상태 기록의 work_items 연결 검사가 계획 칸 카드도 센다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage
promotes:
decision_refs:
---

# W-00000288 상태 기록의 work_items 연결 검사가 계획 칸 카드도 센다

## Purpose

STATE001(audit_state_links)이 상태 기록의 work_items 를 진행 중·보관 카드에만 대조해 계획 칸 카드를 가리키는 상태 기록을 없는 카드로 보고하는데, operations/artifacts.md 는 상태 기록이 관련 카드를 잇는 것을 막지 않고 상위 카드 검사(audit_stage.py:786)는 이미 계획 칸 카드를 세므로, 상태 기록 연결 검사도 계획 칸 카드를 세게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- work_items 가 work/planned/ 의 카드를 가리키는 상태 기록은 감사를 통과하고, 어디에도 없는 카드를 가리키면 여전히 STATE001 로 실패한다. scripts unittest 가 두 경우를 고정하고 hooks·scripts 시험이 모두 통과한다. novel-workspace 감사에서 Q-00000037 오류(계획 칸 W-00000437 연결)가 사라진다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
