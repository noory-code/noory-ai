---
id: W-00000363
title: 카드 한 장에 드는 문서와 절차에서 덜어낼 것을 정한다
kind: design
venue: claude
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000363
promotion: deferred
review: not_required
scope: .stage/decisions
promotes:
decision_refs: DE-00000089
---

# W-00000363 카드 한 장에 드는 문서와 절차에서 덜어낼 것을 정한다

## Purpose

다시 읽지 않는 문서를 쓰느라 일이 느려지지 않도록 카드 한 장에 드는 문서와 절차에서 무엇을 덜어낼지 정한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 카드와 회고의 각 절이 양식이 채운 것인지 사람이나 AI 가 쓴 것인지, 닫은 뒤 다시 읽힌 적이 있는지 센 결과가 있다
- 유지 카드를 등록할 때 묻는 것을 무엇이 무너졌나와 다시 서면 끝으로 줄일지 사용자가 정했다
- 사용자가 덜어낼 것을 골랐고 그 결정이 결정 기록에 있다
- 고른 것을 구현하는 카드가 계획된 카드로 등록되어 있다

## Next action

## Related truth

## Progress

- 닫힌 카드 365장의 줄을 칸별로 셌다. 닫을 때 붙는 명령 출력과 리뷰 전문이 43%, 맨 위 설정 칸이 19%,
  사람과 AI 가 쓰는 본문이 38% 다. 닫은 뒤 다른 기록이 인용한 회고는 W-300 이후 63개 가운데 7개다.
  인용만 셌고 실제로 읽혔는지는 셀 수 없다.
- 2026-11-06 이후 커밋 162개 가운데 121개가 `.stage/` 기록만 고쳤다.
- 사용자가 2026-11-20 에 후보 다섯 가운데 넷을 골랐다("네, 그 네 가지"). 유지 카드의 질문을 줄이는 것이
  그 가운데 3번이다. 센 값과 고른 것은 DE-00000089 에 있다.
- 구현 카드 W-00000368, W-00000369, W-00000370 을 계획된 카드로 등록했다.

## Verification

- `python3 stage/scripts/audit_stage.py`: 오류 0건.
- 세는 데 쓴 스크립트는 세션의 임시 폴더에 있고 저장소에 넣지 않았다.

### Executed at close — 2026-11-21

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective

## Promotion decision
