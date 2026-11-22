---
id: W-00000387
title: 다른 브랜치에서 이미 시작했거나 끝난 카드는 시작하지 않는다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 5
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/start_work.py,stage/scripts/tests,stage/CHANGELOG.md
---

# W-00000387 다른 브랜치에서 이미 시작했거나 끝난 카드는 시작하지 않는다

## Purpose

두 세션이 같은 카드를 따로 하는 일이 시작하는 순간에 막힌다

## Actions


## User value

DE-00000094 의 "맡은 카드 표시"를 구현한다. 2026-11-21 에 메인 세션이 main 만 받아 온 채로 W-00000367 을 시작했는데, 그 카드는 `claude/w367-parallel-session-collisions` 브랜치에서 이미 닫히고 보관되어 있었다. `stage_record_ids.py` 가 이미 받아 온 모든 브랜치에서 번호를 세는 방식을 참고한다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 받아 온 다른 브랜치에서 같은 카드가 active 이거나 보관된 상태면 start_work.py 가 시작하지 않고 그 브랜치 이름을 출력하는 시험이 있고 통과한다
- 다른 브랜치에 같은 카드가 계획된 상태로만 있으면 지금처럼 시작된다

## Next action
