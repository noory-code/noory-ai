---
id: W-00000404
title: stage-orchestrate 스킬과 역할별 브리핑을 만든다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000404
promotion: not_applicable
review: passed
scope: stage/skills,stage/scripts,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000404 stage-orchestrate 스킬과 역할별 브리핑을 만든다

## Purpose

새 세션이 stage-orchestrate 스킬로 오케스트레이터가 되고, 작업 세션과 검증 세션은 생성된 브리핑으로 역할을 받는다 (DE-00000099)

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage-orchestrate 스킬이 있고 stage-handoff 의 서브세션 절과 겹치지 않는다
- 작업 세션(에픽)과 검증 세션의 브리핑을 생성할 수 있고 그것을 보이는 시험이 통과한다
- 새 클라우드 세션이 이 스킬로 오케스트레이터 역할을 맡아 진행 중인 카드와 답을 기다리는 확인을 기록과 세션 목록에서 찾아냈다

## Next action

닫고 PR #107 을 머지한다.

## Related truth

## Progress

- 2026-11-22 작업 세션 session_018VXR6SeAeMrUHEGhh8myKi 가 214667e 를 보고했다. 성공 기준 1, 2 를 주장했다.
- 2026-11-22 시험 세션 session_018VXR6RJwybKUJRATYqvEuM 이 스킬만으로 인수인계를 했다. 카드와 확인은 찾았지만 스킬의 빈 곳 열한 가지(A–K)를 보고했다.
- 2026-11-22 작업 세션이 29e2cf9 로 A–K 를 고쳤다(`started_cards.py` 추가). 메인 세션에서 scripts 907, hooks 467 통과.
- 2026-11-22 작업 세션이 159f03c 로 남은 여덟 가지를 고쳤다. 메인 세션에서 scripts 908, hooks 467 통과, PR #107 의 CI 30개 통과.
- 2026-11-22 사용자가 지휘자 교체 규칙을 승인했다("네 이대로 가죠"): 새 지휘자는 사용자가 지명하고, 이전 세션이 답이 없으면 사용자 확인 뒤 새 세션이 그 태그를 뗀다.
- 2026-11-22 사용자가 세션 태그 `stage-project:<owner>/<repository>` 와 `stage-orchestrator` 를 승인했다("네 그대로 쓰죠").
- 2026-11-22 사용자가 검증 세션의 판정과 닫기 리뷰를 둘 다 두고, 하나로 합칠지는 W-00000401 에서 정하기로 했다("네 추천대로 가죠"). 그때까지 검증 세션은 에픽에만 띄우고 스토리는 닫기 리뷰만 받는다.
- Follow-up candidate: `close_work.py` 가 검증 세션의 판정을 받아들이게 한다 (W-00000401 에서 다룬다).
- Follow-up candidate: 토론 세션과 계획 세션의 브리핑을 생성한다.
- Follow-up candidate: 에픽을 닫는 길(스토리별 cherry-pick)을 실제 에픽으로 해 본다.
- Follow-up candidate: 몇 번 쓴 뒤 stage-orchestrate 스킬(235줄)에서 줄일 수 있는 지시를 찾는다.

### Executor report at close — 2026-11-22

