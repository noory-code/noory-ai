---
id: W-00000405
title: 뺀 장치의 하중을 커밋된 기록으로 잴 수 있게 한다
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
scope: stage/scripts,stage/skills,stage/operations,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md,.stage/research/claude-fit
promotes:
decision_refs:
---

# W-00000405 뺀 장치의 하중을 커밋된 기록으로 잴 수 있게 한다

## Purpose

장치를 하나 뺐을 때 그 장치가 하중을 받고 있었는지, 클라우드 작업 세션으로 도는 지금의 흐름에서도 커밋된 기록만으로 알 수 있다

## Actions


## User value


## Scope

### Included

- `.stage/research/claude-fit/mechanisms.md` 의 B11 행에 Dasina 사고 출처(R-00000028, R-00000031)를 적는다(W-00000403 의 후속 후보).
- DE-00000101 이 정한 판정 방법 칸과 리뷰어 권한은 다음 카드가 만든다. 이 카드는 지금의 판정 기록에서 남길 수 있는 것을 남긴다.


### Excluded

- 빼기 전 기준선을 Mac 의 `.stage/.runtime/driver/logs/` 에서 세는 일. 사용자의 기계가 필요하다.
- 빼기 실험을 시작하기 전에 잴 수 있는지 확인하는 절차. R-00000403 의 규칙 후보로 남기고 한 번 더 관찰되면 올린다.

## Risks


## Success criteria

- 카드 한 장이 닫힐 때 시도 수, 리뷰 FAIL 회차, 실패 기록이 커밋되는 자리에 남는다
- 그 기록으로 W-00000403(B11) 이후에 닫힌 카드들의 수치를 표로 낼 수 있고, .stage/research/claude-fit/b11-load.md 의 결과 표가 그 수치로 채워진다

## Next action

## Related truth

- W-00000403 과 R-00000403: 빼기 전후 비교를 이 카드로 옮겼다.
- DE-00000098, `.stage/research/claude-fit/b11-load.md`
- 사용자가 2026-11-23 에 목적("잴 수 있는지부터 정하기")과 성공 기준 두 개를 정했다("네 추천대로 1, 2만 등록하죠").

## Progress

## Verification
