---
id: W-00000433
title: Add native Antigravity (agy) support for Stage
kind: planning
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000433
promotion: not_applicable
review: not_required
scope: stage/,tests/test_plugin_contracts.py,.github/workflows/plugin-contracts.yml,README.md,CLAUDE.md
promotes:
decision_refs:
---

# W-00000433 Add native Antigravity (agy) support for Stage

## Purpose

Run Stage natively as an Antigravity plugin and venue with the same gates, release workflow, and review containment as Claude and Codex.

## Stories


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage passes agy plugin validate --json ./stage with exit 0 and zero errors (loading 1 hook group and 13 skills, with pre-existing multi-host and >24KB skill warnings documented) and releases all three host manifests in step.
- An Antigravity session on a .stage project receives session-start context, enforces Stage PreToolUse gates, and writes Stop summaries.
- Stage close reviews and drivers can invoke agy -p through agy_review_companion.py with tool-call recording and Antigravity session-folder containment.

## Next action


## Related truth


## Sessions


## Progress


## Verification

- Checks at close 2026-11-27: 2 passed — `python3 -m unittest discover -s tests -q`; `python3 -m unittest discover -s stage/hooks/tests -q`
- Load at close 2026-11-27: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
