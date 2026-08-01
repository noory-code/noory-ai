---
id: W-00000175
title: 밀린 결정을 공식으로 내리고 다시 안 쌓이게 한다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-retrospective/, stage/scripts/tests/, stage/operations/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000175 밀린 결정을 공식으로 내리고 다시 안 쌓이게 한다

## Purpose

DE-00000030 이 정한 승격 규칙을 사람이 손으로만 지켜서 앞으로를 구속하는 결정 여섯이 대기에 갇혔다.

## Actions

- W-00000176 — 밀린 결정 여섯을 공식으로 내린다 (기록 정리 · codex)
- W-00000177 — 카드를 닫을 때 승격 여부를 그 자리에서 판정하게 한다 (구현 · codex)

## User value

프로젝트를 지금 구속하는 결정을 `official/decisions/` 한 자리에서 다 읽는다. 일회성 허가는
거기 안 섞인다. 카드를 보관해도 그 카드가 정한 규칙이 대기 서랍에 갇히지 않는다.

## Scope

### Included

- 대기에 갇힌 결정 여섯을 공식으로 옮기고 인덱스에 싣는다.
- 카드를 닫을 때 그 카드가 소유한 결정의 승격 여부를 판정하게 만든다.
- 그 계약을 지키는지 보는 시험.

### Excluded

- **일회성 venue 허가 여섯**(DE-6·8·25·26·41·45). DE-00000030 이 대기에 남기라고 정했다.
  건드리지 않는다.
- 승격 규칙 자체를 다시 정하는 일. DE-00000030 이 이미 소유한다.
- 보관된 카드가 승격할 수 있게 게이트를 여는 일. 지금 막힌 것을 푸는 데 그 변경이 필요 없다 —
  승격 게이트는 카드의 `promotes` 목록만 보므로 열려 있는 카드 하나로 내릴 수 있다.

## Risks

- **로드맵 착수 결정(DE-00000049)이 갈래가 다르다.** 일회성 허가가 아니니 규칙상 승격 대상인데,
  마일스톤 상태가 이 결정 사슬에서 계산되고 승격 때 사슬을 다시 검사하는 자리가 있다. 나머지
  다섯과 같이 옮기기 전에 그 검사를 통과하는지 먼저 봐야 한다.
- **닫을 때 판정을 강제하면 결정 없는 카드까지 걸릴 수 있다.** 결정을 안 가진 카드는 지금처럼
  지나가야 한다.

## Success criteria

- `decisions/pending/` 에 `authorizes: venue_exception` 없이 `decided` 로 남은 결정이 없다.
- 결정을 소유한 카드가 승격 여부를 안 정하고는 닫히지 않는다.
- 그 계약을 지키는지 보는 시험이 있고, 결정 없는 카드는 그대로 지나간다.
- 사람이 겪는 결과: 지금 나를 구속하는 규칙이 무엇인지 공식 서랍만 열면 다 보인다.

## Next action

W-00000176 부터. 먼저 DE-00000049 가 나머지 다섯과 같은 갈래인지 판정한다.

## Related truth

- **DE-00000030** — 결정이 언제 공식이 되는가. 일회성 허가는 대기에 남고 나머지 `decided` 는
  승격한다. 그 결정이 남긴 후속("닫을 때 그 자리에서 판정한다")이 이 스토리의 뼈대다.


## Progress


## Verification


## Retrospective


## Promotion decision
