---
id: W-00000324
title: codex 가 없는 동안 권한·닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다
kind: planning
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/
promotes:
decision_refs: DE-00000087
---

# W-00000324 codex 가 없는 동안 권한·닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다

## Purpose

같은 모델의 리뷰가 실제로 놓쳤던 종류의 카드가, 다른 모델 계열이 없는 기간에도 사람의 눈을 거쳐서만 닫히게 한다

## Actions
DE-00000087 을 쓰고 `.stage/operations/claude-venue.md` 에 대상 경로와 닫는 순서를 적는다. 이 카드 자신이 `.stage/operations/` 를 바꾸므로 대상이다 — 리뷰 판정 뒤 사용자 확인을 받고 닫는다.


## User value
다른 모델의 검토가 없는 기간에도, 관문을 약하게 만들 수 있는 변경은 사용자가 직접 본 뒤에만 닫힌다.


## Scope

### Included
- 결정 레코드 DE-00000087
- `.stage/operations/claude-venue.md` 의 절차 절


### Excluded
- 감사 규칙이나 닫기 도구로 강제하는 구현
- 이미 닫힌 카드의 소급 확인(W-00000323 은 `.stage/settings.json` 을 바꿨고 이 규칙 이전에 닫혔다)


## Risks
도구가 강제하지 않으므로 감독이 대상임을 놓치면 확인 없이 닫힌다. 표본 5장에서 나온 규칙이라 경로 목록이 좁을 수 있다.


## Success criteria

- DE-00000087 이 decided 이고, 어떤 경로를 바꾼 카드가 대상인지 경로 목록으로 적는다
- .stage/operations/claude-venue.md 가 대상 경로, 사용자에게 보여 줄 것, 확인을 카드에 적는 자리, 닫기 명령을 돌리는 시점을 적는다
- 이 카드 자신이 대상이므로, 사용자가 변경 요약과 리뷰 판정을 보고 확인한 날짜가 이 카드의 Verification 에 적힌 뒤에 닫힌다
- python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다

## Next action
닫기 리뷰 판정을 받은 뒤 사용자에게 변경 요약과 판정을 보여 주고 확인을 기다린다.


## Related truth
DE-00000086 이 codex 없는 기간의 실행 환경을, W-00000299 가 표본 재검토 결과와 권고를 소유한다.


## Progress
2026-11-14: 사용자 지시로 카드를 등록하고 DE-00000087 과 운영 문서 절을 썼다.


## Verification


## Retrospective


## Promotion decision
