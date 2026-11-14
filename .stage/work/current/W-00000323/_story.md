---
id: W-00000323
title: codex 구독이 없는 동안 로컬 카드도 Claude가 실행하도록 환경을 선언한다
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
decision_refs: DE-00000086
---

# W-00000323 codex 구독이 없는 동안 로컬 카드도 Claude가 실행하도록 환경을 선언한다

## Purpose

codex 구독이 없는 동안에도 로컬 세션에서 codex 로 라우팅되는 카드를 예외 결정 없이 시작하고 닫을 수 있게 하되, 같은 모델이 리뷰했다는 사실이 카드마다 남게 한다

## Actions
결정 레코드 DE-00000086 을 쓰고 사용자가 확정한다. 확정 뒤 `environment_venues` 에 환경 한 줄을 더하고, `.stage/operations/claude-venue.md` 에 codex 없는 로컬 세션의 시작·닫기 명령을 적는다.


## User value
codex 구독이 없는 동안에도 로컬에서 개발·수정 카드가 막히지 않고, 나중에 어떤 카드가 같은 모델의 리뷰로 닫혔는지 카드만 보고 가려낼 수 있다.


## Scope

### Included
- 결정 레코드 DE-00000086
- `.stage/settings.json` 의 `environment_venues` 한 줄
- `.stage/operations/claude-venue.md` 의 codex 없는 로컬 세션 절차


### Excluded
- `venue_routing`, `executors`, `review` 설정 변경
- Stage 플러그인 코드와 플러그인 소유 문서 변경
- 열려 있는 codex venue 카드(W-00000271, W-00000281, W-00000282)의 재시작 — 카드마다 따로 정한다


## Risks
실행과 리뷰가 같은 모델 계열이라 둘이 함께 놓치는 결함은 닫기 리뷰가 잡지 못한다. DE-00000082 가 기대던 나중의 로컬 codex 확인도 이 기간에는 없다.


## Success criteria

- DE-00000086 이 decided 이고, 선택한 방향·적용 자리·이 결정이 틀렸음을 알리는 관측을 담는다
- .stage/settings.json 의 environment_venues 에 로컬 환경이 선언되고 venue_routing 과 review 명령은 바뀌지 않는다
- stage_work.environment_venue_error 가 새 환경에서 venue claude·review pending 카드를 허용하고, review 를 요구하지 않는 카드와 venue codex 카드를 거절한다
- .stage/operations/claude-venue.md 가 codex 없는 로컬 세션에서 카드를 시작하고 닫는 명령을 적는다
- python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다

## Next action
사용자가 DE-00000086 초안(환경 이름 `local-no-codex` 포함)을 확인한다. 확정하면 설정과 운영 문서를 고친다.


## Related truth
DE-00000082 와 `stage/operations/cloud-execution.md` 가 환경 정책과 Claude 대역 닫기 리뷰 절차를 소유한다. DE-00000062 와 `.stage/operations/claude-venue.md` 가 claude venue 실행 방식을 소유한다.


## Progress
2026-11-14: 카드를 등록하고 DE-00000086 초안을 `open` 으로 썼다. 설정과 운영 문서는 사용자 확정 전이라 고치지 않았다.


## Verification


## Retrospective


## Promotion decision
