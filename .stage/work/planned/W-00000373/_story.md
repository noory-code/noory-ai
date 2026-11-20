---
id: W-00000373
title: 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다
kind: fix
maintenance: true
venue:
milestone:
status: captured
priority: 4
autonomous: false
acceptance: []
review: not_required
scope: stage/hooks,stage/CHANGELOG.md
---

# W-00000373 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다

## Purpose

세션 시작 글이 상태가 selected 인 계획 카드를 보여 주지 않고 오늘 연 관찰을 open -1d 로 보여 준다

## Actions


## Scope

### Included


### Excluded


## Success criteria

- 상태가 selected 인 폴더 카드(_story.md, _epic.md)가 세션 시작 글의 Selected backlog 에 나온다
- 한국 시각으로 오늘 연 관찰이 UTC 날짜가 하루 앞이어도 open 0d 로 나온다
