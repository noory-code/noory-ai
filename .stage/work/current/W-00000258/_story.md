---
id: W-00000258
title: 회고 번호를 카드 번호에서 만들지 말고 빈 번호를 잡는다
kind: fix
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "grep -q collision stage/scripts/tests/test_close_work.py && python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/driver_lifecycle.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000258 회고 번호를 카드 번호에서 만들지 말고 빈 번호를 잡는다

## Purpose

회고 번호를 카드 번호에서 그대로 만드는데 과거 회고들이 따로 번호를 매겨 와서 그 자리가 이미 차 있으면 카드를 못 닫으므로, 카드 등록이 하듯 빈 번호를 잡게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 회고 자리가 이미 찬 카드도 닫히고, 그 회고가 빈 번호를 받는다
- 이미 자기 번호를 쓰고 있는 카드는 그 번호를 그대로 쓴다

## Actions

없음 — 번호를 잡는 함수 하나를 고치고 그 시험을 붙이는 한 덩어리다.

## User value

카드를 닫을 때 번호 때문에 막히지 않는다. 지금은 막히면 사람이 빈 번호를 손으로 찾아 파일
이름과 본문 두 자리를 고쳐야 한다.

## Scope

### Included

**감독이 등록 전에 잰 것.**

| 잰 것 | 값 |
|---|---|
| 회고 254장 중 번호가 자기 카드와 안 맞는 것 | **168장** |
| 다음에 등록될 카드 | W-00000258 — **이 카드다** |
| 그 카드의 회고 자리 | **이미 찼다.** R-00000258 은 W-00000243 것 |

**이 카드가 자기 고장을 밟는다.** 고치지 않으면 이 카드 자신이 못 닫힌다. 시험이 아니라
실제로 그렇다.

- **번호를 잡는 자리를 고친다.** `driver_lifecycle.py:236` `retrospective_id_for_work_item` 이
  카드 번호에서 `R-` + 숫자로 만든다. 카드 등록(`register_work.py:180-198`)이 하듯 **빈 번호를
  찾아 원자적으로 잡는** 모양으로 바꾼다.
- **이미 자기 번호를 쓰는 카드는 그대로 둔다.** 168장이 안 맞지만 나머지는 맞고, 맞는 것을
  옮기면 링크가 깨진다.
- 손으로 닫는 쪽(`close_work.py`)도 같은 자리에서 막힌다. 두 쪽이 같은 함수를 쓰게 한다.

### Excluded

- **이미 있는 회고 168장을 안 옮긴다.** 번호가 안 맞는 것이 문제가 아니라, 새로 잡을 때 찬
  자리를 피하는 것이 문제다. 옮기면 `retrospective_ref` 와 감사 링크가 전부 따라 움직인다.
- 카드 번호를 안 바꾼다.
- 회고 본문의 틀을 안 바꾼다.

## Risks

- **원자적으로 안 잡으면 병렬 실행이 같은 번호를 집는다.** 오늘 병렬로 둘을 돌렸고, 그때
  드라이버가 회고를 각자 만들었다. `register_work.py` 가 쓰는 모양(파일을 `x` 모드로 열어
  실패하면 다음 번호)을 그대로 따른다.
- **맞는 짝을 옮기면 링크가 깨진다.** 지금 자기 번호를 쓰는 회고는 그대로 둬야 한다.
- 이 카드가 못 닫히면 드라이버가 그 자리에서 멈춘다. 그것이 이 카드가 고치는 고장이므로
  옳은 실패다.

## Next action

**`stage/scripts/driver_lifecycle.py:236` `retrospective_id_for_work_item` 을 먼저 읽는다.**
지금 카드 번호에서 회고 번호를 만든다. 그 1:1 짝이 과거 기록에서 이미 깨져 있다 — 168장이
안 맞는다.

따라갈 모양은 `stage/skills/stage-work/register_work.py:180-198`
`create_hierarchy_item_atomic` 이다. 최대값+1 로 시작해 파일을 `x` 모드로 열고, 이미 있으면
다음 번호로 넘어간다.

**저장된 인수 명령이 `grep -q collision` 으로 시험 파일을 먼저 본다** — 지금 그 낱말이 0번
나오므로, 시험을 안 쓰면 이 검사가 막는다.

## Related truth

- `stage/skills/stage-work/register_work.py:180-198` — 카드 번호를 원자적으로 잡는 자리.
  따라갈 모양이다.
- R-00000258 — 이 고장을 감독이 손으로 겪은 판. 회고를 R-00000243 으로 썼다가 감사가 잡아
  R-00000258 로 옮겼다.
- M-00000004 완료 기준 넷째("사람이 한 일이 판단뿐")에 걸린다. 번호를 손으로 찾아 고치는 것은
  판단이 아니라 장부질이다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
