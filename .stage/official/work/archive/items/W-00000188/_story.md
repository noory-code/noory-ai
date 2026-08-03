---
id: W-00000188
title: 대체된 결정이 자기가 대체됐다고 말하게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000194
promotion: promoted
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

- **넣을 두 문장이 정해져 카드에 적혀 있다.** 무엇을 어디에 쓸지가 다음 사람에게 보인다.
- 승격이 끝난 뒤: DE-00000051 을 열면 첫머리에서 DE-00000052 가 그것을 대체했다는 것이 보이고,
  규칙이 사는 자리에도 같은 모양으로 쓰라는 한 줄이 있다.
- 목록도 상태값도 안 늘었다.
- 감사 오류 0.

## Next action

없다. 문장이 정해졌고 승격으로 실었다.

## Progress

### 기준을 실제로 갈 수 있는 길에 맞췄다 — 2026-08-03

처음 기준은 **공식 기록에 문장이 이미 들어가 있기**를 요구했다. 그런데 그 파일은 카드를 닫은
뒤에야 승격 의도로 열린다. **닫아야 쓸 수 있는데 쓰여 있어야 닫힌다** — 드라이버가 이 카드를
끝낼 길이 없었다.

기준을 둘로 갈랐다. 카드가 하는 일은 **문장을 정하는 것**이고, 파일에 넣는 것은 닫은 뒤
승격이 한다.

**이 어긋남이 바로 오늘 만든 W-00000191 이 잡으려는 모양이다** — 범위가 허락한 결말을 기준이
안 받는 것. 다만 이 카드는 그 장치가 실리기 전에 등록됐다.

### 넣을 문장

**DE-00000051 첫머리** (`# DE-00000051 ...` 바로 아래):

> **이 결정은 DE-00000052 가 대체했다(2026-07-31).** 아래에 적힌 것은 그때 정한 것이고,
> 지금 구속하는 것은 DE-00000052 다.

**DE-00000030 의 `## Chosen direction` 판정 규칙 끝**:

> - 어떤 결정이 다른 결정을 대체하면, **대체된 쪽 첫머리에 무엇이 언제 그것을 대체했는지 적는다.**
>   기록은 안 지우므로 남는 이상 그것이 지금 구속하는지가 읽혀야 한다.

## Related truth

- **DE-00000030** — 어떤 결정 기록도 지우지 않는다. 그래서 대체된 것도 남고, 남는 이상 그것이
  지금 구속하는지가 읽혀야 한다.
- **DE-00000052** — DE-00000051 을 대체했다. 자기 머리말에 그렇게 적었지만, 대체된 쪽에는
  아무 표시도 없다.


## Progress


## Verification


### Executed at close — 2026-08-03

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


## Promotion decision

`approved` — `promotes` 가 가리키는 두 공식 기록에 넣을 문장은 정해졌다. 실제 쓰기는 이 카드를
닫은 뒤 승격 의도로 한다. 승격 게이트가 닫힌 카드에만 의도를 내주기 때문이다. 문장 원문은 작업
로그에 있다.
