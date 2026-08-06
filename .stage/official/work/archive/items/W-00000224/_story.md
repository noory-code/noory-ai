---
id: W-00000224
title: 감독 모드의 claude venue 실행을 세션 팀원에게 맡기기로 정한다
kind: design
venue: claude
milestone: M-00000003
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000221
promotion: promoted
review: not_required
scope: .stage/decisions/, .stage/operations/, .stage/settings.json
promotes: .stage/official/decisions/records/DE-00000062.md
decision_refs: DE-00000062
---

# W-00000224 감독 모드의 claude venue 실행을 세션 팀원에게 맡기기로 정한다

## Purpose

claude venue 카드를 일회성 claude -p 실행자에게 주면 어디서든 명령 권한이 없어 인수 검사를 못 돌리고 막히기만 하므로, 감독 모드에서는 세션의 팀원 에이전트가 계약 문구를 그대로 물려받아 실행하고 중간에 사람에게 물을 수 있게 정한다

## Actions

없음 — 결정 기록과 절차 문서를 쓰는 한 덩어리다.

## User value

claude venue 카드가 권한 없는 실행자에게 가서 멈추는 일이 없어지고, 실행 중 갈림길이 사람에게
질문으로 돌아온다. 사용자가 밝힌 선호(클로드는 에이전트 팀)가 기록된 결정이 된다.

## Scope

### Included

- 결정 기록 DE-00000062: 감독 모드 claude venue = 세션 팀원 실행(워크트리 격리, 계약 상속,
  중간 질문 허용), 인수·닫기 = 감독, 판정 = codex, 무인 = codex 전용, 팀 없으면 handoff.
- 절차 문서 `.stage/operations/claude-venue.md` — 다음 claude 카드부터 따를 다섯 걸음.
- 결정의 공식 승격(이 카드의 마지막 걸음).

### Excluded

- `settings.json` 의 `executors.claude` 와 `review.reviewers.claude` 는 안 고친다 — 앞은
  드라이버 경로의 정의로 남고, 뒤는 이 결정의 범위 밖이다(판정은 읽기·쓰기만으로 돈다).
- 플러그인(stage-drive 문서·기본 설정)은 안 고친다 — 이 프로젝트에서 실측한 뒤 별도 카드로
  승격을 제안한다.

## Risks

- 아직 실측이 없는 설계다. 첫 팀원 실행이 로그 계약(실행 보고 형식)과 실제로 맞는지 확인해야
  하고, 그 실측 전까지 플러그인으로 승격하지 않는다.

## Success criteria

- 감독 모드 claude venue 의 실행 방식(팀원 실행, 워크트리 격리, 계약 상속, 중간 질문 허용, 인수·닫기는 감독, 판정은 codex, 무인은 codex 전용)이 결정 기록 하나에 정해져 있다
- 다음 claude venue 카드를 팀원으로 돌릴 때 따를 절차가 운영 문서에 적혀 있다

## Next action

DE-00000062 를 공식으로 승격하고 카드를 닫는다.

## Related truth

- DE-00000062 — 이 카드가 정한 결정.
- W-00000220(R-00000220) — 권한 구멍이 워크트리 문제가 아니라 비대화형 구조임을 잰 측정.
- M-00000003 기준 ① — 측정된 원인의 "고침"을 이 결정이 고른다.

## Progress

DE-00000062 작성(결정됨), `.stage/operations/claude-venue.md` 작성. 결정의 네 적용 자리를
세어 기록했다 — 실행자 설정(남김), 판정자 설정(범위 밖), 절차 문서(신설), 플러그인 문서
(실측 뒤 별도 제안).

## Verification

성공 기준 둘 다 산출물 자체로 확인된다 — 결정 기록 한 장과 절차 문서 한 장.

### Executed at close — 2026-08-06

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
ve/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
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
WARNING ROUTE002 [.stage/operations/claude-venue.md]: Operations document `operations/claude-venue.md` is not routed in index.md.
Summary: errors=0, warnings=33

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
ve/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
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
WARNING ROUTE002 [.stage/operations/claude-venue.md]: Operations document `operations/claude-venue.md` is not routed in index.md.
Summary: errors=0, warnings=33
```

## Retrospective


## Promotion decision

approved — DE-00000062 를 `.stage/official/decisions/records/` 로 승격한다.
