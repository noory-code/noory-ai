---
id: B-00000003
title: Make AI roles drive Stage work routing and handoffs
kind: feature
parent:
status: triaged
priority:
realized_by:
---

# B-00000003 Make AI roles drive Stage work routing and handoffs

## Purpose

Make Claude and Codex assign, split, and hand off Stage work according to their declared roles so a
human does not manually choose `venue` for each work item.

## Source

User request after confirming that Stage currently treats `venue` as an advisory field populated by
the person or AI creating an item, without enforcing the design-to-Claude and implementation-to-Codex
workflow.

## User value

The human sees the purpose, current problem, required decision, and which AI window to open next,
while each AI maintains the routing details and produces a self-contained handoff.

## Scope

### Included

- Define one project-owned role policy mapping planning and design responsibility to Claude and
  implementation, fixes, tests, QA, and operations responsibility to Codex.
- Make every AI read the role policy before registering or accepting work and derive `venue`
  without asking the human during normal routing.
- Split mixed work such as a feature into separate design and implementation items instead of
  assigning one ambiguous item to one venue.
- Make Claude create or update a Codex implementation item after the design, constraints, and
  success criteria are ready.
- Make Codex route unresolved product or design decisions back to a Claude item while preserving
  implementation evidence and the exact decision needed.
- Require handoffs to state purpose, completed context, remaining problem, success criteria, and
  the next action in human-readable language.
- Make work registration derive the default venue from the declared role policy, with an explicit
  recorded decision required for exceptions.
- Audit missing venues, unknown venues, role-policy mismatches, and mixed work that lacks a clear
  responsibility boundary.
- Update Stage skills, templates, context injection, documentation, and tests for both hosts.

### Excluded

- Automatically launching Claude or Codex processes or switching the user's application window.
- Allowing an AI-role rule to make product, policy, budget, or risk decisions that belong to the
  human.
- Hard-coding Claude and Codex into the Stage harness core when a project declares different venue
  names or role ownership.

## Dependencies

- Complete W-00000011 before implementation because it currently owns overlapping `stage/` paths.
- Decide the machine-readable role-policy schema and its SSOT before changing registration or audit
  behavior.
- Preserve compatibility for projects that use one venue or different AI products.

## Risks

- A work `kind` such as `feature` can contain both design and implementation, so kind-only routing
  would assign it incorrectly unless the work is split.
- Overly strict routing could block a capable AI from handling a small self-contained task.
- Bidirectional handoffs can loop unless each transition names one unresolved decision or executable
  next action.
- Advisory instructions alone may drift; deterministic registration and audit checks must agree with
  the documented role policy.

## Verification criteria

- Given planning or design work, Claude registers the correct venue without asking the human.
- Given implementation, fix, test, QA, or operations work, Codex registers the correct venue without
  asking the human.
- Given a feature containing design and coding, Stage creates or requires separate responsibility
  items with explicit lineage and completion criteria.
- Claude-to-Codex and Codex-to-Claude handoffs are self-contained and leave one clear next action.
- A missing, unknown, or policy-inconsistent venue is reported by the audit.
- An intentional exception is accepted only when linked to a recorded decision.
- Single-venue and custom-venue projects remain supported without Claude/Codex-specific core logic.
- Hook, script, audit, and cross-host tests pass.

## Next action

After W-00000011 closes, record the role-policy ownership and schema decision, then create the
realizing work item and implement registration, handoff, and audit behavior together.
