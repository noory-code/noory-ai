---
id: W-00000383
title: 옛 목록 파일이 남은 프로젝트를 옮길 때 그 파일을 지운다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 8
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts,stage/CHANGELOG.md
---

# W-00000383 옛 목록 파일이 남은 프로젝트를 옮길 때 그 파일을 지운다

## Purpose

active.md, review.md, planned/index.md 가 남은 프로젝트를 새 버전으로 옮기면 그 파일이 지워져 감사 경고 INDEX007 이 남지 않는다

## Actions


## User value

W-00000377(DE-00000091)이 세 목록 파일을 없앴다. 이미 그 파일이 있는 다른 프로젝트는 새 버전에서도
파일이 그대로 남고, 감사가 파일마다 경고 INDEX007("지워라")을 낸다. 이관 스크립트(v3→v4, v4→v5)는 고치지 않았다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 세 목록 파일이 있는 프로젝트를 옮기면 세 파일이 지워지고 감사가 INDEX007 을 내지 않는다

## Next action
