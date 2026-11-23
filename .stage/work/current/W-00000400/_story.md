---
id: W-00000400
title: 세션 시작에 싣는 층을 작게 두고 기억을 잘 꺼내 쓰는 구조를 정한다
kind: design
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/research/memory-layers,.stage/decisions/pending/DE-00000100.md
promotes:
decision_refs:
reserved_ids: DE-00000100
---

# W-00000400 세션 시작에 싣는 층을 작게 두고 기억을 잘 꺼내 쓰는 구조를 정한다

## Purpose

Stage 의 장기 기억과 결정 기록을 줄이지 않고, 세션이 필요한 것을 작은 맨 위 층에서 찾아 꺼내 쓴다

## Actions


## User value


## Scope

### Included

- 설계안(선택지, 각각의 근거와 반대 관점, 추천)을 연구 자료로 쓰고, 사용자가 고를 질문을 결정 기록 DE-00000100 에 `status` 를 정하지 않은 채로 적는다. 고르는 것은 사용자다.


### Excluded


## Risks


## Success criteria

- 기억 구조의 설계안이 연구 자료에 있고, 사용자가 맡긴 선택에 따라 고른 방향이 누가 골랐는지와 함께 결정 기록에 있다

## Next action

작업 세션 session_018VXR6Qgu3ifaQ7oHco8PPm 의 설계안 보고를 받아 사용자에게 선택지를 보이고, 고른 답을 결정 기록에 적은 뒤 닫는다.

## Related truth

## Progress

- 2026-11-23 사용자가 남은 일을 묻지 말고 멈추지 말고 진행하라고 했다("이런거 묻지말고 물어보고 정지하지 말고 그냥 하라고"). 지휘 세션이 그 위임 아래 작업 세션의 추천안을 골랐고, 성공 기준의 "사용자가 골랐고"를 그 사실에 맞게 고쳤다. 사용자가 선택지를 하나씩 보고 고른 것이 아니다.

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 aa4cfbac 에서 카드를 시작하고 작업 세션 session_018VXR6Qgu3ifaQ7oHco8PPm (`claude/w400-memory-layers`)를 띄웠다. 결정 번호 하나를 잡았다.

## Verification
