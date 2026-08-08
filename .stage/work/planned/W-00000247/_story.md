---
id: W-00000247
title: 인라인 인터프리터를 셸 인자로 넘겨도 게이트가 걸리게 한다
kind: design
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/hooks/, stage/hooks/tests/
---

# W-00000247 인라인 인터프리터를 셸 인자로 넘겨도 게이트가 걸리게 한다

## Purpose

게이트가 인라인 코드를 막는데 같은 코드를 셸 인자로 넘기면 안 걸리고, 반대로 읽기만 하는 인라인 코드는 이유 없이 막히므로, 무엇을 막고 무엇을 통과시킬지 실제 쓰임을 세어 정하고 그대로 걸리게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 이 저장소에서 인라인 인터프리터를 쓰는 정당한 자리가 몇 개인지 센 값이 남는다
- 셸 인자로 우회한 쓰기가 막히고, 읽기만 하는 쓰임은 안 막히는 것이 시험으로 잡힌다

## Next action

O-00000041 을 먼저 읽는다. 두 방향의 실패(쓰기가 인자로 빠져나가는 것, 읽기가 막히는 것)와
증거가 그 기록에 있다. 세는 일이 먼저다.
