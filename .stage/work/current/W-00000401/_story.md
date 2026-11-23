---
id: W-00000401
title: 닫기 리뷰가 실제로 실행해 보고 회의적으로 판정하게 하는 방법을 정한다
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
scope: .stage/research/review-judgment,.stage/decisions/pending/DE-00000101.md
promotes:
decision_refs:
reserved_ids: DE-00000101
---

# W-00000401 닫기 리뷰가 실제로 실행해 보고 회의적으로 판정하게 하는 방법을 정한다

## Purpose

리뷰어가 기록만 읽고 승인하는 일이 없어지고, 리뷰어의 판정이 사람의 판정과 맞는지 확인된다

## Actions


## User value


## Scope

### Included

- 설계안(선택지, 각각의 근거와 반대 관점, 추천)을 연구 자료로 쓰고, 사용자가 고를 질문을 결정 기록 DE-00000101 에 `status` 를 정하지 않은 채로 적는다. 고르는 것은 사용자다.
- 사용자가 2026-11-22 에 검증 세션의 판정과 닫기 리뷰를 둘 다 두고, 하나로 합칠지는 이 카드에서 정하기로 했다. 그때까지 검증 세션은 에픽에만 띄운다(W-00000404 의 Progress). 설계안은 이 선택지를 담는다.
- O-00000061 의 후보 "`close_work.py` 가 검증 세션의 판정을 받아들이게 한다"가 여기에 속한다.


### Excluded


## Risks


## Success criteria

- 사용자가 판정 강화의 설계안을 보고 하나를 골랐고 그 결정이 결정 기록에 있다

## Next action

작업 세션 session_018VXR6Q2K58yVwCfDNw6tT1 의 설계안 보고를 받아 사용자에게 선택지를 보이고, 고른 답을 결정 기록에 적은 뒤 닫는다.

## Related truth

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 aa4cfbac 에서 카드를 시작하고 작업 세션 session_018VXR6Q2K58yVwCfDNw6tT1 (`claude/w401-review-judgment`)를 띄웠다. 결정 번호 하나를 잡았다.

## Verification
