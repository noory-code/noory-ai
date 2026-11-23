---
id: W-00000408
title: 닫기 리뷰어가 실행해서 판정하고 판정 방법이 카드에 남는다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts,stage/skills,stage/operations,stage/templates,.stage/settings.json,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000408 닫기 리뷰어가 실행해서 판정하고 판정 방법이 카드에 남는다

## Purpose

리뷰어가 기록만 읽고 승인하는 일이 없어진다: 실행이 필요한 기준은 리뷰어가 직접 실행해서 판정하고, 무엇으로 판정했는지가 커밋된 카드에 남는다 (DE-00000101)

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 대역 리뷰어가 카드의 검사 명령(예: audit_stage.py)과 스스로 고른 명령을 실행할 수 있고, 프로젝트 파일을 고친 리뷰는 지금처럼 닫기가 실패시킨다
- 판정 파일이 기준마다 판정 방법을 담고, 실행이 필요한 기준을 실행하지 못한 판정이면 닫기가 실패하며, 기준별 판정 방법이 카드에 남는다
- 설정과 템플릿의 리뷰 명령이 근거를 직접 보지 못한 기준은 FAIL 이라고 말하고, 닫기가 이미 돌린 검사의 반복 대신 리뷰어 자신의 탐침을 요구한다
- stage-orchestrate 와 검증 브리핑이 검증 세션은 닫기의 관문이 아니며 세션에서만 볼 수 있는 기준이 있을 때만 띄운다고 말한다

## Next action


## Related truth


## Progress


## Verification
