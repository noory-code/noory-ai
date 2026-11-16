---
id: W-00000337
title: DE-00000082 를 공식 결정 기록으로 올린다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/decisions/, .stage/official/decisions/
promotes: .stage/official/decisions/records/DE-00000082.md, .stage/official/decisions/index.md
decision_refs:
---

# W-00000337 DE-00000082 를 공식 결정 기록으로 올린다

## Purpose

이미 코드로 쓰이고 있는 실행 환경 칸 결정(DE-00000082)을 대기 폴더에서 공식 결정 기록으로 옮겨, 다음 세션이 그것을 정착된 규칙으로 읽게 한다

## Actions

없음 — 결정 기록 한 장을 옮기고 두 인덱스를 맞추는 일이라 나누지 않는다.

## User value

세션이 시작할 때 DE-00000082 를 아직 정해지지 않은 결정으로 읽지 않는다. 대기 중인 결정 목록에서
빠져서, 사람이 정해야 할 것이 하나 줄어든 것이 목록에 그대로 보인다.

## Scope

### Included

- DE-00000082 를 `decisions/pending/` 에서 `official/decisions/records/` 로 옮기고 상태를
  `promoted` 로 바꾼다.
- 대기 결정 인덱스에서 그 줄을 빼고 공식 결정 인덱스에 한 줄을 더한다.
- 사용자가 2026-11-16 에 "82 지금, 73은 나중에"를 골랐다.

### Excluded

- 결정 본문은 고치지 않는다. 같은 날 Follow-up 에 적은 메모(DE-00000087 이 W-00000299 권고에
  답했다)는 그대로 함께 옮긴다.
- DE-00000073 은 플레인리 에픽을 닫을 때 올린다. DE-00000085·86·87 은 그대로 둔다.
- `decision_refs` 는 비워 둔다. 이 카드는 결정을 정한 카드가 아니라 옮기는 카드다. 결정을 정한
  카드는 W-00000292 이고 보관돼 있다.

## Risks

- 결정을 정한 카드와 올리는 카드가 다르다. 감사가 이 조합을 받아들이는지는 해 봐야 안다.

## Success criteria

- DE-00000082 가 official/decisions/records 에 status: promoted 로 있고 대기 폴더에서는 빠진다
- 두 결정 인덱스가 그 이동을 함께 반영한다
- 감사가 오류 없이 통과한다

## Next action

회고를 쓰고 `promotion: deferred` 로 닫은 뒤, intent 를 만들어 결정 기록을 옮긴다.

## Related truth

- DE-00000082 — 올릴 결정. 결정을 정한 카드는 W-00000292(보관됨).
- W-00000273 — 같은 방식으로 DE-00000074 를 올린 카드(보관됨).

## Progress


## Verification


## Retrospective


## Promotion decision
