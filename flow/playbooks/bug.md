---
name: bug
description: Bug-fix task type — reproduce → failing test (pin the cause) → fix → regression verification. Reproduce·regression mandatory regardless of scale
---

# bug (bug fix)

A task type for fixing defects. **Pin the cause by reproducing**, then embed that reproduction as a failing test, fix it, and prevent recurrence via regression. Even small bugs are not exempt from the reproduce·regression gates (regardless of scale).

## Applies to

- Work that corrects behavior that differs from expectation (a defect)
- A reproducible error / a fix that needs regression prevention
- Not a fit: adding new behavior (→ `feature`) / behavior-preserving structural improvement (→ `refactor`)

## Procedure

1. **Reproduce** — find the minimal conditions·input that cause the defect and reproduce it consistently / output: reproduction procedure (input + expected vs actual)
2. **Root-cause analysis** — trace the root cause from the reproduction (cause, not symptom) / output: cause note
3. **Write a failing test (Red)** — write a test that exposes the defect. It fails (Red) before the fix / output: failing reproduction test
4. **Fix + verify** — the minimal fix that makes the test pass → pass (Green) / output: fix code + reproduction test passing
5. **Regression verification** — rerun all related existing tests (confirm the fix does not break other behavior) / output: full regression test pass
6. **PR** — reproduction procedure + cause + fix + test results + review / output: Pull Request

> Concrete debugging tools·log analysis·language-specific tests are delegated to procedures **supplied by the project**. This playbook defines only the general defect-fix flow.

## AC format

Specify each defect with 5 fields.

- **Given** — the precondition to reproduce the defect (input / state)
- **When** — the action that triggers the defect
- **Then** — the expected result after the fix (defect resolved)
- **Verification method** — reproduction test (fails before the fix → passes after) + regression test
- **Success·failure criteria** — reproduction test passes + full regression passes = PASS / reproduction test fails or regression breaks = FAIL

> No unmeasurable AC like "works fine / looks okay."

Example (domain-agnostic — a sum error):

- **Given** — a specific input set (including boundary values)
- **When** — computing the sum
- **Then** — the correct sum (existing error resolved)
- **Verification method** — a test that failed on that input passes after the fix + the existing sum tests pass in regression
- **Success·failure criteria** — reproduction test + regression both PASS / any one FAIL

## Hard Gate

> **HARD GATE**: no starting the fix without reproduction (procedure ①)
> If unmet: procedure ④ (fix) is blocked — an unreproduced defect has an unknown cause, so a fix is guesswork. Reproduction must come first
> Bypass: only on an explicit user expression (skip / move on / bypass / skip over)

> **HARD GATE**: no finishing·PR without a regression test (procedure ⑤)
> If unmet: procedure ⑥ is blocked — the failing reproduction test (③) + the related regression tests must all pass
> Bypass: only on an explicit user expression

## Feedback-loop locations

1. **Procedure ④ (fix + verify)** — the core loop. Run the reproduction test (verify) → analyze failure (feedback) → fix → rerun
2. **Procedure ① (reproduce)** — the reproduction-condition-narrowing loop (re-explore conditions if reproduction fails)
3. **Procedure ⑥ (PR)** — reviewer feedback → fix → re-review

> These are verification loops within the work flow. Improving the playbook itself is the responsibility of retrospective-based evolution (`retro-processing`) (out of scope).

## Review·evaluation points

- **Review**: procedure ⑥ (PR review — check cause accuracy / fix scope / regression risk). Delegated when the project supplies a review teammate. **RT runs default-on** (intensity·independence = README §7 + the RT-intensity matrix). RT essence attacks: cause accuracy·regression risk·reproduction sufficiency.
- **Evaluation**: reproduction test (fails before the fix → passes after) + full regression pass = the output-evaluation criterion.
- `flow-procedure-story` §7-2 review·evaluation Hard Gate enforces execution of the points above.

## Violation handling

- A fix without reproduction / a finish without regression = blocked or sent back for completion
- A bypass is allowed only on an explicit user expression + is obligated to be recorded in the retrospective's Problem section
</content>
