---
id: W-00000226
title: 드라이버 스킬이 명령 시간 한도가 어디서 나오는지 적는다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000226 드라이버 스킬이 명령 시간 한도가 어디서 나오는지 적는다

## Purpose

드라이버는 카드마다 다른 명령 시간을 주는데 스킬이 그 산정 방식도 직접 지정하는 방법도 안 적어 두어 운영자가 큰 카드에서 잘리고 나서야 배우므로, 시간이 무엇에서 나오고 언제 직접 줘야 하는지를 스킬이 적게 한다

## Actions

없음 — 스킬 한 절을 더하는 한 덩어리다.

## User value

운영자가 큰 카드를 걸기 전에 시간이 모자랄지 알 수 있다. 지금은 첫 바퀴가 잘리고 나서 배우고,
그 잘림이 카드를 드라이버에서 못 나오게 만든 적이 있다(O-00000030, 이제 고쳐졌지만 잘림
자체는 여전히 한 바퀴를 버린다).

## Scope

### Included

- 드라이버 스킬에 명령 시간 한도를 설명하는 자리를 만든다:
  - 직접 안 주면 시간이 **카드가 선언한 크기**에서 나온다 — 미완 자식 수, 선언 범위 항목 수,
    성공 기준 수 중 가장 큰 값에 최소 단위를 곱한다.
  - 그래서 정말 작은 카드만 최소값을 받는다.
  - `--timeout <초>` 로 직접 줄 수 있다.
- 직접 줘야 하는 경우를 조건으로 적는다 — 선언한 크기가 실제 일의 크기보다 작을 때(범위를
  좁게 적었는데 만질 자리가 많은 카드).
- `stage/CHANGELOG.md` 에 이 문서 변경을 적는다.

### Excluded

- 산정 방식(코드) 자체는 안 바꾼다. 이 카드는 이미 있는 동작을 읽을 수 있게 만든다.
- 병렬 실행의 `--driver-timeout` 설명은 이미 있으므로 안 건드린다.

## Risks

- 스킬은 매 세션 로드되는 지시문이라, 설명이 코드와 어긋나면 운영자가 틀린 값을 믿는다.
  적기 전에 `drive.py` 의 산정 함수를 직접 읽고 맞춘다.


## Success criteria

- 스킬만 읽고도 시간을 직접 안 줬을 때 카드가 받는 시간이 무엇에서 나오는지 알 수 있다
- 직접 지정해야 하는 경우가 추측 없는 조건으로 적혀 있다
- 스킬이 적은 산정 방식이 현재 코드와 일치한다

## Next action

`drive.py` 의 `declared_command_size` 와 `subtree_command_timeout` 을 읽어 실제 산정을 확인한
뒤, 스킬에서 드라이버 실행을 설명하는 자리에 그 절을 넣는다.

## Related truth

- O-00000031 (닫힘) — 액션 없는 스토리가 크기와 무관하게 최소 시간을 받던 실측. W-00000218 이
  산정을 카드 선언 크기 기반으로 바꿔 고쳤고, 이 카드는 그 동작을 읽을 수 있게 만든다.
- DE-00000062 — 이 카드가 첫 팀원 실행 실측이다.


## Progress


## Verification


## Retrospective


## Promotion decision
