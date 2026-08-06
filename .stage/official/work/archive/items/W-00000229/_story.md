---
id: W-00000229
title: 목적이 빈 카드에서는 그 위의 목적이라도 보여 준다
kind: fix
venue: codex
milestone:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: archived
terminal_disposition: rejected
verification: pending
retrospective: completed
retrospective_ref: R-00000227
promotion: not_applicable
review: not_required
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000229 목적이 빈 카드에서는 그 위의 목적이라도 보여 준다

## Purpose

목적이 비어 있는 옛 카드를 만질 때 쓰기마다 붙는 목적 안내가 보여 줄 것이 없어 조용히 지나가므로, 그 카드가 걸린 마일스톤과 테마의 문장이라도 대신 보여 준다

## Actions

없음 — 안내를 만드는 자리에 갈래 하나를 더하고 시험을 붙이는 한 덩어리다.

## User value

목적이 빈 옛 카드 32장을 만질 때 "이거 왜 하는 일이었지"가 조용히 지나가지 않는다. 지금은
카드 목적이 비면 아무것도 안 나오고, 그 카드가 마일스톤에 걸려 있어도 마찬가지다.

## Scope

### Included

- 쓰기마다 붙는 목적 안내(`stage_guard.py` 의 `purpose_tool_context`)가, 카드의 목적이 비어
  있으면 그 카드가 걸린 마일스톤과 그 마일스톤의 테마 문장을 대신 싣게 한다.
- 지금 코드는 마일스톤 문장을 카드 목적보다 **앞에** 싣는데, 그 자리를 찾는 조건이 카드
  frontmatter 의 `milestone` 이다. 목적이 비었는지와 무관하게 이미 그렇게 동작하므로, 이
  카드가 더하는 것은 **"카드 목적이 비어도 안내를 만든다"** 한 갈래다.
- 회귀 시험 둘을 `test_stage_guard.py` 에 더한다 — 목적이 빈 카드가 마일스톤에 걸린 경우,
  목적이 있는 카드가 지금과 같은 출력을 내는 경우.

### Excluded

- 카드도 마일스톤도 없어 보여 줄 문장이 하나도 없는 경우에 뭔가를 지어내지 않는다. 그때는
  지금처럼 범위 줄만 나온다.
- 옛 카드 32장의 목적을 채우지 않는다. 보관된 카드는 안 고치는 것이 이 프로젝트 규칙이다.

## Risks

- 이 안내는 모든 도구 호출에 붙는다. 갈래를 잘못 넓히면 출력이 시끄러워진다. 목적이 있는
  카드의 출력은 한 글자도 안 바뀌어야 한다 — 시험이 그것을 고정한다.


## Success criteria

- 목적이 빈 카드에 쓰기를 하면 그 카드가 걸린 마일스톤과 테마의 문장이 나온다
- 목적이 있는 카드의 안내는 지금과 똑같이 나온다

## Next action


## Related truth


## Progress

무인 실행 한 바퀴(가지 `stage/driver/W-00000229-1786011361`). 실행자가 소스를 안 고치고
카드를 거절했다 — 마일스톤과 테마 문장은 카드 목적이 비어 있어도 이미 나온다. 감독이 코드로
다시 확인했다: 안내를 만드는 자리는 카드 목적이 비었는지와 무관하게 먼저 마일스톤·테마 줄을
싣고, 카드 목적 줄만 목적이 있을 때 붙는다. 안 나오는 경우는 카드에 마일스톤 자체가 없을
때뿐이고, 그때는 보여 줄 문장이 없다 — 이 카드의 Excluded 가 이미 "지어내지 않는다"고 적었다.

**그 바퀴가 하니스 결함 하나를 드러냈다.** 실행자가 계약대로 카드의 `promotion` 만 쓰자
드라이버가 담을 것이 없어 커밋에 실패하고 카드를 막았다. O-00000034 로 남겼다.

## Verification

실행자 판단을 감독이 코드로 검증했다. 성공 기준 둘은 이미 참이므로 만들 것이 없다.

## Retrospective

R-00000227 참조.

## Promotion decision

not_applicable — 결정 기록 없음, 승격 경로 없음. 카드 자체는 물림: 등록 시점에 이미 되고
있던 동작을 다시 만들라고 적었다.
