---
id: W-00000188
title: 대체된 결정이 자기가 대체됐다고 말하게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: approved
review: not_required
scope: .stage/
promotes: .stage/official/decisions/records/DE-00000051.md, .stage/official/decisions/records/DE-00000030.md
decision_refs:
---

# W-00000188 대체된 결정이 자기가 대체됐다고 말하게 한다

## Purpose

DE-00000051 을 열면 그것이 아직 구속하는 규칙처럼 읽힌다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

공식 서랍에서 결정 하나를 열면 그것이 지금도 구속하는지 그 자리에서 알 수 있다.

## Scope

### Included

- DE-00000051 첫머리에 무엇이 그것을 대체했는지 적는다.
- 대체된 결정을 그렇게 표시한다는 것을 결정 소유 규칙(DE-00000030)이 사는 자리에 한 줄 붙인다.

### Excluded

- **목록에 칸을 더하거나 새 상태값을 만드는 일.** 56건 중 대체가 1건이다. 반복이 보이기 전에
  장치를 만들지 않는다.
- 대체된 결정을 지우거나 옮기는 일. 어떤 결정 기록도 안 지운다(DE-00000030).
- 본문의 나머지. 그때 정한 것은 그때의 사실이라 그대로 둔다.

## Risks

- **한 줄이 본문과 어긋날 수 있다.** DE-00000051 은 자기 선택을 옳다고 적는다. 첫머리 한 줄이
  그것을 뒤집는 것이 아니라 "그 뒤에 이렇게 됐다"를 말하도록 쓴다.

## Success criteria

- DE-00000051 을 열면 첫머리에서 DE-00000052 가 그것을 대체했다는 것이 보인다.
- 규칙이 적힌 자리에도 그 한 줄이 있어, 다음 대체가 나오면 같은 모양으로 쓴다.
- 목록도 상태값도 안 늘었다.
- 감사 오류 0.

## Next action

DE-00000051 첫머리에 한 줄을 넣는다. 그것이 공식 기록이라 승격 의도가 필요하다 — 이 카드가
`promotes` 로 선언한다.

## Related truth

- **DE-00000030** — 어떤 결정 기록도 지우지 않는다. 그래서 대체된 것도 남고, 남는 이상 그것이
  지금 구속하는지가 읽혀야 한다.
- **DE-00000052** — DE-00000051 을 대체했다. 자기 머리말에 그렇게 적었지만, 대체된 쪽에는
  아무 표시도 없다.


## Progress


## Verification


## Retrospective


## Promotion decision

`approved` — `promotes` 가 가리키는 두 공식 기록에 넣을 문장은 정해졌다. 실제 쓰기는 이 카드를
닫은 뒤 승격 의도로 한다. 승격 게이트가 닫힌 카드에만 의도를 내주기 때문이다. 문장 원문은 작업
로그에 있다.
