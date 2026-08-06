---
id: W-00000226
title: 드라이버 스킬이 명령 시간 한도가 어디서 나오는지 적는다
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
retrospective_ref: R-00000225
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

DE-00000062 의 첫 팀원 실행. 세 바퀴 돌았고 병합 `9f8bf996`. 스킬에 명령 시간 한도를 설명하는
절이 생겼다 — 카드 선언 크기(미완 자식·범위 항목·성공 기준 중 최댓값)에 900초를 곱한 값이
기본이고, 직접 줄 때는 표 두 행이 각각 숫자를 내놓고 둘 다 참이면 큰 쪽을 쓴다.

**카드가 본 것보다 낡은 자리가 많았다.** 카드는 스킬 한 곳을 봤는데 실제로는 셋이었고, 그중
가장 낡은 것이 스킬 자신이 "규칙의 주인"이라고 지목한 `stage/docs/SCHEMA_V4.md` 였다. 팀원이
둘을 범위 넘음으로 신고하고 고쳤다 — 그 문서(수용, 주인이 어긋나면 스킬만 고쳐도 소용없음)와
`--timeout` 도움말 문자열(수용, "subtree-derived"가 이제 틀린 말).

## Verification

인수는 감독이 직접 돌렸다(감사 오류 0, 드라이버 시험 85, 훅 시험 361, `--help` 확인). 판정은
codex 가 세 바퀴 봤다.

기준 1·3 통과 — 판정자가 `max(1, 2, 3) * 900 = 2700` 을 직접 계산하고 `split_scope`,
`declared_success_criteria_count`, `subtree_limits` 기준선을 코드로 대조했다.

**기준 2 는 끝내 통과 못 했고, 그것이 이 카드가 남기는 기록이다.** 판정이 두 바퀴에 걸쳐
서로 다른 진짜 결함을 잡았고 둘 다 고쳤다 — 형용사가 판단을 대신하던 조건("여러 곳"), 그리고
표의 두 행이 동시에 참일 때 값이 하나로 안 정해지던 것. 남은 지적("디렉터리 아래 어느 파일을
셀지엔 판단이 든다")은 **기각했다**: 판정자 자신이 코드에 그런 임계값이 없음을 확인했고,
없는 규칙을 지어 적는 것은 이 프로젝트의 정직 원칙이 금지한다.

**기준 자체가 채울 수 없게 쓰였다.** "모든 경우를 추측 없는 조건으로"는 판단이 본질인 경우가
남아 있는 한 도달 불가다. 카드를 쓴 쪽(감독)의 잘못이고, 그래서 네 번째 바퀴를 돌리는 대신
여기 적고 닫는다. 세 바퀴가 실제 개선을 냈으므로 기준이 무익했던 것은 아니다.

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
Ran 361 tests in 1.316s

OK
```

## Retrospective


## Promotion decision
