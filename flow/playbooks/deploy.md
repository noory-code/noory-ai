---
name: deploy
description: Deploy / infrastructure-change work type — write the runbook and rollback path first → change plan (plan) → approval (review) → progressive rollout (apply) → observe & verify → expand or roll back
---

# deploy (deploy / infrastructure)

A work type that ships a deploy target to a production environment or changes infrastructure. **It does not build code features themselves** — it is the flow of safely applying artifacts that are already built. The core is the **stage separation of plan → review → apply** and **progressive rollout** (partial exposure → observe → expand/roll back), and every apply happens only on top of a **runbook and rollback path prepared in advance**.

## Applies to

- Work that ships a deploy target (build artifacts / releases) to a production/staging environment
- Infrastructure configuration changes (capacity, network, config values, schema application, and other changes that alter the operational state)
- Risky applies that need a progressive-exposure / rollback path
- Not a fit: developing code features themselves (→ `feature`) / fixing defects (→ `bug`) / structural improvement preserving existing behavior (→ `refactor`) / producing documents & specs (→ `docs`)

## Procedure

1. **Write the runbook & rollback path first** — document the apply procedure, verification items, and the path to revert on failure first. If rollback is impossible, make it possible or halt the apply / Artifact: runbook document (apply stages + rollback procedure + observation-metric list)
2. **Change plan (plan)** — work out what changes how, and the impact scope / blast radius. State the difference between the current state and the target state / Artifact: change plan (change diff, impact scope, progressive-stage definition)
3. **Plan review & approval (review)** — review the plan and rollback path and get approval. Agree on risk and impact scope / Artifact: approval record (reviewer, approval decision, conditions)
4. **Progressive rollout (apply)** — apply the approved plan starting from partial exposure (small target → stage expansion). Applying everything at once is prohibited / Artifact: apply log (apply stage, target scope, timestamp)
5. **Observe & verify** — after each stage, check the observation metrics and compare against the normal baseline. Detect anomaly signals / Artifact: observation result (metric values + whether the normal baseline is met)
6. **Expand or roll back** — if observation is normal, expand to the next stage (return to ④); if anomalous, execute the runbook's rollback path / Artifact: expansion decision or rollback execution record

> The concrete deploy mechanism (progressive-exposure method, observation-metric definitions, rollback commands) and the platform/tool-specific apply procedures are delegated to the analysis procedures **supplied by the project** (project `.claude/agents/`). This playbook defines only the general deploy flow.
>
> **④⑤⑥ is a loop repeated at every progressive stage.** Partial exposure → observe → judge (expand/roll back) → next partial exposure. Full expansion is reached only when every stage's observation is normal.

## AC format

Write the success condition of each deploy stage in 5 fields.

- **Given** — precondition (state right before apply / exposure scope / runbook ready)
- **When** — action (apply this stage / expand exposure)
- **Then** — expected result (observation metrics within the normal baseline / target operates normally)
- **Verification method** — check observation metrics (automated monitoring or an observation procedure) + compare against the normal baseline
- **Pass/fail criteria** — normal baseline met = expand / baseline exceeded or anomaly signal = roll back

> No unmeasurable "it works / looks fine" AC. Fix observation metrics and the normal baseline as numbers or clear qualitative statements.

Example (domain-agnostic — partial-exposure stage):

- **Given** — runbook & rollback path ready, exposure scope = a portion of the whole (small scale)
- **When** — apply the change to that portion
- **Then** — the key observation metrics stay within the normal range versus the pre-apply baseline
- **Verification method** — after apply, collect and compare the observation metrics over a set observation window
- **Pass/fail criteria** — stays within normal range = PASS (expand to next stage) / baseline exceeded = FAIL (execute rollback)

## Hard Gate

> **HARD GATE**: no apply without a runbook & rollback path
> On failure: procedure ④ (progressive rollout) is blocked — procedure ① (runbook & rollback path) is a required prerequisite
> Bypass: only on explicit user expression (skip / move on / bypass / skip it)

> **HARD GATE**: no apply without plan review approval
> On failure: procedure ④ (progressive rollout) is blocked — procedure ③ (plan review & approval) is a required prerequisite
> Bypass: only on explicit user expression (skip / move on / bypass / skip it)

> **HARD GATE**: no full expansion while observation metrics are unconfirmed
> On failure: procedure ⑥ (expand) is blocked — procedure ⑤ (observe & verify) must confirm the previous stage is normal. On an anomaly signal, roll back instead of expanding
> Bypass: only on explicit user expression (skip / move on / bypass / skip it)

## Feedback-loop location

The "verify → feedback → fix → re-verify" loop of this playbook:

1. **Procedures ④⑤⑥ (progressive rollout → observe → expand/roll back)** — the core loop. Partial exposure (apply) → collect observation metrics (verify) → anomaly analysis (feedback) → expand or roll back (judge). Repeated at every progressive stage until full expansion or rollback completes
2. **Procedure ③ (plan review & approval)** — an early feedback loop before apply (blocks plan/rollback-path defects before apply)

> The above loops are verification loops **within the work flow**. Improving the playbook itself ("is this deploy flow correct") is the responsibility of retrospective-driven evolution (the `retro-processing` work type) — outside this playbook's scope.

## Review & evaluation points

- **Review**: procedure ③ (review & approve the plan / rollback path). Prioritize risk, blast radius, and rollback feasibility. Delegate when the project supplies a review teammate. **RT runs default-on** (strength & independence = README §7 + the RT strength matrix). RT essence attack: rollback path, blast radius, observation sufficiency.
- **Evaluation**: procedure ⑤, observation metrics ↔ normal baseline comparison = the evaluation criterion for each stage's artifact. Every progressive stage's observation normal = deploy satisfied. An anomaly during a stage = roll back.
- `flow-procedure-story` §7-2 review & evaluation Hard Gate forces execution of the above points.

## Handling violations

- apply without a runbook & rollback path / apply without approval / full expansion without observation = block or request remediation
- An artifact where apply was forced through without a rollback path = treated as invalid, prioritize returning to a safe state
- Bypass is allowed only on explicit user expression (skip / move on / bypass / skip it)
- The fact of a bypass = mandatory record in the retrospective Problem section
