---
id: W-00000436
title: Add agy review companion and Antigravity containment
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_agy_review_companion.py stage/scripts/tests/test_review_containment.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/agy_review_companion.py,stage/skills/stage-retrospective/review_containment.py,stage/scripts/tests/test_agy_review_companion.py,stage/scripts/tests/test_review_containment.py,stage/docs/BLUEPRINT.md,stage/docs/SCHEMA_V5.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000436 Add agy review companion and Antigravity containment

## Purpose

Enable Stage close reviews and drivers to run agy -p headlessly while recording tool calls and flagging Antigravity session-folder reads.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- agy_review_companion.py builds valid agy -p commands and relays stream-json tool calls and results into Stage logs.
- review_containment.py flags commands referencing Antigravity session folders (~/.gemini/antigravity and ~/.gemini/antigravity-cli) as outside reach.

## Next action


## Related truth


## Sessions


## Progress


## Verification
