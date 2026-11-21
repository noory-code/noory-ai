---
id: W-00000366
title: 도면의 위 두 층을 쓰고 도면 자리를 한 곳으로 정한다
kind: documentation
venue:
milestone: M-00000005
status: selected
priority: 5
autonomous: false
acceptance: []
review: not_required
scope: .stage/official/model,stage/docs/BLUEPRINT.md,stage/README.md,stage/CHANGELOG.md
---

# W-00000366 도면의 위 두 층을 쓰고 도면 자리를 한 곳으로 정한다

## Purpose

AI 가 문서 한 장에서 Stage 의 목표와 레이어와 코드가 말해 주지 않는 것을 읽는다

## Actions


## User value

2026-11-20 에 사용자와 정한 것이다.

- 설계는 둘이다. 일에 대한 계획은 카드와 함께 사라져도 된다. 시스템 도면은 남아야 하고 한곳에 모여야 한다.
- 도면은 층으로 나눈다: 목표, 레이어, 컴포넌트, 컴포넌트 설계. 손으로 쓸 것은 위 두 층과 코드가 말해 주지
  않는 것이다. 아래층은 결정 기록과 코드 위치로 가는 링크만 둔다.
- 레이어 초안: 기록 / 경로와 규칙 / 관문 / 절차 / 검증 / 드라이버 / 점검. 점검(기록이 계약대로인가)과
  검증(일이 목적에 닿았나)은 다른 레이어다.
- 초안을 쓰다 찾은 것: 공용 모듈이 `stage/hooks/` 에 있고 스크립트 46개 가운데 33개가 가져다 쓴다. 이유는
  모른다. `drive.py` 와 `close_work.py` 가 서로를 가져다 쓴다.
- `.stage/official/model/` 에는 빈 양식만 있다. 도면을 올린 적이 없다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 문서 한 장에 목표로 가는 링크와 레이어 일곱 개의 표와 코드가 말해 주지 않는 것이 있다
- 공용 모듈이 hooks 폴더에 있는 이유와 drive.py 와 close_work.py 가 서로를 가져다 쓰는 이유가 적혀 있거나 그 결정 기록으로 가는 링크가 있다
- 도면 노릇을 하는 자리가 한 곳이고 다른 자리는 그곳을 가리킨다

## Next action
