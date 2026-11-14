---
id: W-00000323
title: codex 구독이 없는 동안 로컬 카드도 Claude가 실행하도록 환경을 선언한다
kind: planning
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000323
promotion: deferred
review: passed
scope: .stage/
promotes:
decision_refs: DE-00000086
---

# W-00000323 codex 구독이 없는 동안 로컬 카드도 Claude가 실행하도록 환경을 선언한다

## Purpose

codex 구독이 없는 동안에도 로컬 세션에서 codex 로 라우팅되는 카드를 예외 결정 없이 시작하고 닫을 수 있게 하되, 같은 모델이 리뷰했다는 사실이 카드마다 남게 한다

## Actions
결정 레코드 DE-00000086 을 쓰고 사용자가 확정한다. 확정 뒤 `environment_venues` 에 환경 한 줄을 더하고, `.stage/operations/claude-venue.md` 에 codex 없는 로컬 세션의 시작·닫기 명령을 적는다.


## User value
codex 구독이 없는 동안에도 로컬에서 개발·수정 카드가 막히지 않고, 나중에 어떤 카드가 같은 모델의 리뷰로 닫혔는지 카드만 보고 가려낼 수 있다.


## Scope

### Included
- 결정 레코드 DE-00000086
- `.stage/settings.json` 의 `environment_venues` 한 줄
- `.stage/operations/claude-venue.md` 의 codex 없는 로컬 세션 절차


### Excluded
- `venue_routing`, `executors`, `review` 설정 변경
- Stage 플러그인 코드와 플러그인 소유 문서 변경
- 열려 있는 codex venue 카드(W-00000271, W-00000281, W-00000282)의 재시작 — 카드마다 따로 정한다


## Risks
실행과 리뷰가 같은 모델 계열이라 둘이 함께 놓치는 결함은 닫기 리뷰가 잡지 못한다. DE-00000082 가 기대던 나중의 로컬 codex 확인도 이 기간에는 없다.


## Success criteria

- DE-00000086 이 decided 이고, 선택한 방향·적용 자리·이 결정이 틀렸음을 알리는 관측을 담는다
- .stage/settings.json 의 environment_venues 에 로컬 환경이 선언되고 venue_routing 과 review 명령은 바뀌지 않는다
- stage_work.environment_venue_error 가 새 환경에서 venue claude·review pending 카드를 허용하고, review 를 요구하지 않는 카드와 venue codex 카드를 거절한다
- .stage/operations/claude-venue.md 가 codex 없는 로컬 세션에서 카드를 시작하고 닫는 명령을 적는다
- python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다

## Next action
사용자가 DE-00000086 초안(환경 이름 `local-no-codex` 포함)을 확인한다. 확정하면 설정과 운영 문서를 고친다.


## Related truth
DE-00000082 와 `stage/operations/cloud-execution.md` 가 환경 정책과 Claude 대역 닫기 리뷰 절차를 소유한다. DE-00000062 와 `.stage/operations/claude-venue.md` 가 claude venue 실행 방식을 소유한다.


## Progress
2026-11-14: 카드를 등록하고 DE-00000086 초안을 `open` 으로 썼다. 설정과 운영 문서는 사용자 확정 전이라 고치지 않았다.

2026-11-14: 사용자가 환경 이름 `local-no-codex` 와 초안을 확정했다. DE-00000086 을 `decided` 로 바꾸고, `environment_venues` 에 한 줄을 더하고, `.stage/operations/claude-venue.md` 에 절차 절을 더했다.

2026-11-14: 회고를 쓰다가 W-00000299 의 표본 재검토 결과(5장 중 1장 반려)가 결정 레코드에 빠진 것을 찾아 Reason 과 Follow-up 에 더했다. 선택한 방향은 바뀌지 않는다.


### Executor report at close — 2026-11-14

