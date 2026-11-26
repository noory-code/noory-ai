---
id: W-00000429
title: 규칙: 리뷰어에게 허용하는 규칙을 바꾸면 허용되는 경우와 거절되는 경우를 모두 실제로 실행해 본다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000429
promotion: not_applicable
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000429 규칙: 리뷰어에게 허용하는 규칙을 바꾸면 허용되는 경우와 거절되는 경우를 모두 실제로 실행해 본다

## Purpose

리뷰어의 허용 규칙을 바꾼 카드가 실제 실행으로 양쪽을 확인한 뒤에 닫힌다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000374 를 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `4a09180` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
### Executor report at close — 2026-11-26

```
What changed: stage/operations/review.md, "What the close sees of the reviewer", gains the subsection "A change to what the reviewer may do": when a change touches the allow or deny rules a reviewer command passes to `claude` (in scripts/claude_review_companion.py the `Edit(<verdict file>)` rule, `shell_tools`, `DENIED_COMMANDS`, `denied_rules`, or the `--allowedTools` and `--disallowedTools` lists of `claude_command`, or the same two options in a project's own reviewer command), then before the card closes the real `claude` runs under the new rules on each platform whose rules changed, once on a call they must allow and once on a call they must refuse; the result is read from the stream-json output (`tool_use` blocks and `permission_denials`), both results go on the card's `## Verification`, a platform the session cannot run is a `- Checked` line from that machine, and a unit test of the lists is not enough. It names the two cards and the existing live probe test and cites (R-00000374; first occurrence W-00000359). stage/CHANGELOG.md has the entry under Unreleased.
Why: The story's success criterion: the rule file states this behavior with its condition and cites R-00000374. The reviewer stand-in ships with the plugin, so the rule binds every project (rule-promotion.md, "Where the rule goes"), and review.md owns what the reviewer may do.
Decisions made: (1) Settled by the PM session as a one-file how-detail and reported to the PO session before building: the rule goes to operations/review.md, "What the close sees of the reviewer", not to cloud-execution.md. (2) The story title says "actually run"; the rule keeps the candidate's "real `claude`". (3) `--verbose` is in the named command because claude_command builds it so; R-00000374 names `claude -p --output-format stream-json`. (4) "the same two options in a project's own reviewer command" is by analogy; no retrospective shows a project command going wrong. (5) A platform the session cannot run is mapped to the existing `- Checked` line of "A check recorded on the card"; no retrospective states this for reviewer permissions, and the rule does not say what happens when no such machine exists. (6) The results on the session's own platform have no fixed line form: "both results on the card's `## Verification`, with the command line of each run". (7) R-00000359 is not cited as a source: its own rule candidate is a different one. (8) The story was written by a `writer` specialist sub-agent; the PM session checked every name against claude_review_companion.py and test_claude_review_guard.py, softened "settled only by running" to "checked by running" and one changelog sentence, and re-ran the checks. (9) No path outside the story's scope changed. No record was created.
Work not done: No real `claude` was run for this card; it changes no permission rule. `LiveReviewerWriteProbeTest` was not run (it is skipped without STAGE_LIVE_REVIEW_PROBE=1). No test pins the new sentences. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Checks run on Linux at this commit: python3 -m unittest discover -s stage/hooks/tests -q (491 tests, OK, skipped=2); python3 -m unittest discover -s stage/scripts/tests -p 'test_c*.py' -q (158 tests, OK, skipped=2).
```

## Verification

2026-11-26 이 스토리는 닫을 때 리뷰를 받지 않았다(`review: not_required`). 닫기 리뷰는 에픽 W-00000424 가 닫힐 때 한 번 돌고, 그때 커밋 `4a09180` 의 경로를 본다.

- Checks at close 2026-11-26: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
