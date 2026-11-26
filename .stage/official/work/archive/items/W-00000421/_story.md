---
id: W-00000421
title: 규칙 후보는 두 번 보면 묻지 않고 규칙이 되고, 한 번 본 것은 사람이 잡은 것만 사용자가 판정한다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000421
promotion: deferred
review: passed
scope: stage/skills/stage-retrospective/rule-promotion.md,stage/skills/stage-retrospective/SKILL.md,stage/skills/stage-orchestrate/SKILL.md,stage/hooks/stage_memory_index.py,stage/hooks/stage_context.py,stage/hooks/README.md,stage/hooks/tests,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/operations/cloud-execution.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs: DE-00000104
---

# W-00000421 규칙 후보는 두 번 보면 묻지 않고 규칙이 되고, 한 번 본 것은 사람이 잡은 것만 사용자가 판정한다

## Purpose

회고의 규칙 후보가 사용자 판정 0건인 채 쌓이지 않고, 두 번 본 것은 규칙이 되고 한 번 본 것은 사람이 잡은 것만 사용자에게 온다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- rule-promotion.md 의 둘째 시험이 사람이 잡은 것이나 병합·릴리스 뒤에 드러난 것을 들고, 닫기 리뷰어와 CI 가 잡은 것은 뺀다
- 회고가 스스로 두 번째라고 적은 후보는 두 번 본 것으로 센다
- 세션 색인이 proposed: promote 줄과 나머지 후보의 수를 싣는다
- 두 번 본 줄은 사용자 판정 없이 규칙이 되고 한 번 본 줄은 판정을 기다리며, PO 스킬은 한 번 본 것의 표와 집계 한 줄만 사용자에게 보인다
- 누가 잡았는지 적지 않은 한 번짜리 후보는 hold 다

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6NLyvitbSjC79DvT8T — pm — 2026-11-26 — opened from the index: DE-00000104

## Progress

