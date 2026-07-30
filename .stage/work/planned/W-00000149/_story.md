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

DE-00000044 를 설정과 코드로 옮긴다. **범위가 처음 잡을 때보다 훨씬 작다** — 등급을 바꾸는 축은
안 만들기로 했다. 할 일은 드라이버가 부르는 명령에 모델을 못 박는 것이다: claude 쪽 `opus[1m]`,
codex 쪽 `gpt-5.6-sol`. 값은 지금 도는 것과 같고, 바뀌는 것은 그 값이 실행하는 사람의 홈
디렉터리가 아니라 프로젝트 설정에 적힌다는 점이다. 어느 명령으로 돌았는지 작업 로그에도 남긴다.

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
