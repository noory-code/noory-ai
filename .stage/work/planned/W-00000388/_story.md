---
id: W-00000388
title: 메인 세션이 서브세션에 일을 맡기고 닫는 절차와 번호 묶음을 만든다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 5
autonomous: false
acceptance: []
review: not_required
scope: stage/skills/stage-handoff/SKILL.md,stage/operations/cloud-execution.md,stage/scripts/stage_record_ids.py,stage/scripts/tests,.stage/operations/parallel-sessions.md,stage/CHANGELOG.md
---

# W-00000388 메인 세션이 서브세션에 일을 맡기고 닫는 절차와 번호 묶음을 만든다

## Purpose

메인 세션이 프롬프트를 손으로 쓰지 않고 Stage 절차대로 서브세션에 카드를 맡기고, 번호가 겹치지 않고, 돌아온 결과를 메인 세션이 닫는다

## Actions


## User value

DE-00000094 를 구현한다. 그 결정의 "Where this applies" 표에 고칠 자리가 있다. 서브세션은 만들기만 하고, 카드의 시작과 닫기와 보관은 메인 세션이 한다. 번호 묶음은 다른 세션이 fetch 한 뒤 쓰인 번호로 셀 수 있는 자리에 남겨야 한다. 2026-11-21 에 메인 세션이 서브세션 프롬프트에 손으로 적었던 것(번호를 고르지 말 것, 보고 형식, 닫기 방법)이 이 절차로 옮겨 와야 한다. W-00000387 이 먼저 끝나면 그 검사를 절차에 쓴다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 메인 세션이 남긴 번호 묶음을 다른 체크아웃의 stage_record_ids.py 가 fetch 뒤에 쓰인 번호로 세는 시험이 있고 통과한다
- stage-handoff 스킬에 서브세션에 맡기기, 보고 형식, 메인 세션의 닫기가 적혀 있다
- 서브세션 하나에 카드를 맡겨 이 절차대로 메인 세션이 닫은 기록이 카드에 있다

## Next action
