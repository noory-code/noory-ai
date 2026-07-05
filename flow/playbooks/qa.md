---
name: qa
description: Quality-verification work type — risk-based test allocation → run exploratory test charters (goal/scope/time) → record defects → pass/fail decision. The core is risk-based verification allocation, not writing unit tests (→ feature)
---

# qa (quality verification)

A work type that verifies an already-implemented target from the perspective of **is it shippable**. It **allocates verification effort first to high-risk areas** (risk-based) and fills the gaps that automated tests do not reach with **exploratory test charters** (goal/scope/time box). It does not verify every area equally — it allocates by risk weighting.

## Applies to

- Pre-release quality verification of implementation-complete features and release candidates
- Focused verification of areas with high regression risk, integration points, and user impact
- Exploring, per-person or per-session, the gaps that automated tests alone cannot catch
- Not suitable:
  - New feature implementation + writing unit tests (→ `feature`). qa **does not produce code**; it allocates verification effort by risk — writing new unit tests is not the goal
  - Fixing the root cause of a defect (→ `bug`). qa only goes as far as **finding and recording** defects; the fix is a separate work type
  - Structure improvement that preserves existing behavior (→ `refactor`)

## Procedure

1. **Fix the verification target and scope** — make the boundary explicit for what to verify and what to exclude / Deliverable: verification scope definition (target list + exclusion items)
2. **Assess risk (risk-based)** — score risk per area as impact × likelihood, classify high/medium/low / Deliverable: risk table (area · impact · likelihood · grade)
3. **Allocate verification effort** — allocate verification depth and time in proportion to risk grade (high risk = focused, multiple techniques; low risk = smoke) / Deliverable: allocation plan (per-area technique/time mapping)
4. **Define verification cases** — write verification cases as AC (Given/When/Then) starting with high-risk areas / Deliverable: verification case list (with risk-grade tags)
5. **Write exploratory test charters** — define a charter (goal/scope/time box) for areas that automated cases do not reach / Deliverable: charter list (each charter = goal + scope + time box)
6. **Run verification + record defects** — run cases and charters, record found defects with reproduction steps / Deliverable: run results + defect list (reproduction steps · severity · affected area)
7. **Coverage / pass-fail decision** — check whether high-risk areas are covered → pass/fail decision / Deliverable: verification report (coverage by risk grade + unresolved defects + decision)

> Concrete verification techniques (how to use test frameworks / automation tools / load and security verification procedures) and per-area risk-analysis criteria are delegated to the analysis procedures and teammates that **the project supplies** (project `.claude/agents/`). This playbook defines only the general quality-verification flow.

## AC format

Write each verification case with 5 fields. Tag it with a risk grade (high/medium/low) as well.

- **Given** — preconditions (input / state / environment / risk area)
- **When** — verification action (run / input / execute exploratory charter)
- **Then** — expected result (normal behavior / spec match / absence of defects)
- **Verification method** — automated test / manual procedure / exploratory session observation
- **Pass/fail criteria** — pass condition (quantitative or clearly qualitative) / defect-decision criteria

> No unmeasurable AC of the form "works well / looks fine" allowed.

Example (domain-agnostic — high-risk input verification):

- **Given** — a core processing path given boundary values / abnormal input (high risk)
- **When** — run the behavior with that input
- **Then** — return the defined reject/exception response without error, no state corruption
- **Verification method** — automated cases (boundary values) + exploratory session (unexpected input combinations)
- **Pass/fail criteria** — PASS if the defined response / defect (tagged severity) if undefined behavior or state corruption

## Hard Gate

> **HARD GATE**: no pass decision while high-risk area verification is uncovered
> If unmet: block procedure 7 (pass decision) — every high-risk-grade area in the risk table (procedure 2) must be covered by a verification case or charter to be able to pass. Verification that does not apply risk-based priority (equal/arbitrary allocation) is considered incomplete verification
> Bypass: only on explicit user expression (skip / move on / bypass / skip it)

> **HARD GATE**: no running verification without risk assessment
> If unmet: block procedure 6 (run verification) — procedure 2 (risk assessment) + procedure 3 (effort allocation) are required first. Verification with no basis for risk allocation cannot make a coverage decision
> Bypass: only on explicit user expression

## Feedback loop location

The "verify → feedback → fix → re-verify" loop of this playbook:

1. **Procedure 6 (run verification + record defects)** — the core loop. Run cases and charters (verify) → find defects (feedback) → record defects and re-assess risk → re-verify affected areas. Exploratory charters spawn follow-up charters based on findings
2. **Procedure 2↔3 (risk assessment ↔ allocation)** — an early loop that updates the risk table and allocation and re-allocates when new risks surface during execution
3. **Procedure 7 (coverage / pass-fail decision)** — a gate loop that returns to procedures 4–6 when an uncovered high-risk area is found

> The loops above are verification loops **within the work flow**. Improvement of the playbook itself ("is this verification flow correct") is the responsibility of retrospective-based evolution (the `retro-processing` work type) — outside this playbook's scope.

## Review / evaluation points

- **Review**: procedure 2 (risk-assessment review — check for missed / underestimated risks) + procedure 5 (charter review — whether goal/scope/time are clear) + procedure 7 (verification-report review). Prioritize essential defects in risk identification (missed high-risk areas). Delegate when the project supplies a review teammate. **RT runs default-on** (rigor / independence = README §7 + RT rigor matrix). RT essential attacks: uncovered high-risk areas, underestimated risk, goalless charters.
- **Evaluation**: procedure 4 verification-case AC (Given/When/Then) satisfaction + procedure 7 coverage by risk grade = deliverable evaluation criteria. 100% coverage of high-risk areas + 0 unresolved high-severity defects = pass.
- The `flow-procedure-story` §7-2 review/evaluation Hard Gate forces the above points to run.

## Violation handling

- Verification without risk assessment / pass decision with uncovered high-risk areas / goalless exploration without a charter = block or request completion
- Bypass allowed only on explicit user expression (skip / move on / bypass / skip it)
- The fact of a bypass + uncovered high-risk areas = obligatory record in the retrospective Problem section
