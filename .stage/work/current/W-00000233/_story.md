---
id: W-00000233
title: 일의 종류에 맞는 모델을 고르는 기준을 절차가 갖게 한다
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
promotion: pending
review: not_required
scope: .stage/operations/claude-venue.md
promotes:
decision_refs:
---

# W-00000233 일의 종류에 맞는 모델을 고르는 기준을 절차가 갖게 한다

## Purpose

팀원을 띄울 때 모델을 안 정하면 부모 세션 모델을 그대로 물려받아 문구 다듬기 같은 기계적인 일에도 제일 무거운 모델이 붙으므로, 일의 종류에서 모델이 나오는 기준을 절차가 갖게 한다

## Actions

없음 — 절차에 고르는 기준 한 절을 더하는 한 덩어리다.

## User value

문구 하나 다듬는 일에 제일 무거운 모델이 붙는 일이 없어진다. 지금은 모델을 안 주면 부모
세션 것을 그대로 물려받고, 그것이 기본이라 아무도 안 정한 채로 굴러간다.

## Scope

### Included

- 절차에 "모델을 고른다" 걸음을 넣는다. 고르는 근거는 **카드의 `kind`** 다 — venue 가 이미
  같은 방식으로 정해지므로(`venue_routing`) 새 축을 만들지 않고 같은 신호를 쓴다.
- 종류별로 어느 쪽을 주는지 표로 적는다. 형용사("가벼운 일")가 아니라 종류 이름으로 가른다.
- **아껴서는 안 되는 자리**를 근거와 함께 적는다 — 판정이다. O-00000024 가 72바퀴로 판정이
  실행보다 출력 2.9배를 쓴다고 쟀고, 오늘 하루에만 판정이 실질 결함을 다섯 번 잡았다.
  값이 큰 만큼 값을 하는 자리라 여기서 내리면 잡던 것을 놓친다.
- 모델을 안 주면 부모 것을 물려받는다는 사실을 적는다. 그것이 이 구멍의 원인이다.

### Excluded

- codex 몫 실행자의 모델은 안 다룬다. 그쪽은 `.stage/settings.json` 의 실행자 명령이 이미
  모델을 문자열로 박고 있어 이 문서의 소유가 아니다.
- 종류별 배정을 실측으로 뒷받침하지 않는다. 실측이 없다 — 이 카드는 기본값을 세우는 것이고,
  어긋나면 그때 고친다. 그 사실을 표 옆에 적는다.

## Risks

- 실측 없이 정하는 기준이다. 너무 낮게 잡으면 일이 안 되고, 너무 높게 잡으면 지금과 같다.
  그래서 판정만은 근거(O-00000024)로 고정하고 나머지는 바꿀 수 있는 기본값으로 적는다.

## Success criteria

- 절차만 보고 이 카드에 어떤 모델을 줄지 정할 수 있고, 그 판단에 형용사가 아니라 일의 종류가 쓰인다
- 아껴서는 안 되는 자리가 근거와 함께 적혀 있다

## Next action

`.stage/operations/claude-venue.md` 의 감독 모드 절차에서 팀원을 띄우는 걸음 옆에 모델 고르는
절을 넣는다. W-00000232 가 같은 파일의 3번 걸음을 고치는 중이므로 그 결과 위에 얹는다.

## Related truth

- O-00000024 — 판정이 실행보다 출력 2.9배, 입력 1.3배를 쓴다(72바퀴 실측). 아낄 자리와 안
  아낄 자리를 가르는 근거다.
- W-00000232 — 같은 파일의 팀원 띄우기 걸음을 고치는 카드. 이 카드가 그 뒤에 온다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
