---
id: W-00000234
title: 실행 결과를 들이는 명령이 게이트를 어떻게 지나는지 정한다
kind: design
venue: claude
milestone: M-00000004
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000236
promotion: promoted
review: not_required
scope: .stage/decisions/, .stage/operations/
promotes: .stage/official/decisions/records/DE-00000065.md
decision_refs: DE-00000065
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

## Progress

DE-00000065 을 세웠다. 팀원이 창에서 다섯 바퀴 돌았고 codex 가 다섯 번 판정했다. 병합
`d39aeaad`.

**두 통행증은 이 자리를 못 덮는다.** 커밋 게이트는 통행증을 아예 안 읽고, 통행증을 소비하는
유일한 자리는 공식 경로에만 걸린다. 모자란 것은 통행증의 종류가 아니라 커밋 게이트에 허가
축이 없다는 것이다.

**고른 방향** — 하니스가 들이는 명령을 갖고 훅에 통행증을 만들지 않는다. 명령은 하니스 가지
에서만, 생애주기가 최종인 카드에 대해서만, 카드 선언 범위와 **정확히 두 생애주기 기록**(카드
파일과 `retrospective_ref` 가 가리키는 회고)만 담아, `--no-ff --no-commit` 으로 충돌을 먼저
보고 남은 조건까지 통과한 뒤에야 병합 커밋을 만든다. 두 커밋 모두 메시지에 카드와 원본
가지를 담는다 — 서브프로세스 커밋은 훅에 안 보이므로, 기록이 없으면 조용한 우회가 된다.

## Verification

인수는 감독이 팀원 워크트리에서 직접 돌렸다(감사 오류 0). 판정은 codex 가 다섯 바퀴 봤고
**성공 기준 둘 다 마지막 바퀴에 통과**했다. 지적 스물둘을 전부 받아 고쳤다 — 뒤로 갈수록
무거워졌다: 문구 → 틀린 증명 → 안전 구멍 둘 → 자기모순.

**판정이 잡은 안전 구멍 둘**은 결정을 실제로 바꿨다. 완료 카드가 회고 참조 없이 들어갈 수
있던 자리(완료 검사가 참조를 안 본다)와, 충돌 검사가 기록 조건보다 앞서 미검사 병합이 본
가지에 생길 수 있던 자리다.

**남는 한계 하나, 알고 문다** — 커밋 메시지에 기록이 빠진 것을 감사가 못 잡는다. 감사는
`.stage/` 산출물을 보지 이력을 안 훑는다. 무는 이유는 창이 없다는 것이 세는 것보다 앞서기
때문이다. 감사를 넓히는 일은 결정의 Follow-up 에 별도 카드로 있다.

**감독이 직접 고친 자리 하나** — 마지막 판정이 남긴 행 번호 오류(`drive.py:1530` → `:1556`)를
팀원에게 여섯 번째로 보내는 대신 감독이 고쳤다. 그 한 줄에 대해서는 만든 쪽과 보는 쪽이
같아졌다. 숨기지 않고 여기 적는다.

### Executed at close — 2026-08-07

```
$ python3 stage/scripts/audit_stage.py --project-root .
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

$ python3 stage/scripts/audit_stage.py --project-root .
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

R-00000236 참조.

## Promotion decision

approved — DE-00000065 를 `.stage/official/decisions/records/` 로 승격한다.
