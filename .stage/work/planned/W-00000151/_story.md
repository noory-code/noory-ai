---
id: W-00000151
title: decision_refs 가 무엇을 담는지 문서에 적는다
kind: documentation
venue:
milestone:
status: captured
priority: 3
autonomous: false
acceptance: []
review: not_required
scope: stage/docs/, stage/skills/stage-work/SKILL.md, stage/skills/stage-retrospective/SKILL.md, stage/templates/, stage/CHANGELOG.md
---

# W-00000151 decision_refs 가 무엇을 담는지 문서에 적는다

## Purpose

작업 카드에는 그 카드가 내린 결정을 적어 두는 칸이 있다. 그 칸에 **무엇을 적는 것인지가 어디에도
안 적혀 있다.** 검사 프로그램은 "이 카드가 확정한 결정만"으로 보고 다른 것이 적히면 거절하는데,
쓰는 사람은 "이 카드가 따르는 결정"까지 적어도 되는 줄 안다.

그래서 하루에 카드 셋이 그 칸을 잘못 채웠다. 이 저장소에서 두 번, 다른 프로젝트에서 한 번이다.
그 프로젝트는 검사 오류를 고치지 못하고 그대로 남겨 뒀다.

규칙 자체는 맞다. **문서가 그 뜻을 안 적어 뒀을 뿐이다.** 규칙이 코드에만 있으면 사람은 다르게
쓴다.

## Actions

문서 네 곳에 같은 두 문장을 넣는다.

- 그 칸에는 **이 카드가 확정한 결정만** 적는다.
- 다른 카드가 내린 결정을 따르는 경우에는 그 칸이 아니라 카드 본문에서 링크한다.

넣을 곳: 작업 카드를 설명하는 문서, 카드를 등록하는 절차 문서, 카드를 닫는 절차 문서, 카드
템플릿의 주석. 그리고 변경 이력에 한 줄.

## User value

카드를 쓰는 사람이 그 칸을 열 때마다 짐작하지 않는다. 지금은 잘못 채운 뒤 검사에서 막히고, 막힌
카드가 이미 보관돼 있으면 고치기도 어렵다.

## Scope

### Included

`stage/docs/`, 카드 등록 스킬(`stage/skills/stage-work/SKILL.md`), 카드 닫기 스킬
(`stage/skills/stage-retrospective/SKILL.md`), `stage/templates/`, `stage/CHANGELOG.md`.

### Excluded

검사 프로그램은 안 건드린다. 규칙이 맞다.

## Risks

네 곳 중 한 곳만 빠져도 값이 안 난다. 다음 사람이 하필 빠진 쪽을 읽는다.

## Success criteria

- 위 네 곳 **전부**에 같은 두 문장이 있다.
- 문서가 "왜 여러 카드가 한 결정을 적으면 안 되는가"도 한 줄 답한다. 이유는 안전 검사다 — 정책을
  벗어난 실행 창을 한 번 허가할 때, 그 허가가 어느 카드의 것인지를 바로 이 연결로 특정한다.
  여러 카드가 한 결정을 적을 수 있게 되면 카드 하나에 준 허가를 다른 카드가 주장할 수 있다.
- 그 두 문장을 처음 읽는 사람이 **다른 파일을 안 열고** 무엇을 적어야 하는지 안다.

## Next action
