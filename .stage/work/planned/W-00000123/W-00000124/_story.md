---
id: W-00000124
title: 버전을 카드가 아니라 릴리스가 정한다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/CHANGELOG.md, stage/skills/, CLAUDE.md
---

# W-00000124 버전을 카드가 아니라 릴리스가 정한다

## Purpose

DE-00000040 §1. 플러그인 카드가 버전을 올리지 않는다 — CHANGELOG 의 미출시 절에만 적고, 릴리스 명령이 버전을 정해 매니페스트 둘을 고친다. 이것이 병렬을 여는 열쇠다: 두 카드가 같은 다음 버전을 집는 충돌이 사라지고, 무엇보다 도는 동안 버전이 안 바뀌어 마켓플레이스 재당김이 돌던 작업을 죽이는 사고(P-00000001, 오늘 두 번)가 원천 차단된다. CLAUDE.md 의 Plugin Changes 규칙을 같이 고친다 — 사용자 확인 완료(2026-07-29).

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
