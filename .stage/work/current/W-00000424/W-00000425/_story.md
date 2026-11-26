---
id: W-00000425
title: 규칙: 기록의 자리나 배치를 바꾸는 변경은 그 자리를 읽는 코드와 화면의 테스트부터 센다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000425
promotion: not_applicable
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000425 규칙: 기록의 자리나 배치를 바꾸는 변경은 그 자리를 읽는 코드와 화면의 테스트부터 센다

## Purpose

기록의 자리를 옮기는 세션이 그 자리를 읽는 코드와 화면의 테스트를 먼저 센다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000241 과 R-00000373 을 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `2b4bca6` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
### Executor report at close — 2026-11-26

```
What changed: stage/skills/stage-work/SKILL.md, "Count affected places before drafting", gains one rule after the four-check paragraph: when a record file is stored at another path, folder, or file name, or a section heading or frontmatter field of a record is added, removed, renamed, or split, then before the four checks search the repository for the path, heading and field name, list and count every piece of code that reads or writes that place and every test of a screen that shows the record, and rewrite those tests for the new place in the same change. It says what happened in the two source cards and cites (R-00000241, R-00000373). stage/CHANGELOG.md has the entry under Unreleased.
Why: The story's success criterion: the rule file states this behavior with its condition and cites R-00000241 and R-00000373. rule-promotion.md, "Where the rule goes", sends a rule that binds every project to the plugin's operations/ or the skill that owns the step; counting affected places is a step of stage-work.
Decisions made: (1) Settled by the PM session as a one-file how-detail and reported to the PO session before building: the rule amends stage-work, "Count affected places before drafting", and not the six-kind table of stage-decision, because a card that moves a record without a decision reads stage-work at registration; the new text points to the stage-decision section and does not repeat its table. (2) The condition names frontmatter fields and "removed, renamed", which neither retrospective shows; they are direct readings of "the place of a record". "Reordered" was left out. (3) The action says "reads or writes", because the driver place in R-00000241 writes machine retrospectives. (4) The list of screens (session-start text, session index, derived views, audit output, unattended driver) is wider than the two the retrospectives show. (5) The story was written by a `writer` specialist sub-agent; the PM session read the diff against both retrospectives and re-ran the checks. (6) No path outside the story's scope changed. No record was created.
Work not done: No test pins the new sentences. No session has followed the rule on a real card. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Checks run on Linux at this commit: python3 -m unittest discover -s stage/scripts/tests -q; python3 -m unittest discover -s stage/hooks/tests -q; python3 stage/scripts/audit_stage.py --project-root . (results in the PM session's report).
```

## Verification

2026-11-26 이 스토리는 닫을 때 리뷰를 받지 않았다(`review: not_required`). 닫기 리뷰는 에픽 W-00000424 가 닫힐 때 한 번 돌고, 그때 커밋 `2b4bca6` 의 경로를 본다.

- Checks at close 2026-11-26: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
