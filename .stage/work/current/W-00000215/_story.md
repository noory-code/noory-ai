---
id: W-00000215
title: 목적 표시가 빈 카드에서 한 번을 안 쓰게 한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000215 목적 표시가 빈 카드에서 한 번을 안 쓰게 한다

## Purpose

쓰기 직전에 목적을 띄우는 장치가 막 만든 카드에서는 빈 본문을 보여 주며 세션의 한 번을 써 버리므로, 목적이 빈 카드를 만나면 그 한 번을 아꼈다가 목적이 채워진 뒤에 뜨게 한다

## Actions

없음 — 훅의 소모 판정 한 자리를 고치고 시험을 더하는 한 덩어리다.

## User value

카드를 만들고 바로 본문을 쓰는 가장 흔한 흐름에서, "이거 왜 하는 일이었지"를 보여 주는 장치가
지금은 제목 한 줄만 보여 주고 세션의 한 번을 써 버린다. 고치면 그 한 번이 목적이 실제로
채워진 뒤 — 진짜 필요할 때 — 쓰인다.

## Scope

### Included

- `stage_guard.py` 의 쓰기 직전 목적 표시(`append_purpose_context`, 573행 근처)가 카드의
  `## Purpose` 가 비어 있으면 **세션 한 번을 소모하지 않고** 지나가게 한다. 목적이 채워진
  뒤의 첫 쓰기가 그 한 번을 쓴다.
- 빈 목적 카드 → 본문 채움 → 다음 쓰기에서 목적이 뜨는 흐름의 시험을
  `test_stage_guard.py` 에 더한다.

### Excluded

- 카드 목적이 비면 마일스톤·테마를 대신 보여 주는 길(O-00000018 의 둘째 후보)은 안 간다 —
  등록이 이제 빈 목적을 거부하므로(0.58.0), 빈 본문은 대개 "막 만든 직후" 한순간뿐이다.
  그 순간을 아끼는 쪽이 싸고 충분하다.

## Risks

- 등록 게이트(0.58.0)가 빈 목적 카드를 거의 없앴으므로 이 구멍의 빈도는 낮아졌다. 다만 옛
  카드 32장은 여전히 목적이 비어 있고, 그 카드를 만지는 첫 쓰기가 지금도 한 번을 헛써 버린다.
- "비었다" 판정이 공백·플레이스홀더 문장을 어떻게 볼지 정해야 한다. 좁게(정말 빈 것만) 시작한다.

## Success criteria

- 목적이 빈 카드에 첫 쓰기를 해도 장치의 세션 한 번이 소모되지 않는다
- 목적이 채워진 뒤의 첫 쓰기에서 목적이 뜬다

## Next action

`append_purpose_context` 가 세션 한 번을 소모하는 자리와 카드 본문을 읽는 자리를 확인하고,
빈 목적이면 소모 없이 지나가는 갈래를 끼운다.

## Related truth

- O-00000018 — W-00000167 등록 직후 실측: 돌아온 글에 Purpose 도 User value 도 없이 제목
  한 줄뿐이었다. 이 카드가 닫히면 그 관측을 닫는다.


## Progress


## Verification


## Retrospective


## Promotion decision
