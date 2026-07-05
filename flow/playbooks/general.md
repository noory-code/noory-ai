---
name: general
description: A general-purpose flow independent of work type — the fallback for work that does not fit a specific work-type playbook
---

# general (general-purpose fallback)

A general-purpose way of working for tasks that do not clearly match a specific work-type playbook (feature/bug/refactor/docs, etc.). It defines only a minimal skeleton — understand the task → plan → execute → verify → retrospective. It does not enforce any specific methodology.

> **Position**: a replacement for a fixed `default`. When selecting a playbook, if the work type fits no playbook, fall back to this `general` (no specific playbook is forced as the default — `flow-playbook-selection`).

## Applies to

- Work that does not clearly match any work-type playbook
- Exploratory / mixed / one-off work
- Not suitable: if the work type is clear, use that playbook (general is a fallback only)

## Procedure

1. **Understand the task** — clarify what/why + completion conditions / deliverable: task definition (goal + completion criteria)
2. **Plan** — break into steps + decide verification points / deliverable: step list (each verifiable)
3. **Execute** — perform the planned steps / deliverable: work output
4. **Verify** — confirm the completion criteria are met / deliverable: check result
5. **Retrospective** — evaluate AI behavior + learnings / deliverable: retrospective (Keep/Problem/Try)

## AC format

Each AC has 5 fields: **Given** / **When** / **Then** / **Verification method** (grep·ls·test or manual observation) / **Pass/fail criteria**.

Example (domain-agnostic): Given the task is defined (completion criteria stated) / When the planned steps run / Then the completion criteria are met / Verification: deliverable exists + checked against completion criteria / Pass: all completion criteria met.

## Hard Gate

> **HARD GATE**: no execution without understanding the task (completion criteria)
> If unmet: the execution step is blocked — define completion criteria first
> Bypass: only on explicit user phrasing (skip / move on / bypass / skip it)

## Feedback-loop location

- **Verify (step 4)** — if the completion criteria are not met, return to Execute (step 3), remediate, and re-verify

## Review/evaluation points

- **Review**: review the deliverable at Verify (step 4) — an essential check against the completion criteria. Delegate when the project supplies a review teammate. **RT runs default-on** (strength/independence = README §7 + RT strength matrix).
- **Evaluation**: whether the completion criteria (defined when understanding the task) are met = the deliverable evaluation criterion.
- The `flow-procedure-story` §7-2 review/evaluation Hard Gate enforces execution of the points above.

## Violation handling

- Execution without completion criteria / skipping verification = block or request remediation
- Bypass is allowed only on explicit user phrasing + a mandatory record in the retrospective Problem section
