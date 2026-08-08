---
id: W-00000250
title: 무인 실행이 끝난 뒤 사람이 잇는 구간에서 게이트가 안 막게 한다
kind: design
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/, stage/hooks/, .stage/decisions/
---

# W-00000250 무인 실행이 끝난 뒤 사람이 잇는 구간에서 게이트가 안 막게 한다

## Purpose

하니스가 시킨 다음 걸음을 하니스가 막는다 — 카드를 거절한 실행자는 커밋에서 막히고 무인 결과를 병합할 때는 열린 작업이 없어 막히므로, 무인이 끝난 뒤 사람이 손으로 잇는 구간을 하니스가 알아보게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 카드만 고치고 거절한 실행이 커밋 실패가 아니라 거절로 읽힌다
- 무인 결과 병합이 열린 작업 없이도 통과한다

## Next action

O-00000034 와 O-00000035 를 먼저 읽는다. 각각 고칠 길 셋이 적혀 있고 아직 안 골랐다. 두 기록이
같은 구간을 가리키므로 한 결정으로 묶인다.
