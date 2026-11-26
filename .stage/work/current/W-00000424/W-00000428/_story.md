---
id: W-00000428
title: 규칙: 숫자에서 개선 제안을 낼 때 그 자리를 지금 모양으로 만든 커밋이나 주석을 먼저 읽는다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000428
promotion: not_applicable
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000428 규칙: 숫자에서 개선 제안을 낼 때 그 자리를 지금 모양으로 만든 커밋이나 주석을 먼저 읽는다

## Purpose

숫자만 보고 낸 개선 제안이 이미 이유가 있어 그렇게 된 자리를 되돌리지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000334 를 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `9641222` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
### Executor report at close — 2026-11-26

```
What changed: stage/skills/stage-work/SKILL.md, "Run the premise before turning an observation into a card", gains one paragraph before its closing paragraph: when a proposal comes from a number (a size, a count, a duration, a cost, a limit that looks missing, too high, or too low), read how the place got its present shape before proposing it to the user, as a card, or as a follow-up candidate — `git blame <path>` and `git log -L <start>,<end>:<path>` on the measured lines, the commit messages, the comment beside the code, and the decision record or card those commits name; when one of them states a reason, the proposal says what has changed since, or it is withdrawn. It tells the two cases and cites (R-00000334). stage/CHANGELOG.md has the entry under Unreleased.
Why: The story's success criterion: the rule file states this behavior with its condition and cites R-00000334. R-00000334 itself says the lesson is close to this existing stage-work rule and that adding "a proposal from a measurement" to it fits better than a new rule (rule-promotion.md, "Amending beats appending").
Decisions made: (1) Settled by the PM session as a one-file how-detail and reported to the PO session before building: the existing stage-work section is amended; no new section and no operations/ file. (2) "the decision record or card those commits name", "as a follow-up candidate", and the list "a size, a count, a duration, a cost, a limit" go beyond the candidate's "commit or comment"; the retrospective's one case is a size that led to a count cap. (3) The W-00000333 sentence is kept because R-00000334 names it as the earlier occurrence, although R-00000333 describes a criterion written before checking where the plugin is read, not a number. (4) The rule does not say what to do when the history states no reason; the proposal then goes ahead. (5) The story was written by a `writer` specialist sub-agent; the PM session read the diff against R-00000334 and re-ran the check. (6) No path outside the story's scope changed. No record was created.
Work not done: Commit db9f74f1 and the figure "6 of 17" are taken from R-00000334; this shallow checkout cannot resolve that commit. No test pins the new sentences. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Check run on Linux at this commit: python3 -m unittest discover -s stage/scripts/tests -p 'test_register_work.py' -q (48 tests, OK).
```

## Verification

2026-11-26 이 스토리는 닫을 때 리뷰를 받지 않았다(`review: not_required`). 닫기 리뷰는 에픽 W-00000424 가 닫힐 때 한 번 돌고, 그때 커밋 `9641222` 의 경로를 본다.

- Checks at close 2026-11-26: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
