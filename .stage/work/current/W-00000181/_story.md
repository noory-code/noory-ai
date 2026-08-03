---
id: W-00000181
title: 오늘 실린 stage 변경을 릴리스한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/
promotes:
decision_refs:
---

# W-00000181 오늘 실린 stage 변경을 릴리스한다

## Purpose

오늘 실린 변경이 아직 어느 프로젝트에도 안 닿는다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

이 저장소가 자기가 만든 것을 실제로 쓴다. 지금은 이틀치 변경이 저장소 안에만 있고, 다른
프로젝트는 물론 이 프로젝트의 다른 창에도 안 닿는다.

## Scope

### Included

- `stage` 플러그인을 0.56.0 으로 올린다. 변경 기록에 쌓인 22개가 그 이름을 받는다.
- 새 버전이 실제로 불러와지는 것을 확인한다.

### Excluded

- 다른 플러그인. 이번에 바뀐 건 `stage` 뿐이다.
- 프로젝트별 설정(`.stage/`). 그건 이 저장소 것이고 플러그인이 배포하지 않는다.

## Risks

- **올려도 안 잡힐 수 있다.** 코덱스 쪽이 옛 버전을 들고 있는 상태가 실재한다. 그래서 이 종류의
  통과 기준이 "불러와지는 것까지"다.
- **바뀐 것 중에 게이트가 여럿이다.** 다른 프로젝트가 이 버전을 받으면 전에 없던 이유로 닫기가
  막힐 수 있다. 변경 기록이 그 이유를 말하는지 확인한다.

## Success criteria

- 버전이 변경 기록과 두 매니페스트에서 0.56.0 으로 같다.
- 그 커밋이 원격에 올라갔다.
- **새 버전이 실제로 불러와지는 것을 봤다.** 올린 것만으로는 통과가 아니다(DE-00000054).

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor` 를 돌린다. 그다음 새 버전이
잡히는지 확인한다.

## Related truth

- **DE-00000054** — 릴리스는 자기 종류를 갖고 클로드로 간다. 통과 기준이 "올렸다"가 아니라
  "쓸 수 있다"인 이유가 거기 있다.


## Progress


## Verification


## Retrospective


## Promotion decision
