---
id: W-00000233
title: 일의 종류에 맞는 모델을 고르는 기준을 절차가 갖게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000232
promotion: not_applicable
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
- **아껴서는 안 되는 자리**를 근거와 함께 적는다 — 판정이다. 판정(`review.reviewers.codex`)은
  `settings.json` 에서 kind 와 무관하게 이미 고정돼 있으므로, 이 표는 그 모델을 다루지 않는다는
  사실을 적는다.
- 모델을 안 주면 부모 것을 물려받는다는 사실을 적는다. 그것이 이 구멍의 원인이다.

### Excluded

- codex 몫 실행자의 모델은 안 다룬다. 그쪽은 `.stage/settings.json` 의 실행자 명령이 이미
  모델을 문자열로 박고 있어 이 문서의 소유가 아니다.
- 종류별 배정을 실측으로 뒷받침하지 않는다. 실측이 없다 — 이 카드는 기본값을 세우는 것이고,
  어긋나면 그때 고친다. 그 사실을 표 옆에 적는다.

## Risks

- 실측 없이 정하는 기준이다. 너무 낮게 잡으면 일이 안 되고, 너무 높게 잡으면 지금과 같다.
  판정(`review.reviewers.codex`)은 이 표와 무관하게 이미 고정돼 있어 이 위험 밖에 있고,
  나머지 kind 배정만 바꿀 수 있는 기본값이다.

## Success criteria

- 절차만 보고 이 카드에 어떤 모델을 줄지 정할 수 있고, 그 판단에 형용사가 아니라 일의 종류가 쓰인다
- 아껴서는 안 되는 자리가 근거와 함께 적혀 있다

## Next action

`.stage/operations/claude-venue.md` 의 감독 모드 절차에서 팀원을 띄우는 걸음 옆에 모델 고르는
절을 넣는다. W-00000232 가 같은 파일의 3번 걸음을 고치는 중이므로 그 결과 위에 얹는다.

## Related truth

- O-00000024 — 클로드 판정 세션이 코덱스 실행 세션보다 토큰을 많이 쓴다는 것을 72바퀴로
  쟀다(출력 2.9배, 입력 1.3배). 이 카드가 다루는 codex 판정자(`review.reviewers.codex`)를
  잰 것은 아니다 — 배경으로만 남긴다.
- W-00000232 — 같은 파일의 팀원 띄우기 걸음을 고친 카드. 이 카드가 그 위에 얹혔다.

## Progress

절차에 kind 별 모델 표가 들어갔다. 병합 `f0df6048`. 팀원은 sonnet 으로 돌았다 — 이 카드가
세우는 규칙이 자기 자신에게 배정하는 값과 같다.

## Verification

인수는 감독이 팀원 워크트리에서 직접 돌렸다(감사 오류 0, 경고 32 — 기준선과 같음). 판정은
codex 가 두 바퀴 봤고 두 번 다 반려했으며, 지적 여섯을 전부 받아 고쳤다.

기준 1 — 통과. 표가 kind 이름으로 가르고 형용사를 안 쓴다. 처음 배정한 `documentation`·
`release` 최경량은 판정이 반례로 뒤집었고(같은 kind 카드가 판단으로 여러 바퀴를 돈 것,
릴리스 통과 기준이 "불러와짐 관측"인 것), 근거를 사건이 아니라 규칙 문서로 옮겼다.

기준 2 — 통과. 다만 도달 방식이 처음 의도와 다르다. 이 표는 판정자 모델을 아예 안 다룬다는
것이 밝혀졌으므로(설정이 kind 와 무관하게 고정한다), "아껴서는 안 되는 자리"를 이 표 안에서
찾을 수 없다. 대신 그 자리가 어디서 정해지는지와, 바꾸려는 사람이 먼저 읽을 기록이 어디
있는지를 적었다.

**감독의 잘못 둘이 이 카드에서 드러났다.** 하나는 내가 카드에 적어 준 근거였다 — O-00000024
가 비용을 쟀을 뿐인데 "비싸니 값을 한다"로 읽었고, 팀원이 그대로 옮겼다. 판정이 잡았다.
둘은 판정이 릴리스 행의 근거를 확인하다 찾은 것으로, 이 카드 밖의 일이다(O-00000039).

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

R-00000232 참조.

## Promotion decision

not_applicable — 결정 기록을 걸지 않았고 승격 경로도 없다.
