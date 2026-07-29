---
id: W-00000036
title: C6b: milestone closure snapshot + revalidation + re-attribution gate
kind: development
venue: codex
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000035
promotion: not_applicable
review: not_required
scope: stage/skills/,stage/scripts/,stage/hooks/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000036 C6b: milestone closure snapshot + revalidation + re-attribution gate

## Purpose

C6 (part b) per SCHEMA_V4.md Roadmap family closure semantics: (1) a milestone closure decision freezes the exact W ids with their terminal_disposition and the completion-criteria attestation; closure is valid only when every linked W is terminal (archived accepted or explicitly rejected). (2) Promotion of a closure revalidates the frozen basis against live state through the registry, fail-closed with the diff shown. (3) Re-attribution gate (preventive, write-gate): a W id in any effective closure snapshot cannot change its milestone: field without a decision superseding that closure. (4) Reopening requires a superseding decision. All v4-only, gated on schema_version; v3 unchanged; STAGE_SCHEMA_VERSION stays 3. Parent lineage: sibling of C6a (W-00000035).

## Scope


## Success criteria


## Related truth


## Progress

- 2026-07-13 — Implemented the v4-only immutable milestone-closure basis, promotion-time
  fail-closed revalidation, preventive re-attribution gate, and supersession-based reopen
  contract. `STAGE_SCHEMA_VERSION` remains 3 and no existing test assertion was modified. The
  end-to-end v4 fixture created a theme and milestone, attributed and archived two W cards with
  `terminal_disposition: accepted` / `rejected`, captured both exact outcomes plus the
  completion-criteria attestation, passed promotion revalidation, and denied an illegal
  milestone change naming the effective closure. Fail-closed coverage also denied disposition
  drift, a missing basis card, and a newly linked card with exact id-level diffs. Verification:
  hook suite 298 tests green; script suite 234 tests green.


## Verification


### Executed at close — 2026-07-13

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 298 tests in 0.787s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 3
Migration complete.
  unchanged operations/verification.md (unchanged)
Migration complete.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 3
Migration complete.
----------------------------------------------------------------------
Ran 234 tests in 11.923s

OK

$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
