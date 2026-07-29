---
id: W-00000014
title: Make AI roles drive Stage work routing and handoffs
kind: feature
venue: claude
source: B-00000003
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000014
promotion: not_applicable
scope: stage, .stage
promotes:
decision_refs: DE-00000004
---

# W-00000014 Make AI roles drive Stage work routing and handoffs

## Purpose

Make each AI derive a work item's `venue` from a project-declared role policy instead of asking
the human, keep exceptions explicit through decision records, and make cross-venue handoffs
self-contained — without hard-coding any AI product into the harness core.

## Scope

- Record the role-policy schema, its SSOT, derivation, exception, and handoff contract as a
  working decision before implementation.
- Add a project-owned machine-readable `kind -> venue` routing policy with a backward-compatible
  default (no policy declared → current advisory behavior).
- Make work registration derive the default venue from the policy and mark policy exceptions as
  requiring a linked decision record.
- Audit missing venues, unknown venues, and policy-inconsistent venues without a decision link.
- Inject the declared routing policy into session context so every AI reads it before
  registering or accepting work.
- Update the stage-work and stage-handoff skills: split mixed design+implementation work into
  separate items with lineage, route unresolved decisions back to the planning venue, and require
  self-contained handoffs (purpose, completed context, remaining problem, success criteria, next
  action).
- Declare this repository's routing policy in its `.stage/settings.json`.
- Bump the Stage plugin version in both manifests and record the change in the changelog.

## Success criteria

- With a declared policy, registration derives the venue for routed kinds without asking the
  human; kinds without a route keep per-item choice.
- A venue that contradicts the declared policy is accepted only alongside a decision reference;
  the audit reports the missing link otherwise.
- Missing and unknown venues are reported by the audit only when a policy is declared;
  single-venue and no-policy projects keep current behavior with zero new findings.
- The session context shows the declared routing policy and the split/back-routing rules.
- No Claude- or Codex-specific logic enters hooks, scripts, or the audit; venue names are
  project-declared strings.
- Stage hook and script tests pass, including policy-present, policy-absent, exception, and
  malformed-policy cases.

## Related truth

- Realizes `B-00000003`.
- This repository's venue meaning lives in `official/canon/vocabulary.md` (promoted by W-00000012);
  the machine routing map added here lives in `.stage/settings.json`.

## Progress

- DE-00000004 fixed the routing schema (flat `kind -> venue` map in `settings.json`
  `venue_routing`), the exception contract, and the handoff/back-routing rules before
  implementation.
- `load_venue_routing` shipped in `stage_paths.py` (fail-open normalization; audit owns
  malformation reporting).
- `register_work.py` derives an omitted venue and announces policy exceptions requiring a
  `decision_refs` link.
- The audit gained `VENUE001`–`VENUE004`, applied to open present items only.
- SessionStart injects the declared routing map with the derive/split/back-routing rules.
- `stage-handoff` requires the five-element self-contained handoff; `stage-work`,
  `operations/artifacts.md`, and the README moved the machine policy owner to `settings.json`.
- This repository declared planning/design -> claude and development/fix/qa/ops -> codex.
- Released as 0.21.0.

## Verification

Executed this session:

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 269 tests in 0.517s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 148 tests in 4.122s

OK
```

## Retrospective

See `R-00000014` in `work/retrospectives/`.

## Promotion decision

`promotion: not_applicable` — all changes live in the `stage/` plugin and this repository's
`.stage/settings.json`; the venue meaning already promoted by W-00000012 is unchanged.
