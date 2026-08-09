---
id: W-00000250
title: 무인 실행이 끝난 뒤 사람이 잇는 구간에서 게이트가 안 막게 한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000250
promotion: promoted
review: not_required
scope: stage/scripts/, stage/hooks/, .stage/decisions/, .stage/state/
promotes: .stage/official/decisions/records/DE-00000068.md
decision_refs: DE-00000068
---

# W-00000250 무인 실행이 끝난 뒤 사람이 잇는 구간에서 게이트가 안 막게 한다

## Purpose

카드를 옳게 거절한 실행이 무인에서 커밋 실패로 판정돼 시도를 태우고 카드가 막힘으로 남으므로, 담을 경로 중 아직 없는 것 때문에 담기가 통째로 실패하지 않게 정한다

## Actions

없음 — 결정 하나다.

## User value

실행자가 "이 카드는 틀렸다"고 옳게 판단했을 때 그 판단이 그대로 사람에게 온다. 지금은 하니스
오류로 덮여서, 사람이 원인을 찾으려면 실행 가지의 결정 기록까지 열어야 한다.

## Scope

### Included

**등록 시점에 이 카드가 재고 좁힌 것.** 시작한 뒤 코드를 읽고 실제로 돌려 확인했다.

| 잰 것 | 값 |
|---|---|
| O-00000035(병합 때 열린 작업이 없어 막힘) | **해소됨.** `land_run.py` 가 셋째 길을 구현했고 2026-08-09 에 W-00000252 를 실제로 들였다. 관측을 닫았다 |
| O-00000034 의 첫 방아쇠(카드만 바뀜) | **해소됨.** `driver_git.py:93-95` 가 카드 파일을 담는 목록에 넣고, `:103` 이 "담을 것 없음"을 성공으로 읽는다 |
| O-00000034 가 적어 둔 셋째 길(계약에서 `promotion` 쓰기 빼기) | 필요 없어졌다. 첫 방아쇠가 이미 풀려서다 |
| O-00000034 의 둘째 방아쇠(선언한 경로가 아직 없음) | **살아 있다.** 이 카드가 다루는 유일한 자리 |
| 같은 모양이 걸릴 다른 자리 | 없다. `land_run.py:362` 는 diff 에서 뽑은 목록에 `add -A` 를 걸어 못 맞는 경로가 안 생기고, `commit_lifecycle` 은 `.stage` 디렉터리 하나를 넘긴다 |

- **담기가 통째로 실패하지 않게 한다.** `git add -- a b` 는 `b` 가 없으면 `a` 까지 포함해
  아무것도 안 담는다. 실측했다.
- **없는 경로를 뺐다는 것이 보고에 남는다.** 조용히 빼면 넘은 기록이 사라지는 O-00000020 과
  같은 모양이 된다.
- **삭제를 잃지 않는다.** 선언한 디렉터리의 파일이 전부 지워진 경우도 그 삭제가 담겨야 한다.

### Excluded

- 실행자 계약을 안 고친다. `promotion` 쓰기는 그대로 둔다.
- 무인 루프의 걸음 순서를 안 바꾼다. 담기가 성공하면 그 뒤의 거절 처리
  (`driver_unattended.py:536`)가 이미 제대로 돈다.
- 커밋 게이트와 승격 게이트를 안 건드린다.

## Risks

- **없는 경로를 빼는 것과 남는 경로를 거절하는 것이 반대 방향이다.** DE-00000066 은 목록 밖이
  스테이지에 올라 있으면 거절하라고 정했다. 왜 한쪽은 빼고 한쪽은 거절하는지 결정이 답해야
  한다.
- 빼는 판정을 파일 존재만으로 하면 삭제를 잃는다. 실측으로 확인했다 — 선언한 디렉터리가
  통째로 지워지면 `ls-files` 가 그 디렉터리 이름을 안 내므로 목록에서 빠지고, 삭제가 안 담긴다.

## Success criteria

- 선언한 경로 중 아직 없는 것이 있어도 나머지가 담기고, 뺀 경로가 실행 기록에 남는다
- 선언한 디렉터리가 통째로 지워진 실행에서 그 삭제가 담긴다
- 카드를 거절한 실행이 커밋 실패가 아니라 거절로 읽혀 시도를 안 태운다

## Next action

결정을 쓴다. 실측은 위 표에 있고, 후보 방식 셋을 실제로 돌려 봤다.

## Related truth

## Progress

## Verification

### Executed at close — 2026-08-09

```
$ python3 stage/scripts/audit_stage.py
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

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 372 tests in 1.459s

OK
```

## Retrospective

## Promotion decision
