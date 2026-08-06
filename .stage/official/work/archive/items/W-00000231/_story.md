---
id: W-00000231
title: stage 0.60.0 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000230
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000231 stage 0.60.0 을 낸다

## Purpose

병렬 명령이 무인 모드를 넘기는 기능과 명령 시간 한도 설명이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다른 프로젝트도 카드 여러 장을 무인으로 한 번에 걸 수 있고, 큰 카드를 걸기 전에 시간이
모자랄지 스킬만 읽고 알 수 있다. 지금은 둘 다 이 저장소 안에만 있다.

## Scope

### Included

- 부 버전을 올린다(0.59.0 → 0.60.0). 병렬 명령에 없던 옵션이 생겼으므로 고침이 아니라
  기능이다.
- 쌓인 변경 기록 두 묶음에 그 버전 제목을 붙이고 다음을 위한 빈 자리를 연다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- 릴리스를 한 번에 커밋하고 푸시한다.

### Excluded

- 다른 프로젝트를 옮기지 않는다. 보태는 변경이라 옛 프로젝트가 그대로 돈다.
- 마일스톤에 걸지 않는다. 셋 다 닫혔고 릴리스는 어차피 완료 기준을 안 움직인다
  (O-00000027 이 남긴 규칙).

## Risks

- 릴리스는 푸시까지가 한 몸이라 되돌리기가 비싸다. 감사와 시험을 먼저 통과시킨다
  (훅 361, 스크립트 599, 둘 다 통과 확인함).
- 코덱스 런타임이 새 버전 캐시를 못 집으면 다음 세션의 훅이 막힌다(P-00000001). 두 번 연속
  코덱스를 한 번 돌리자 집었으므로 같은 순서로 확인한다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.60.0 하나를 말한다
- 릴리스가 원격에 올라가 다른 프로젝트가 받을 수 있다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.


## Progress

0.59.0 → 0.60.0. 쌓여 있던 두 묶음에 그 버전 제목이 붙었고 두 매니페스트가 같은 값을 말한다.
커밋 `007db63f` 로 푸시 완료.

**쓸 수 있는지 확인했고, 한 자리가 안 됐다.** 원격 매니페스트는 0.60.0 을 말한다. 이 기계의
클로드 쪽은 저장소 디렉터리를 원본으로 읽어 이미 새 내용으로 돈다. **코덱스 쪽 캐시는
0.59.0 에 머물렀다** — 알려진 완화책(코덱스를 한 번 돌린다)을 세 번 썼는데 안 통했다. 오늘
0.57.0·0.59.0 에서는 첫 번째에 통했던 그 방법이다. O-00000037 로 남겼다.

## Verification

성공 기준 셋 다 충족했다 — 매니페스트 둘과 변경 기록이 0.60.0 하나를 말하고, 원격에 올라가
받을 수 있고, 감사가 오류 없이 통과한다(시험도 훅 361 + 스크립트 599 통과).

**다만 이 기계에서 다음 코덱스 실행이 막힌다.** 릴리스 자체의 결함은 아니지만(원격은 정상,
받는 쪽 캐시 문제다) 운용에 바로 걸리는 자리라 O-00000037 이 든다. 다음 세션은 캐시부터
확인해야 한다.


### Executed at close — 2026-08-06

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

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.298s

OK
```

## Verification


## Retrospective


## Promotion decision
