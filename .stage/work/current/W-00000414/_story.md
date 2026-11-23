---
id: W-00000414
title: 지금의 닫기 리뷰어를 결함이 기록된 과거 변경으로 잰다
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
scope: .stage/research/review-judgment
promotes:
decision_refs:
---

# W-00000414 지금의 닫기 리뷰어를 결함이 기록된 과거 변경으로 잰다

## Purpose

닫기 리뷰어의 판정이 사람이 남긴 과거의 판정과 얼마나 맞는지가 수로 있어서, 리뷰어를 더 조일지 말지를 그 수로 정한다 (DE-00000101 의 3-가)

## Actions


## User value


## Scope

### Included

- 재는 방법과 표본을 먼저 적는다. 쓸 수 있는 과거 변경이 몇 건인지부터 센다(닫기 리뷰가 반려한 기록, 닫은 뒤 고친 기록, 회고가 결함을 적은 카드).
- 리뷰어는 저장소의 리뷰 명령(`claude_review_companion.py`)으로 돌린다.


### Excluded

- 리뷰 코드나 설정을 고치는 일. 바닥을 넣는 것은 추천까지만 한다.
- 사용자가 카드 다섯 장을 직접 판정하는 일(3-나).


## Risks


## Success criteria

- 결함이 기록된 과거 변경의 목록과, 지금의 리뷰어를 그 변경과 통과한 최종판에 돌려 센 거짓 통과와 거짓 반려의 수가 연구 자료에 있다
- 그 결과에 비추어, 실행이 필요한 기준에 ran 이 하나는 있어야 한다는 바닥을 넣을지에 대한 추천이 근거와 함께 있다

## Next action

작업 세션 session_018VXR6QZEBarY6p6PTVEZdb 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.


## Related truth

- DE-00000101, `.stage/research/review-judgment/design.md`, W-00000408, W-00000410(실행해서 판정하는 리뷰어의 첫 반려)
- 리뷰어를 여러 번 띄우므로 비용이 든다. 표본이 작으면 작다고 적고 수를 과하게 읽지 않는다.
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions

- session_018VXR6QZEBarY6p6PTVEZdb — work — 2026-11-23 — opened from the index: not reported yet


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 d192365b 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QZEBarY6p6PTVEZdb (`claude/w414-measure-reviewer`)를 띄웠다. 번호 묶음은 잡지 않았다.


## Verification
