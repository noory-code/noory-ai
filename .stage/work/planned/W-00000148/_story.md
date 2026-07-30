---
id: W-00000148
title: 두 번째 바퀴의 리뷰를 좁힌 범위로 돌린다
kind: fix
venue:
milestone:
status: captured
priority: 1
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/templates/, stage/docs/, stage/CHANGELOG.md
---

# W-00000148 두 번째 바퀴의 리뷰를 좁힌 범위로 돌린다

## Purpose

W-00000146 이 정할 결정을 코드로 옮긴다. 두 번째 바퀴부터 리뷰가 지난 판정에서 통과한 기준을
이어받고, 다시 보는 것은 지난 판정에서 어긋난 기준과 그 사이 바뀐 구간으로 좁힌다.

**W-00000149 와 같은 설정 항목을 건드린다** — `.stage/settings.json` 의 `review.reviewers` 두 벌과
`review.strengths` 네 벌, 템플릿의 `settings.jsonc`, `drive.py` 의 리뷰 단계. 두 카드를 따로 돌리면
같은 줄을 두 번 고치고 두 번째가 첫 번째를 덮을 위험이 있다. **한 바퀴에 같이 돌리는 것이 기본이고,
따로 돌릴 이유가 생기면 그때 순서를 정한다.**

시작 전 조건: W-00000146 의 결정이 `decided` 여야 한다. 결정 없이 시작하면 실행자가 판정 파일의
모양을 스스로 정한다.


## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
