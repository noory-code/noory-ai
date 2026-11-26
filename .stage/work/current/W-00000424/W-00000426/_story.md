---
id: W-00000426
title: 규칙: 사용자에게 묻거나 토론할 때는 질문 하나에 답 하나만 두고 큰 그림부터 말한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000426
promotion: not_applicable
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000426 규칙: 사용자에게 묻거나 토론할 때는 질문 하나에 답 하나만 두고 큰 그림부터 말한다

## Purpose

사용자가 한 번에 한 가지를 답하고 큰 그림을 먼저 본다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000371 과 R-00000402 를 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `7e97cf0` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
### Executor report at close — 2026-11-26

```
What changed: stage/operations/output.md, "Rules", gains one bullet for a response that asks the user to choose or decide something, or that is a turn in a discussion with the user: open with the big picture, ask one question that one answer settles and hold the other open questions until it is answered, use at most one table (the one with that question's options), and keep reasons and opposing views out of the question sentence. It says what went wrong both times and cites (R-00000371, R-00000402). stage/CHANGELOG.md has the entry under Unreleased.
Why: The story's success criterion: the rule file states this behavior with its condition and cites R-00000371 and R-00000402. output.md owns the rules for user-visible responses in every project that installs Stage (rule-promotion.md, "Where the rule goes").
Decisions made: (1) Settled by the PM session as a one-file how-detail and reported to the PO session before building: the rule goes to operations/output.md and not to stage-orchestrate, "Talk with the user", because a session that works alone on the device also asks the user. (2) "in one or two sentences" and "what is being decided overall, and where this question sits in it" are this card's wording; R-00000402 says only "short" and "big picture first". (3) The rule does not say where the held questions wait; neither retrospective does. (4) The existing first bullet, "Lead with the conclusion in the first sentence", is unchanged, and the new bullet does not say which of the two opens a question turn; they agree when a question turn has no conclusion yet. (5) The story was written by a `writer` specialist sub-agent; the PM session read the diff against both retrospectives and re-ran the hooks suite. (6) No path outside the story's scope changed. No record was created.
Work not done: No test pins the new sentences. No session has asked the user under the rule. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Check run on Linux at this commit: python3 -m unittest discover -s stage/hooks/tests -q (491 tests, OK, skipped=2).
```

## Verification

2026-11-26 이 스토리는 닫을 때 리뷰를 받지 않았다(`review: not_required`). 닫기 리뷰는 에픽 W-00000424 가 닫힐 때 한 번 돌고, 그때 커밋 `7e97cf0` 의 경로를 본다.

- Checks at close 2026-11-26: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