```
What changed: Across all three commits: added stage/skills/stage-orchestrate/SKILL.md; replaced stage-handoff's "Hand cards to cloud sub-sessions" section with a pointer; subsession_brief.py gained --role work|verify and --commit (epic work brief with one commit and one executor report per story, verify brief with a PASS/FAIL verdict per criterion and no changes) and forbids a work session from editing the card's Progress and Next action; new stage/scripts/started_cards.py lists the cards in progress across HEAD, the default branch, and unmerged fetched branches, minus cards the default branch archived, names the copy edited last, and lists what waits in the records; start_work.py reads other branches and lifecycle roots through that module; stage-drive states its boundary with the orchestrator. In this commit: started_cards.py prints `Project tag: stage-project:<owner>/<name>` derived from the remote's URL (the project folder name without a remote) and prints a `Waiting on user:` line only under "Waiting in the records"; the skill uses `<project-tag>` copied from that line, keeps a row whose id is named by a kept row's stage-main-session tag and treats it as the earlier orchestrator, names the session-list row shape (archived is session_status SESSION_STATUS_ARCHIVED, untagged rows have no tags key, page until a page returns fewer than 100 rows), reads list_events with limit 20 and pages back at most five pages when a page holds no assistant event, says sessions outside the project stay out of the list even when they wait on the user, records follow-up candidates as `Follow-up candidate:` lines under Progress, and adds "One conductor at a time"; tests and CHANGELOG updated.
Why: W-00000404 asks that a new session become the orchestrator through the skill and find the cards in progress and the waiting confirmations from the records and the session list; the main session's two trials showed where the skill still needed improvisation.
Decisions made: Kept the script name subsession_brief.py and the default role so existing callers do not change; a work session's unit is one top-level card, replacing DE-00000094's split_when rule with DE-00000099's start-up cost rule; the verify session reports a message and writes no verdict file, so close_work.py still runs its configured close review (whether the verdict replaces it is the user's pending choice); in progress means started on HEAD, the default branch, or an unmerged fetched branch and not archived on the default branch, because a squash-merged branch reads as unmerged; the copy to read is the one whose record has the newest commit, because only the orchestrator edits a card after its start; the orchestrator, not the work session, writes Progress and Next action when a report arrives, with the fixed prefix `Waiting on user:`; the tags stage-project and stage-orchestrator are a new convention awaiting the user's confirmation; the project tag is derived by the script from the remote URL's last two path segments so one source spells it; the conductor is the single session tagged stage-orchestrator, the user names a new conductor by asking a session to take over, the new session changes nothing until the tag moves, the earlier orchestrator writes its records and removes its own tag when it answers, and when it is archived or silent the new session removes that tag only after the user confirms, because two sessions closing cards at once is the failure to avoid and an unanswered hand-over must not block the user; follow-up candidates go under Progress with a fixed prefix because close already copies the executor report there and Next action stays one step; start_work.py lost its own git reading in favor of started_cards.py (SSOT); the skill is 235 lines because the session-list rules, record keeping, and the conductor rule are new content; changed outside the card scope: stage/operations/cloud-execution.md (its pointer named the removed stage-handoff section, and it now says how to bring an epic's per-story commits over) and stage/README.md (the entry-skill list names the new skill).
Work not done: The third version of the take-over was not re-tried by a fresh session, which is the main session's to start; the session-list row shape and the list_events limit behavior are taken from the main session's trial reports and were not observed here; set_session_tags on another session's row (removing an earlier orchestrator's tag) was not tried; the epic close path (cherry-pick per story) is documented and untried; Windows runs of the suites are left to the pull request's Windows CI; no record ids were created.
```

## Verification

- 2026-11-22 메인 세션에서 작업 세션의 세 커밋을 합친 트리로 `python3 -m unittest discover -s stage/scripts/tests -q` 를 돌렸다: 908 통과(건너뜀 2). `python3 -m unittest discover -s stage/hooks/tests -q`: 467 통과(건너뜀 2). `audit_stage.py`: errors=0.
- 기준 1: `stage/skills/stage-orchestrate/SKILL.md` 가 있고, `stage-handoff` 의 서브세션 절은 그 스킬을 가리키는 한 문단으로 바뀌었다. `test_orchestrate_skill.py` 가 겹치지 않음을 본다.
- 기준 2: `subsession_brief.py --role work`(에픽) 와 `--role verify` 가 브리핑을 내고 `test_subsession_brief.py` 가 통과한다.
- 기준 3: 새 클라우드 세션 session_018VXR6RJwybKUJRATYqvEuM 이 3637dfdc 에서 스킬만 따라 `started_cards.py` 한 번으로 진행 중 카드 W-00000404 와 카드에 적힌 `Waiting on user:` 두 줄을 찾았고, 세션 목록에서 답을 기다리는 작업 세션을 찾았다. 그 시험이 찾은 여덟 가지는 159f03c 에서 고쳤고, 그 판은 새 세션이 다시 해 보지 않았다.
- PR #107 의 CI 30개(Windows 포함)가 9a106f93 에서 통과했다.

- Checks at close 2026-11-22: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
