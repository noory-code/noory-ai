---
id: W-00000418
title: 기계에서만 보이는 성공 기준을 카드에 기록된 확인으로 닫기 리뷰가 판정하게 한다
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
retrospective_ref: R-00000418
promotion: not_applicable
review: passed
scope: stage/operations/review.md,stage/operations/cloud-execution.md,stage/templates/v4/project-stage/settings.jsonc,.stage/settings.json,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000418 기계에서만 보이는 성공 기준을 카드에 기록된 확인으로 닫기 리뷰가 판정하게 한다

## Purpose

사용자의 기계에서만 보이는 성공 기준을 가진 카드가, 그 확인이 카드에 기록된 뒤에는 닫기 리뷰를 통과해 닫힐 수 있다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰 규칙이 카드의 ## Verification 에 날짜·기계·명령·결과가 적힌 기기 확인이나 사용자 판정을 read 로 판정하게 허용한다
- 그런 기록이 없는 기계 전용 기준은 지금처럼 FAIL 이다
- W-00000407 이 이 규칙으로 닫기 리뷰를 다시 받는다

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6RqorVPW78Q1Ns72B6 — work — 2026-11-24 — opened from the index: O-00000062

## Progress

- 2026-11-24 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. W-00000407 의 닫기 리뷰가 두 기준을 `unable` 로 반려한 것이 계기다. `stage/operations/review.md` 는 검증 세션의 관찰만 `read` 로 판정하게 하고, `cloud-execution.md` 의 "Merge a card that waits for the user's machine" 은 확인이 도착하면 닫기 리뷰가 모든 기준을 판정한다고 해서, 기계 전용 기준을 가진 카드는 닫히지 않는다. 사용자가 절차를 고치는 길을 골랐고("1"), 목적과 성공 기준은 지휘 세션의 초안을 사용자가 그대로 승인했다("초안대로 등록").
- 닫기 절차를 바꾸는 카드다. DE-00000087 에 따라 사용자 확인 뒤에 닫는다.
- 셋째 기준(W-00000407 의 재리뷰)은 지휘 세션이 이 카드의 변경을 받은 뒤에 한다. 작업 세션은 하지 않는다.
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-24 작업 세션 session_018VXR6RqorVPW78Q1Ns72B6 가 2f467bf5 를 보고했다. 첫째와 둘째 성공 기준을 채웠다고 했다. `review.md` 에 "A check recorded on the card" 를 더했고, 리뷰 명령 여섯 개와 템플릿, `cloud-execution.md`, 작업 브리핑이 따라간다. 줄의 형식은 `- Checked` 와 `- User verdict` 둘로 고정했다. `- Checked ... did not hold` 뒤의 `- User verdict ... held` 는 사용자의 판정이 정한다. 범위 밖으로 `stage/skills/stage-orchestrate/SKILL.md` 를 고쳤다(사용자의 답을 `- User verdict` 줄로 적으라는 문장). 실제 리뷰어가 새 문장을 따르는지는 돌려 보지 않았다고 했다.
- 2026-11-24 지휘 세션이 squash 커밋 0dab111 에서 훅 시험(489 통과), 스크립트 시험(1025 통과), `audit_stage.py`(오류 0)를 다시 돌렸다.
- 2026-11-24 지휘 세션이 W-00000407 의 확인을 새 줄 형식으로 옮기고 그 카드의 닫기 리뷰를 다시 돌린다(셋째 기준).
- Follow-up candidate: `read` 로 통과한 기계 전용 기준 뒤에 `- Checked`/`- User verdict` 줄이 있는지 `close_work.py` 나 audit 가 본다. 또는 기록된 확인과 기록의 사실을 가르는 표시를 둔다.
- Follow-up candidate: 다른 프로젝트(Dasina 등)는 리뷰 명령에 새 문장 넷을 넣어야 한다. 빠져도 audit 가 알리지 않는다(REVIEW003 은 method 낱말만 본다).
- Follow-up candidate: `claude_review_companion.py` 의 REVIEWER_RULES 가 기록된 확인의 예외를 말하게 한다.
- Follow-up candidate: `.stage/operations/verification.md` 의 "Windows 동작 확인" 이 `- Checked` 형식을 가리키게 한다.
- 2026-11-24 지휘 세션이 W-00000407 의 닫기 리뷰를 이 카드의 규칙으로 다시 돌렸다(셋째 기준). 첫 리뷰는 두 기준을 `unable` 로 반려했고, 확인을 `- Checked` 와 `- User verdict` 줄로 옮긴 뒤의 리뷰는 두 기준을 `read` 로 통과시켰다. 리뷰어는 판정 이유에 줄의 종류와 날짜를 적고 자기가 확인을 돌리지 않았다고 적었다. W-00000407 은 닫혀 보관됐다.
- 2026-11-24 사용자가 이 카드를 닫으라고 했다("닫으세요", DE-00000087 의 확인). 지휘 세션은 그 전에 사용자의 판정이 실패한 확인을 덮는다는 것과, 리뷰어가 아무도 돌리지 않은 확인의 줄을 가려내지 못한다는 것을 알렸다.

