---
id: W-00000419
title: 후속 작업 후보는 지금 깨져 있거나 열린 마일스톤의 완료 기준 한 줄을 지목할 때만 카드가 된다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000419
promotion: deferred
review: passed
scope: stage/skills/stage-orchestrate/SKILL.md,stage/scripts/subsession_brief.py,stage/operations/before.md,stage/operations/after.md,stage/operations/cloud-execution.md,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs: DE-00000102
---

# W-00000419 후속 작업 후보는 지금 깨져 있거나 열린 마일스톤의 완료 기준 한 줄을 지목할 때만 카드가 된다

## Purpose

카드를 닫을 때마다 나오는 후속 작업 후보 가운데 문턱을 넘은 것만 카드가 되고 나머지는 기록 없이 버려져서, 일감이 끝없이 생기지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 작업 브리핑이 후속 후보마다 재현 명령이나 열린 마일스톤의 완료 기준 한 줄을 붙이라고 한다
- 지휘 스킬이 그 증거가 있는 후보만 등록하고 나머지는 기록하지 않는다
- 카드를 닫을 때 등록 몇, 버림 몇 한 줄이 적힌다
- before.md, after.md, 지휘 스킬이 같은 조건을 말한다

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6QrDdz3LAVPpMYGmyK — work — 2026-11-25 — opened from the index: DE-00000102, M-00000006

## Progress

- 2026-11-25 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 사용자가 토론 세션 session_018VXR6SH4PsfzwA6PTiZW3a 에서 문턱을 정했고 DE-00000102 에 적었다. 성공 기준 네 줄은 토론 세션의 초안이고 사용자가 그대로 받았다("추천대로 해주세요"). 고칠 자리는 DE-00000102 의 "Where this applies" 에 있다.
- 범위 밖: 규칙 후보의 문턱(아직 정해지지 않았다), 버린 후보의 목록(사용자가 고르지 않았다).
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-25 작업 세션 session_018VXR6QrDdz3LAVPpMYGmyK 가 4ad0af16 을 보고했다. 성공 기준 넷을 모두 채웠다고 했다. 조건의 주인은 `operations/before.md` 의 "Follow-up candidates" 다. 범위 밖으로 `stage/scripts/started_cards.py` 의 설명 한 줄을 고쳤다. 작업 세션은 사용자가 그 세션에서 두 확인(버린 수를 적는 줄, 인용한 줄을 찾아보지 않는 것)에 "추천대로"라고 답했다고 전했다.
- 2026-11-25 지휘 세션이 squash 커밋 3a9b852 에서 훅 시험(489 통과)과 스크립트 시험(1027 통과)을 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0

### Executor report at close — 2026-11-25

```
What changed: stage/operations/before.md gains the section "Follow-up candidates", which owns the conditions: a candidate becomes a card when it is broken now and carries the reproducing command with its output, or when it quotes one line of an open milestone's `## Completion criteria` with the milestone id; one with neither is discarded and recorded nowhere; whoever names the candidate attaches the evidence; the registering session checks only that it is there and does not ask the user for a purpose; the closing card's `## Progress` gets `Follow-up candidates: registered <n>, discarded <m>`. stage/operations/after.md step 6 states the same two conditions and the tally line instead of routing follow-up plans to `proposals/` or `work/planned/`. stage/skills/stage-orchestrate/SKILL.md: "Keep the records current" writes `Follow-up candidate: <text> — evidence: <...>` only for a candidate with evidence and `Follow-up candidates discarded: <n>` for the others; "Organize work" registers such a candidate without asking the user for a purpose; "Close and merge" registers the lines and writes the tally before `close_work.py`; "Take over from the records" no longer says candidates live in open observations. stage/operations/cloud-execution.md, "Close a sub-session's card", checks for the tally line before closing. stage/scripts/subsession_brief.py: the work brief's report item asks for the evidence with each candidate. stage/scripts/started_cards.py: docstring only. Tests pin the two conditions in before.md, after.md, the skill, and the brief, the pointer to before.md, and the tally line. stage/CHANGELOG.md has the entry under Unreleased.
Why: The card's four success criteria: the work brief asks for a reproducing command or a completion-criteria line with each candidate; the orchestrate skill registers only candidates with that evidence and does not record the rest; a `registered <n>, discarded <m>` line is written at close; before.md, after.md, and the skill state the same condition.
Decisions made: (1) before.md owns the conditions; after.md, the skill, and cloud-execution.md state them in one sentence and point there. (2) The discard count is kept between a session report and the close as a `Follow-up candidates discarded: <n>` line on `## Progress`, a count without text; without it the close could not sum what was discarded earlier. (3) The orchestrator does not ask a session to add evidence it did not send, and does not run the reproducing command or look the quoted line up; DE-00000102 says the judge only checks that evidence is there. (4) The tally line is written by the orchestrator by hand before `close_work.py`; no script writes or checks it, and it is written when both numbers are 0. (5) A candidate the orchestrator or the close review names at close passes the same test. (6) before.md says a user request still makes a card by itself, and that a broken `.stage/` record is fixed directly without a card, as DE-00000102 did for verification.md. (7) The verify brief was not changed; it has no follow-up item. (8) Path changed outside the card's scope: stage/scripts/started_cards.py — its docstring said open observations are listed because follow-up candidates live there; DE-00000102, "Where this applies", names that line. Only the docstring changed. (9) No record was created.
Work not done: No session has yet reported under the new brief and no card has been closed with the tally line, so whether sessions attach evidence and the orchestrator discards is not observed; the tests pin the text only. DE-00000093's "wrong if" sentence was not edited; DE-00000102 already says how to read it. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Checks run on Linux: python3 -m unittest discover -s stage/scripts/tests -q (1027 tests, OK, skipped=2); python3 -m unittest discover -s stage/hooks/tests -q (489 tests, OK, skipped=2); python3 stage/scripts/audit_stage.py (errors=0, warnings=32).
```

## Verification

2026-11-25 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `3a9b852` 의 것이다.

- Checks at close 2026-11-25: 3 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-25 by claude_review_companion: approved (1 PASS ran, 2 PASS read, 3 PASS read, 4 PASS ran)
- Load at close 2026-11-25: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
