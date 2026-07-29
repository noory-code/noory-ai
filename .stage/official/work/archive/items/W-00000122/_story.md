---
id: W-00000122
title: 겹치지 않는 Stage 작업을 병렬로 돌릴 수 있게 한다 — 설계
kind: design
venue: claude
milestone:
source:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000115
promotion: approved
review: not_required
scope: .stage/decisions/, .stage/work/planned/, .stage/proposals/
promotes: .stage/official/decisions/records/DE-00000040.md, .stage/official/decisions/index.md
decision_refs: DE-00000040
---

# W-00000122 겹치지 않는 Stage 작업을 병렬로 돌릴 수 있게 한다 — 설계

## Purpose

드라이버 한 번에 카드 하나만 도는 것이 지금의 한계다. 겹치지 않는 카드는 동시에 돌 수 있어야 한다. 무엇이 실제로 막는지 세고, 갈림을 결정 기록으로 남기고, 구현 카드를 뽑는다. 사용자 요청 2026-07-29.

## Actions

- 무엇이 실제로 병렬을 막는지 실측으로 센다 — 추측 금지.
- 갈림을 결정 기록으로 남기고, 사람 확인이 필요한 자리를 밝힌다.
- 구현 카드를 규모로 쪼개 등록한다.

## Scope

`.stage/` 만 바꾼다. 구현은 에픽 W-00000123 몫.

## Success criteria

- 막는 자리가 실패 경로부터 세어져 있고, 각각 추측이 아니라 확인된 근거를 갖는다.
- 갈림과 선택이 결정 기록에 있고, 안 바꾸는 자리도 이유와 함께 적혀 있다.
- 사람 확인이 필요한 자리(커밋된 지시문 수정)가 밝혀지고 확인을 받았다.
- 구현 카드가 순서와 함께 등록돼 있다.
- `python3 stage/scripts/audit_stage.py` 가 errors=0, warnings=0.

## Related truth

- [DE-00000040](../../decisions/pending/DE-00000040.md) — 이 설계의 소유자
- [P-00000001](../../proposals/P-00000001.md) — 캐시 잠금의 실측 기록

## Progress

- 막는 자리 넷을 셌다: 작업 트리 공유, 버전 올리기 충돌, 코덱스 캐시 잠금, 공유 인덱스 병합.
- 시도 기록은 `.gitignore` 라 트리마다 이미 따로 논다는 것을 확인해 "바꿀 것 없음"으로 닫았다.
- DE-00000040 작성 → 사람 확인(2026-07-29, 버전 규칙을 릴리스 시점으로) → decided.
- 에픽 W-00000123 + 스토리 셋(W-00000124~126) 등록. 순서 고정 — 버전이 먼저다.

## Verification


### Executed at close — 2026-07-29

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000115](../../retrospectives/R-00000115.md)

## Promotion decision

approved — DE-00000040 을 status promoted 로 `official/decisions/records/` 에 올리고 official
인덱스에 행 하나를 더한다. 버전을 언제 올리는지와 병렬의 단위를 정하므로 미래 작업을 구속한다.