```
What changed: DE-00000086 is decided, environment_venues declares local-no-codex -> claude, .stage/operations/claude-venue.md gains the procedure for a local session without Codex, and the decision now cites the W-00000299 resampling result.
Why: Cards routed to Codex must stay startable and closable while the subscription is paused, each such card must record that the close review was a same-model review, and the record must state what the missing cross-model check had caught before.
Decisions made: Declared a new environment instead of rewriting venue_routing, as the user chose. Named it local-no-codex, confirmed by the user. Left venue_routing, executors, and review untouched. Wrote that teammate model is inherited for kinds the model table marks as not applicable, because the table sets no value for them. Left open Codex-venue cards W-00000271, W-00000281, W-00000282 for a per-card restart decision. Added the W-00000299 evidence to Reason after the user confirmed the draft, without changing the chosen direction, and put the human-confirmation condition it suggests in Follow-up instead of adopting it. Archived W-00000288, W-00000298, W-00000299 in an earlier commit on this branch as queue upkeep outside this card. No scope boundary was crossed.
Work not done: Restarting the open Codex-venue cards, choosing teammate models for development, fix, qa, ops, and chore kinds, and deciding whether permission or verification changes need human confirmation at close.
```

## Verification

이 카드의 닫기 리뷰는 교차 venue 리뷰가 아니라 **같은 모델 계열의 리뷰**다. 클라우드 세션에서 Claude 가 실행했고, `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 로 Claude 대역이 판정했다. 실행한 쪽은 감독 세션 자신이며 팀원에게 맡기지 않았다.

첫 판정은 반려였다. 기준 넷은 통과했고, 감사 기준 하나는 대역이 `python3 -m unittest` 만 실행할 수 있어 확인하지 못했다는 이유였다. 처분: **수용** — 감독이 닫기 워크트리에서 감사를 실행해 출력을 작업 로그에 남겼고, 둘째 판정이 그 기록으로 통과시켰다. 즉 감사 기준과 판정 함수 기준은 판정자가 직접 실행한 것이 아니라 기록과 코드 읽기로 판정됐다.


### Executed at close — 2026-11-14

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
```

### Review at close — 2026-11-14

```
Review report: .stage/.runtime/driver/logs/W-00000323.md
Criteria:
- PASS: DE-00000086 이 decided 이고, 선택한 방향·적용 자리·이 결정이 틀렸음을 알리는 관측을 담는다
  Reason: Read .stage/decisions/pending/DE-00000086.md: frontmatter status is decided, it has Chosen direction (option 2), a Where this applies table, and a falsification section; the later W-00000299 evidence edit keeps the direction unchanged.
- PASS: .stage/settings.json 의 environment_venues 에 로컬 환경이 선언되고 venue_routing 과 review 명령은 바뀌지 않는다
  Reason: Ran git diff a3711c2e -- .stage/settings.json: the only change is adding "local-no-codex": "claude" under environment_venues; venue_routing, executors and review are untouched.
- PASS: stage_work.environment_venue_error 가 새 환경에서 venue claude·review pending 카드를 허용하고, review 를 요구하지 않는 카드와 venue codex 카드를 거절한다
  Reason: Did not run it (python3 invocation needed approval); read stage/hooks/stage_work.py:524 and stage_paths.load_environment_venues: declared keys are read from settings, venue must equal claude, review must be in {pending, passed}, so claude/pending is allowed and not_required or codex is rejected, matching the run table recorded in DE-00000086.
- PASS: .stage/operations/claude-venue.md 가 codex 없는 로컬 세션에서 카드를 시작하고 닫는 명령을 적는다
  Reason: Read the new local-no-codex section via git diff: it gives register_work.py and start_work.py commands with --environment local-no-codex --review and the close prefix STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py, deferring close order to cloud-execution.md.
- PASS: python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다
  Reason: I did not run it (approval required); the driver log records the supervisor running it in this worktree at f2dd21b1 with Summary errors=0, warnings=32, and the only later changes are the story's retrospective fields pointing to the existing R-00000323.md, which close_work.py re-checks.
```

## Retrospective


## Promotion decision
