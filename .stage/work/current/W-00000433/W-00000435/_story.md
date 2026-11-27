---
id: W-00000435
title: Add Antigravity native hook adapter for Stage gates
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/hooks/tests/test_agy_adapter.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
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