### Executor report at close — 2026-11-24

```
What changed: stage/operations/review.md: "How the reviewer judges" gains one rule that sends a criterion only a whole session, the user's machine, or the user can show to a new section, "A check recorded on the card". That section names three lines on the card's ## Verification (the verification session's existing `- Observed` line, a new `- Checked <date> on <machine> at <commit>: <criterion> — <held|did not hold>; <command or action> — <what it showed>` line, and a new `- User verdict <date>: <criterion> — <held|did not hold>; "<the user's words>"; rests on <...>` line), who writes each, what each part must hold, what is not a record, and the reviewer's rules: no line is `unable` and FAIL as before; a line that lacks a part, names a commit that does not hold the card's change, or says `did not hold` is FAIL with method `read`; a complete line that says `held` is PASS with method `read`; a later `- User verdict ... held` line decides over an earlier `- Checked ... did not hold` line; the reason names the line and says the reviewer did not run the check. It replaces the one paragraph that covered the verification session only, and says what the rule does not give. The six review commands in .stage/settings.json and the `review` comment of stage/templates/v4/project-stage/settings.jsonc gain four sentences after "a criterion with method unable is always FAIL." that state the exception and that a criterion without a line stays `unable`. stage/operations/cloud-execution.md: "Close a sub-session's card" step 4 checks for the line before the close; "Merge a card that waits for the user's machine" applies only while the check is not recorded, writes the arriving check as `- Checked` (and `- User verdict` when the user says how to judge a check that does not match the criterion's words), and says how the first close review judges. stage/scripts/subsession_brief.py: the work brief tells the building session not to write a `- Checked` or `- User verdict` line. Tests: test_template_v4.py pins the four sentences in all six commands and the template; test_orchestrate_skill.py pins the section's line forms and its PASS and FAIL rules and the pointers to it; test_subsession_brief.py pins the brief line. stage/CHANGELOG.md has the entry under Unreleased.
Why: The card's first two success criteria: the review rule lets a device check or a user verdict written on the card's ## Verification with its date, machine, command, and result be judged with `read`, and a machine-only criterion without such a record is FAIL as now. The review prompts told the reviewer that an observed behavior needs `ran` and that evidence it did not see itself is FAIL, so changing review.md alone would have left the reviewer rejecting the criterion.
Decisions made: (1) Two fixed line forms instead of accepting any prose under ## Verification, so the reviewer's rule has an explicit condition. Consequence: W-00000407's checks are recorded as prose paragraphs and do not match; the main session has to write them as `- Checked` and `- User verdict` lines before the re-review (third criterion, which this session did not do). (2) A `- User verdict ... held` line passes a criterion although an earlier `- Checked` line says `did not hold`. W-00000407's first criterion is that case: the command as written stopped on ARM64 Windows and the user judged the criterion met from the x86_64 run. The other choice is that only a check that holds can pass; then that card cannot close without a new machine. (3) Method stays `read`, as the card's criterion says; no fourth method was added, so the card's review line and work_load.py cannot tell a recorded check from a fact of the records. review.md says so. (4) The verification session's `- Observed` line is judged under the same section and named in the same prompt sentence, because the prompts had no exception for it either and the old paragraph was its only rule; the line's form stays owned by the stage-orchestrate skill. (5) The reviewer compares the commit a `- Checked` line names with the card's code commit (`git merge-base --is-ancestor`, or an empty `git diff` over the changed paths). (6) The building session is told not to write the lines; nothing enforces it, and the reviewer cannot tell a line for a check nobody ran. (7) The prompt sentences say "a machine of the user" and "the words of the user" because test_project_review_commands_use_no_shell_specific_syntax forbids a single quote in a review command. (8) Paths changed outside the card's scope: stage/skills/stage-orchestrate/SKILL.md — its rule "a criterion could not be observed: ask the user how to judge it" had no place to put the answer where the reviewer reads it; it now says to write a `- User verdict` line and points to review.md. (9) No record was created. stage/scripts/claude_review_companion.py REVIEWER_RULES was not changed.
Work not done: The third success criterion (W-00000407's close review under this rule) belongs to the main session. No real reviewer was run against a card with a `- Checked` line, so whether a reviewer follows the new sentences is not observed; only their presence in the commands is tested. close_work.py does not check that a `read` PASS on such a criterion has a line behind it. Other projects' review commands (for example Dasina) do not have the new sentences until someone adds them; they keep failing such criteria as `unable`. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. `python3 stage/scripts/release_plugin.py stage --check-released` could not run: the checkout is shallow. Checks run on Linux: python3 -m unittest discover -s stage/hooks/tests -q (489 tests, OK, skipped=2); python3 -m unittest discover -s stage/scripts/tests -q (1025 tests, OK, skipped=2); python3 stage/scripts/audit_stage.py (errors=0, warnings=32, the same count as before the change).
```

## Verification

2026-11-24 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `0dab111` 의 것이다.

- Checks at close 2026-11-24: 3 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-24 by claude_review_companion: approved (1 PASS read, 2 PASS read, 3 PASS read)
- Load at close 2026-11-24: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
