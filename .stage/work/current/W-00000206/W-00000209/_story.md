---
id: W-00000209
title: 빈 목적으로 시작하는 길을 막는다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-work/register_work.py, stage/scripts/audit_stage.py, stage/templates/v4/, stage/skills/stage-work/SKILL.md, stage/scripts/tests/test_register_work.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000209 빈 목적으로 시작하는 길을 막는다

## Purpose

목적과 끝나는 자리가 비어도 카드가 만들어져서 목적이 일의 결과로 적히므로, 등록과 감사가 빈 카드를 거부해 시작하는 순간에 답이 있게 만든다

## Actions

없음 — 등록이 거부하는 것과 감사가 잡는 것은 같은 규칙의 앞뒤다.

## User value

목적을 안 캐냈으면 일을 시작조차 못 한다. 지금은 빈 카드로 시작해서 목적을 나중에 채우고,
그러면 목적이 일의 결과가 된다.

## Scope

### Included

- **목적 없이 등록 못 하게 한다.** 지금 `--purpose` 는 선택 항목이고 기본값이 빈 문자열이라
  목적이 아예 없는 카드가 만들어진다.
- **끝나는 자리 없이 등록 못 하게 한다.** 성공 기준을 받아서 카드에 쓰고, 비면 거부한다.
- **감사가 목적과 성공 기준이 빈 카드를 잡는다.** 지금은 안 본다.
- 거부 문구가 무엇을 해야 하는지 말한다. "목적이 없다"가 아니라 "사람에게 무엇을 이루려는지
  묻고 그 답을 넣어라"로 읽혀야 한다.
- 새 규칙을 켜기 전에 이 저장소의 기존 카드 중 빈 것이 몇 장인지 센다.

### Excluded

- 지어낸 목적은 안 잡는다. 못 잡는다 — 기계 눈에는 사람이 말한 문장과 내가 만든 문장이 같은
  글자다(DE-00000059). 그 자리는 사람이 카드 첫 줄에서 본다.
- 카드에 칸을 새로 안 만든다. 이미 있는 목적과 성공 기준을 비게 두지 않을 뿐이다.

## Risks

- **이미 있는 카드가 무더기로 걸릴 수 있다.** 켜기 전에 세고, 많으면 채우는 일이 따로 필요하다.
- 계획 카드는 본문이 얇게 잡히기 쉬운데, 그것도 같은 규칙을 지려면 등록할 때 답이 있어야 한다.
  계획으로 잡는 편의를 없애는 쪽이 맞는지 구현하면서 확인한다.
- 거부 문구가 불친절하면 다음 사람은 빈칸을 채우는 요령만 배운다. 무엇을 해야 하는지 말해야 한다.

## Success criteria

- 목적이 비면 등록이 거부하고, 무엇을 해야 하는지 알려 준다.
- 끝나는 자리가 비면 거부한다.
- 목적이나 끝나는 자리가 빈 카드가 저장소에 있으면 감사가 잡는다.
- 빈 카드를 만들고 나중에 채우는 길이 남아 있지 않다.

## Next action

`register_work.py` 의 `--purpose` 를 필수로 바꾸고, 성공 기준을 받는 자리를 만든다.

## Related truth

- DE-00000059 — 무엇을 막고 무엇을 못 막는지 정했다.
- W-00000190 — 등록에 질문 셋을 넣은 카드. 묻기만 해서는 안 바뀐다는 것이 그 뒤 여덟 번으로
  드러났다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
