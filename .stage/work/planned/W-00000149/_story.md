---
id: W-00000149
title: 시도가 오르면 드라이버가 등급을 올려 부른다
kind: fix
venue:
milestone:
status: captured
priority: 2
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/templates/, stage/docs/, stage/CHANGELOG.md
---

# W-00000149 시도가 오르면 드라이버가 등급을 올려 부른다

## Purpose

W-00000147 이 정할 결정을 코드로 옮긴다. 시도가 오르면 드라이버가 같은 명령을 다시 부르지 않고
한 등급 위 명령으로 부른다. 등급을 선언하지 않은 프로젝트는 지금과 똑같이 돈다.

**W-00000148 과 같은 설정 항목을 건드린다** — `executors` 두 벌, `review.reviewers` 두 벌,
`review.strengths` 네 벌, 템플릿 `settings.jsonc`, `drive.py`. 한 바퀴에 같이 돌리는 것이 기본이다.

시작 전 조건: W-00000147 의 결정이 `decided` 여야 한다.


## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
