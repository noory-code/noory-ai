---
id: W-00000409
title: 세션의 맨 위 층이 기록에서 만든 색인을 싣는다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks,stage/scripts,stage/skills,stage/operations,stage/templates,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md,.stage/decisions/index.md,.stage/research/README.md,.stage/work/current/_story.md,.stage/work/current/_epic.md,.stage/work/current/_template.md
promotes:
decision_refs:
---

# W-00000409 세션의 맨 위 층이 기록에서 만든 색인을 싣는다

## Purpose

기기의 세션과 클라우드 세션이 같은 작은 색인을 맨 위 층으로 받고, 필요한 결정과 기록의 본문을 거기서 찾아 꺼내 쓴다 (DE-00000100)

## Actions


## User value


## Scope

### Included

- DE-00000100 의 "Where this applies" 표의 줄. 색인을 쓰는 코드 가운데 실제로 줄을 쓰는 곳은 이 카드가 가린다.


### Excluded

- 매번 같은 규칙 문장을 줄이는 일. M-00000006 의 (가)가 빼 보며 판정한다. 줄이지 못해 결정 제목이 다 실리지 않으면 그렇다고 보고한다.
- 규칙 후보 66건의 첫 정리와 정리 세션을 실제로 띄우는 일.
- 작업 로그 원문을 커밋하는 일.


## Risks


## Success criteria

- 세션 시작에 싣는 글이 읽을 때 기록에서 만든 색인이고 본문을 싣지 않으며, 전체가 10,000자를 넘지 않는다
- 상한을 넘을 때는 지금 하는 일을 남기고 오래된 결정 제목부터 덜어내며, 덜어낸 건수와 읽을 자리를 한 줄로 남긴다
- 클라우드 작업 세션의 브리핑이 훅과 같은 색인을 받는다
- 결정 색인이 결정마다 제목을 싣는다
- 카드에 그 일을 한 세션의 번호를 적는 자리가 있고, 외부 자료의 자리(research/<주제>/sources.md)와 규칙 후보 정리 세션을 띄우는 때와 그 경계(본문을 고치지 않고 제안까지만)가 절차에 적혀 있다

## Next action

작업 세션 session_018VXR6P2o521MckQ6RaB1e7 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.


## Related truth

- DE-00000100, `.stage/research/memory-layers/`, W-00000400
- 알고 고른 약점: 상한 10,000자는 잰 값이 아니고, 색인의 효과를 잴 기록이 지금 없다. 세션이 실린 줄을 썼는지 잴 자리를 만들 수 있으면 만들고, 못 만들면 보고에 적는다.
- 클라우드 세션은 SessionStart 층을 받지 않는다(최근 닫힌 카드가 모두 클라우드다).
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 DE-00000100 에서 옮겨 적었다.


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 691b177a 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6P2o521MckQ6RaB1e7 (`claude/w409-top-layer-index`)를 띄웠다. 번호 묶음은 잡지 않았다.


## Verification
