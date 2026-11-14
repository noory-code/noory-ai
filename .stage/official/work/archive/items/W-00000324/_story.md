---
id: W-00000324
title: codex 가 없는 동안 권한·닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다
kind: planning
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000324
promotion: deferred
review: passed
scope: .stage/
promotes:
decision_refs: DE-00000087
---

# W-00000324 codex 가 없는 동안 권한·닫기·검증 절차를 바꾸는 카드는 사용자 확인 뒤에 닫는다

## Purpose

같은 모델의 리뷰가 실제로 놓쳤던 종류의 카드가, 다른 모델 계열이 없는 기간에도 사람의 눈을 거쳐서만 닫히게 한다

## Actions
DE-00000087 을 쓰고 `.stage/operations/claude-venue.md` 에 대상 경로와 닫는 순서를 적는다. 이 카드 자신이 `.stage/operations/` 를 바꾸므로 대상이다 — 리뷰 판정 뒤 사용자 확인을 받고 닫는다.


## User value
다른 모델의 검토가 없는 기간에도, 관문을 약하게 만들 수 있는 변경은 사용자가 직접 본 뒤에만 닫힌다.


## Scope

### Included
- 결정 레코드 DE-00000087
- `.stage/operations/claude-venue.md` 의 절차 절


### Excluded
- 감사 규칙이나 닫기 도구로 강제하는 구현
- 이미 닫힌 카드의 소급 확인(W-00000323 은 `.stage/settings.json` 을 바꿨고 이 규칙 이전에 닫혔다)


## Risks
도구가 강제하지 않으므로 감독이 대상임을 놓치면 확인 없이 닫힌다. 표본 5장에서 나온 규칙이라 경로 목록이 좁을 수 있다.


## Success criteria

- DE-00000087 이 decided 이고, 어떤 경로를 바꾼 카드가 대상인지 경로 목록으로 적는다
- .stage/operations/claude-venue.md 가 대상 경로, 사용자에게 보여 줄 것, 확인을 카드에 적는 자리, 닫기 명령을 돌리는 시점을 적는다
- 이 카드 자신이 대상이므로, 사용자가 변경 요약과 리뷰 판정을 보고 확인한 날짜가 이 카드의 Verification 에 적힌 뒤에 닫힌다
- python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다

## Next action
닫기 리뷰 판정을 받은 뒤 사용자에게 변경 요약과 판정을 보여 주고 확인을 기다린다.


## Related truth
DE-00000086 이 codex 없는 기간의 실행 환경을, W-00000299 가 표본 재검토 결과와 권고를 소유한다.


## Progress
2026-11-14: 사용자 지시로 카드를 등록하고 DE-00000087 과 운영 문서 절을 썼다.


### Executor report at close — 2026-11-14

```
What changed: DE-00000087 is decided and .stage/operations/claude-venue.md gains the section naming the target paths and the close order; DE-00000086 Follow-up now points at the new decision.
Why: The kind of card a same-model review already missed once must pass a human before closing while Codex is unavailable.
Decisions made: Limited the condition to cards that change gate paths rather than every environment card, to keep confirmation meaningful. Defined the target by changed path, not by judgment. Listed the paths from where W-00000295 changed things plus the hooks, close, audit, driver, settings, and operations paths. Did not implement tool enforcement and said so in the record. Did not retroactively apply the rule to W-00000323. Edited one Follow-up line in DE-00000086, owned by closed card W-00000323, to link the answer. No scope boundary was crossed.
Work not done: Enforcing the rule in the audit or close tooling, and closing this card, which waits for the user's confirmation under its own rule.
```

## Verification

사용자 확인 — 2026-11-14. 감독이 사용자에게 바뀐 경로 세 개와 한 줄씩의 요약, 규칙의 대상 경로와 닫는 순서, 도구가 강제하지 않는다는 한계, 기준별 리뷰 판정(셋 통과, 사용자 확인 기준 하나 미충족), 감사 기준은 리뷰어가 직접 실행하지 못하고 감독의 기록으로 판정했다는 것을 보여 주었다. 사용자가 그대로 확정하라고 답했다.

이 카드의 닫기 리뷰는 교차 venue 리뷰가 아니라 **같은 모델 계열의 리뷰**다. 클라우드 세션에서 감독 세션 자신이 실행했고 Claude 대역이 판정했다. 첫 판정은 사용자 확인 기준이 아직 충족되지 않았다는 이유로 반려였다. 처분: **수용** — 사용자 확인을 받아 위에 적었다.


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
Review report: .stage/.runtime/driver/logs/W-00000324.md
Criteria:
- PASS: DE-00000087 이 decided 이고, 어떤 경로를 바꾼 카드가 대상인지 경로 목록으로 적는다
  Reason: DE-00000087 frontmatter is status: decided and Chosen direction holds a path table (hooks, review companions, close_work.py, audit_stage.py, driver scripts, settings, operations) plus the environment condition, and states the rule is not tool-enforced.
- PASS: .stage/operations/claude-venue.md 가 대상 경로, 사용자에게 보여 줄 것, 확인을 카드에 적는 자리, 닫기 명령을 돌리는 시점을 적는다
  Reason: The new section (lines 125-150) lists the same target paths as the decision, the three things to show the user, the '사용자 확인 — <날짜>' line in ## Verification, and that the closed card moves to the main branch only after confirmation.
- PASS: 이 카드 자신이 대상이므로, 사용자가 변경 요약과 리뷰 판정을 보고 확인한 날짜가 이 카드의 Verification 에 적힌 뒤에 닫힌다
  Reason: The card's ## Verification now carries '사용자 확인 — 2026-11-14' with what the user saw (paths, summary, rule limits, per-criterion verdict, audit judged from records), matching the driver log's user-confirmation evidence; the card is still active, so closing follows the confirmation.
- PASS: python3 stage/scripts/audit_stage.py --project-root . 가 errors=0 을 낸다
  Reason: I did not run the command (execution was denied in this review); judged from the supervisor's driver-log record showing 'Summary: errors=0, warnings=32' at commit cdd7d0c3, with later edits limited to card text and the retrospective file.
```

## Retrospective


## Promotion decision
