---
id: W-00000435
title: Add Antigravity native hook adapter for Stage gates
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/hooks/tests/test_agy_adapter.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000435
promotion: not_applicable
review: not_required
scope: stage/hooks.json,stage/hooks/agy_adapter.py,stage/hooks/stage_context.py,stage/hooks/tests/test_agy_adapter.py,stage/hooks/README.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000435 Add Antigravity native hook adapter for Stage gates

## Purpose

Enforce Stage registration, promotion, deletion, question, and session-summary gates inside Antigravity sessions.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Antigravity SessionStart and PreInvocation hooks inject Stage context and active purpose chains via injectSteps.
- Antigravity PreToolUse, PostToolUse, and Stop hooks enforce Stage gates, complete two-phase intent claims, and write session summaries.

## Next action


## Related truth


## Sessions


## Progress


## Verification

- Checks at close 2026-11-27: 1 passed — `python3 -m unittest stage/hooks/tests/test_agy_adapter.py`
- Load at close 2026-11-27: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
