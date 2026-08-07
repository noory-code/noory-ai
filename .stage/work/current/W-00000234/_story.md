---
id: W-00000234
title: 실행 결과를 들이는 명령이 게이트를 어떻게 지나는지 정한다
kind: design
venue: claude
milestone: M-00000004
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/decisions/, .stage/operations/
promotes:
decision_refs:
---

# W-00000234 실행 결과를 들이는 명령이 게이트를 어떻게 지나는지 정한다

## Purpose

실행이 끝난 결과를 본 가지로 들이려면 감시 대상 소스를 커밋해야 하는데 그 시점에는 열린 작업이 없어 커밋 게이트가 막고, 지금은 사람이 병합용 작업 항목을 새로 등록해 지나가므로, 그 명령이 어떤 자격으로 게이트를 지나는지 결정으로 정한다

## Actions

없음 — 결정 하나를 세우는 한 덩어리다. 명령을 만드는 것은 이 결정 뒤의 별도 카드다.

## User value

실행 결과를 들일 때마다 사람이 병합용 작업 항목을 새로 등록하는 일이 없어진다. 지금은 그렇게
지나가고 있고, 그 항목은 병합 말고는 아무 일도 담지 않는다.

## Scope

### Included

- 결정 하나를 세운다: 실행이 끝난 결과를 본 가지로 들이는 명령이 **무엇을 하고**, **어떤
  자격으로 커밋 게이트를 지나는가**.
- 하는 일의 후보는 오늘 사람이 손으로 한 것들이다 — 워크트리 로그를 본 저장소로 옮기기,
  워크트리에서 커밋하기, 본 가지에 병합하기, 워크트리와 가지 치우기.
- 게이트를 지나는 자격은 이 저장소에 이미 있는 두 모양을 먼저 본다: 보관 명령이 쓰는 통행증
  (`archive_intent`)과 승격 통행증(`promote_intent.py`). 새 축을 만들기 전에 그것들로 되는지
  본다(AHA).
- 그 자격이 **다른 자리의 감시를 넓히지 않는다**는 것을 결정에 적는다. 게이트를 넓히는 결정은
  이 프로젝트에서 늘 위험으로 다뤄 왔다.

### Excluded

- 명령을 만들지 않는다. 이 카드는 결정만 세운다.
- 사람 몫으로 남는 것은 안 건드린다 — 판정 지적의 처분, 회고 본문, 닫을지의 결정.
- 팀원 실행과 무인 실행을 갈라 정하지 않는다. 둘 다 같은 자리에서 막히므로 한 결정이 둘을
  덮어야 한다.

## Risks

- **게이트를 여는 일이다.** 열린 작업 없이 감시 대상 소스를 커밋할 수 있게 만드는 것이므로,
  그 자격이 이 명령이 하는 병합 말고 다른 커밋으로 새면 안 된다.
- 지금의 우회(병합용 작업 항목 등록)는 정직하지만 비싸다. 결정이 그것보다 나쁘면 안 바꾸는
  것이 낫다 — 그 판단을 결정에 적는다.

## Success criteria

- 들이는 명령이 무엇을 하고 어떤 자격으로 커밋 게이트를 지나는지가 결정 기록 하나에 정해져 있다
- 그 자격이 다른 자리의 감시를 넓히지 않는다는 것이 결정에 적혀 있다

## Next action

`archive_work.py` 와 `promote_intent.py` 가 게이트를 지나는 방식을 읽고, 그중 하나로 되는지
먼저 본다. 안 되면 무엇이 모자란지를 결정에 적는다.

## Related truth

- O-00000035 — 병합 때 열린 작업이 없어 커밋 게이트가 막은 실측. 충돌이 없으면 조용히
  지나가는 것도 그 관측이 든다.
- M-00000004 완료 기준 첫째 — 이 결정이 그 기준의 앞쪽 절반이다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
