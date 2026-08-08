---
id: W-00000244
title: 열린 관측을 읽는 쪽을 만든다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q -k context"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/operations/, stage/hooks/, stage/hooks/tests/, stage/scripts/, stage/skills/stage-work/, stage/CHANGELOG.md, .stage/decisions/, .stage/state/
promotes:
decision_refs:
---

# W-00000244 열린 관측을 읽는 쪽을 만든다

## Purpose

관측 열여섯이 열린 채로 최대 열이틀째 앉아 있고 세션에 들어오는 목록이 최신 여섯을 잘라
버려서 가장 새 문제가 아무한테도 안 보이므로, 열린 관측이 사람 눈에 다 들어오고 일감이
되거나 닫히도록 꺼내 보는 자리를 만든다

## Actions

없음 — 한 덩어리다.

## User value

문제를 적어 두면 언젠가 처리된다. 지금은 적어 두면 그 자리에서 늙는다.

## Scope

### Included

**감독이 이미 잰 것.** 등록 전에 세션 시작 훅을 직접 돌려 확인했다.

| 잰 것 | 값 |
|---|---|
| 세션에 들어오는 전체 길이 | 6,545자 |
| `state/current.md` 를 자르는 한도 | 1,400자 (`stage_context.py:38` 의 `read_if_exists` 기본값) |
| 지금 열린 관측 | 16개 |
| 그중 세션에 실제로 들어온 것 | O-00000036 까지 — **뒤의 여섯이 잘렸다** |
| 가장 오래 열린 것 | O-00000002, 2026-07-27 (열이틀) |

- **잘리는 쪽을 고친다.** 최신이 잘리고 가장 오래된 것이 남는다. 새로 적은 문제가 그다음
  세션에 안 보이면 적는 행위 자체가 값을 잃는다.
- **얼마나 오래 열려 있는지를 목록이 말하게 한다.** 지금은 제목만 있어서 어제 것과 열이틀
  된 것이 같아 보인다.
- **지금 열린 열여섯을 한 장씩 읽어 처분한다.** 일감으로 세우거나, 이미 해소됐으면 닫거나,
  아직 열려 있어야 하면 왜인지 그 관측에 적는다. 세 갈래 밖은 없다.
- **관측이 늘 때 이 자리가 다시 막히는지 본다.** 한도를 올리는 것으로 끝나면 서른 개가
  됐을 때 같은 자리를 다시 밟는다.

### Excluded

- 회고나 결정을 꺼내 보는 자리는 안 만든다. 회고는 W-00000245 가 어제 다뤘고, 그 절차가
  실제로 도는지 보고 나서 같은 모양을 관측에 쓸지 정한다.
- 관측을 자동으로 닫지 않는다. 닫을지는 사람이 판단한다.
- 세션 시작이 `.stage/operations/` 규칙을 안 실어 주는 것(O-00000042)은 이 카드 밖이다.
  같은 훅을 만지지만 다른 문제다 — 그쪽은 규칙이 아예 안 오고, 이쪽은 오다가 잘린다.

## Risks

- **한도를 올리면 세션 시작이 무거워진다.** 지금 6,545자인데 관측 본문을 다 실으면 몇 배가
  된다. 목록만 늘리고 본문은 안 싣는 선을 지킨다.
- **잘리는 자리가 여기만이 아니다.** `read_if_exists` 는 진행 중 작업과 리뷰 후보에도 같은
  한도를 쓴다. 하나만 고치면 나머지가 조용히 같은 문제를 갖는다 — 세 자리를 다 세고 고친다.
- 열여섯을 한 번에 처분하면 판단이 거칠어진다. 한 장씩 근거를 적고, 애매하면 열어 둔다.

## Success criteria

- 열린 관측이 세션에 하나도 안 잘리고 들어오고, 각각 며칠째 열려 있는지가 그 줄에 있다
- 관측이 지금의 두 배가 돼도 안 잘린다는 것이 시험으로 잡힌다
- 지금 열린 열여섯이 각각 일감이 되거나 닫히거나, 열어 두는 이유가 그 관측에 적혀 있다

## Next action

`stage/hooks/stage_context.py:38` 의 `read_if_exists` 가 한도 1,400자로 세 자리를 자른다
(`Current state`, `Active work`, `Review candidates`). 자르는 방식을 고치기 전에 세 자리가
각각 무엇을 잃는지 실제로 돌려서 잰다 — 감독은 관측 자리만 쟀다.

## Related truth

- O-00000042 — 같은 훅의 다른 구멍. 규칙 본문이 아예 안 실린다. 이 카드가 훅을 만질 때 함께
  볼 수 있지만 고치는 것은 별건이다.
- R-00000241 — 회고의 배움이 규칙이 되는 절차. 같은 모양의 문제("써 놓고 읽는 쪽이 없다")를
  회고 쪽에서 먼저 풀었다. 그 절차가 참고가 된다.

## Progress

## Verification

## Retrospective

## Promotion decision
