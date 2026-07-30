---
id: W-00000151
title: decision_refs 가 무엇을 담는 칸인지 문서가 말한다
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

# W-00000151 decision_refs 가 무엇을 담는 칸인지 문서가 말한다

## Purpose

DE-00000046 이 정한 것을 문서에 싣는다. **`decision_refs` 는 그 카드가 확정한 결정만 담고, 남의
결정에 구속받는 카드는 본문에서 링크한다.**

규칙 자체는 코드에 이미 있었다(감사 WORK015). 없던 것은 그 뜻을 적은 문서다. 그래서 하루에 카드
셋이 그 규칙을 모르고 쓰였고, 다른 프로젝트는 감사 오류를 못 고치고 남겨 뒀다. **문서가 없으면
규칙이 옳아도 사람은 다르게 쓴다.**

## 적어야 할 자리

- `stage/docs/` 의 작업 카드 서술 — `decision_refs` 의 뜻과 주인 규칙.
- `stage/skills/stage-work/SKILL.md` — 등록할 때 무엇을 적는지.
- `stage/skills/stage-retrospective/SKILL.md` — 결정을 확정하며 닫는 카드가 주인이 된다는 것.
- `stage/templates/` 의 카드 템플릿에 주석 자리가 있으면 같은 문장.
- `stage/CHANGELOG.md` 미출시 절.

## Success criteria

- 위 네 자리에 같은 규칙이 적힌다. **한 자리라도 빠지면 다음 사람이 빠진 쪽을 읽는다.**
- 문서가 "왜 1:N 이 아닌가"도 한 줄 적는다 — venue 예외 검사가 같은 연결에 매달려 있다.
- 코드는 안 바꾼다. 규칙은 이미 맞다.


## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