- 2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 문턱은 사용자가 2026-11-25 에 정했고 DE-00000104 에 적었다. 성공 기준 다섯 줄은 토론 세션의 초안이고 사용자가 PO 세션에서 그대로 진행하라고 했다("네"). 고칠 자리는 DE-00000104 의 "Where this applies" 에 있다.
- 범위 밖: `.stage/state/rule-candidates.md` 에 새 문턱을 적용하는 일(다음 카드), 올린 규칙을 빼는 방법.
- 새 브리핑(`--po-session`, `--role pm`)으로 뜨는 첫 PM 세션이다.
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-26 PM 세션 session_018VXR6NLyvitbSjC79DvT8T 가 만들기 전에 결정 하나를 올렸다: 사용자가 올리지 않는다고 판정한 한 번짜리 줄은 목록에서 어떻게 되는가. 선택지는 A `proposed: hold` 로 내리고 `user declined <날짜>` 를 적는다(PM 의 추천), B 목록에서 뺀다, C 이 카드에서는 정하지 않는다. PO 세션이 사용자의 위임("왠만하면 니 추천을 따를 테니까 쭉쭉 진행해라")으로 A 를 골랐다. DE-00000104 가 문턱 아래의 후보를 목록에 두기로 한 것과 같은 방향이다. 사용자가 보고 뒤집을 수 있다.
- 2026-11-26 PM 세션이 카드를 두 조각(색인 코드, 규칙 문서와 브리핑)으로 나눠 전문가 서브에이전트 둘에게 맡긴다고 알렸다. 범위 밖으로 `stage/operations/retrospective.md` 34행을 고친다고 했다.
- 2026-11-26 PM 세션 session_018VXR6NLyvitbSjC79DvT8T 가 e756d4ca 를 보고했다. 성공 기준 다섯을 모두 채웠다고 했다. 카드를 두 조각으로 나눠 `developer`(색인)와 `writer`(문턱 문서와 브리핑)에게 맡기고 검수했다고 했다. 범위 밖으로 `stage/operations/retrospective.md` 의 `promotion:` 한 줄을 고쳤다.
- 2026-11-26 PO 세션이 squash 커밋 8f51c35 에서 훅 시험(491 통과), 스크립트 시험(1039 통과), `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidate: 이 저장소의 클라우드 브리핑에 `proposed: promote` 줄이 한 줄도 실리지 않고 수만 보인다 — evidence: `python3 stage/scripts/subsession_brief.py --project-root . W-00000421 --po-session session_x --role pm --branch b | tail -4` 가 `- …14 candidates not shown — read .stage/state/rule-candidates.md` 를 낸다
- Follow-up candidates: registered 1, discarded 0. PM 세션이 든 둘째 후보(`.stage/state/rule-candidates.md` 의 머리말)는 이미 정해진 다음 카드(지금 목록에 적용)의 일이라 후보로 세지 않았다.

### Executor report at close — 2026-11-26

```
What changed: stage/skills/stage-retrospective/rule-promotion.md: the first test counts a retrospective that states its own second occurrence as seen twice; the second test is "seen once, and a person caught it or it surfaced after merge or release", and what the close reviewer or CI caught is `proposed: hold`, as is a once-seen candidate whose retrospective does not say who caught it and a bullet carrying `user declined <date>`; "What goes in `## Rule candidate`" asks the writer for who caught it and whether it is a second occurrence; the list format puts the basis inside the parentheses after the R-ids and keeps two values; a new block "What happens to a `proposed: promote` line" says seen 2 or more becomes a rule through a card the PO session registers without the user's verdict and seen 1 waits for the user. stage/skills/stage-retrospective/SKILL.md states the two tests the same way. stage/skills/stage-orchestrate/SKILL.md, "The rule-candidates task", `on_its_report`: register a card for each promote line seen twice without asking; show the user only one table of the promote lines seen once and one tally line; register a card for each line the user chooses; a declined line goes to `proposed: hold` with `user declined <date>`. stage/scripts/subsession_brief.py: the rule-candidates brief marks by those tests, writes who caught a once-seen candidate, keeps a `user declined` bullet at hold, and reports the lines seen twice, a table of the lines seen once, and the count of hold lines. stage/hooks/stage_memory_index.py: `rule_candidate_lines` lists only the `proposed: promote` bullets and its status opens with one line `<n> more candidates are proposed: hold and are not listed`; `promote_first` is removed. stage/hooks/stage_context.py: docstring only. stage/hooks/README.md, stage/operations/cloud-execution.md, stage/operations/retrospective.md and stage/docs/BLUEPRINT.md say the same. Tests pin the index lines, the brief's sentences, and the threshold sentences in the documents. stage/CHANGELOG.md has the entry under Unreleased.
Why: The card's five success criteria: the second test names a person's catch or a find after merge or release and excludes the close reviewer and CI; a retrospective that states its own second occurrence counts as seen twice; the session index carries the promote lines and the count of the other candidates; a line seen twice becomes a rule without the user's verdict, a line seen once waits, and the PO skill shows the user only the table and one tally line; a once-seen candidate with no stated catcher is hold.
Decisions made: (1) Decided by the PO session on the user's delegation, asked before building: a once-seen line the user declines goes to `proposed: hold` with `user declined <date>` inside its parentheses, written by the PO session, and the research session keeps it at hold until a second occurrence. (2) Confirmed by the PO session as not decisions: the list keeps two values and `seen <n>` tells an automatic promote line (2 or more) from one that waits for the user (1); a self-stated second occurrence is written `seen 2: <R-id>; <R-id> states its second occurrence`; the basis of a once-seen line is written after the R-id (`caught by a person: ...`, `caught by CI`); the index lists promote lines only and counts the rest on one line. (3) Settled here, one file each: the hold count line sits in the candidates block's fixed tail, so it is never shortened, and is omitted when the count is 0; a bullet with no proposal counts as hold, as before; the PO session commits a `user declined` mark in the chore card that merges the list while that card is open and through a new chore card after it closed; one rule card per promoted line, as the skill already said. (4) Path changed outside the card's scope: stage/operations/retrospective.md — its `promotion:` line said the session proposes and a person chooses, which contradicts DE-00000104; only that key changed. (5) The card was split into two pieces given to specialist sub-agents: `developer` the session index, `writer` the threshold documents and the brief; each diff was read and both suites were re-run here. (6) No record was created.
Work not done: `.stage/state/rule-candidates.md` still carries the old marks and its header still says the user decides every promotion; applying the threshold to it is the next card. How a promoted rule is removed is not stated anywhere. In this repository's brief the 14 promote lines are all shortened away, because the brief plus the index is over 10,000 characters; the hold count line stays. No research session has run under the new brief. `python3 stage/scripts/release_plugin.py stage --check-released` was not run. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Checks run on Linux at this commit: python3 -m unittest discover -s stage/hooks/tests -q (491 tests, OK, skipped=2); python3 -m unittest discover -s stage/scripts/tests -q (1039 tests, OK, skipped=2); python3 stage/scripts/audit_stage.py (errors=0, warnings=32, the same count as before the change); python3 -m unittest discover -s plainly/tests -q (OK).
```

## Verification

2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `8f51c35` 의 것이다.

- Checks at close 2026-11-26: 3 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-26 by claude_review_companion: approved (1 PASS read, 2 PASS read, 3 PASS ran, 4 PASS read, 5 PASS read, 6 PASS read)
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
