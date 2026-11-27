---
id: W-00000437
title: Keep Stage SKILL.md bodies under Antigravity 24KB limit
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s tests -q"
  - "python3 -m unittest stage/scripts/tests/test_orchestrate_skill.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-work/,stage/skills/stage-drive/,stage/skills/stage-orchestrate/,stage/scripts/tests/test_orchestrate_skill.py,tests/test_plugin_contracts.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000437 Keep Stage SKILL.md bodies under Antigravity 24KB limit

## Purpose

Keep every Stage SKILL.md body at or below 24000 bytes so Antigravity loads every skill completely without truncation.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Every stage/skills/*/SKILL.md body is 24000 bytes or smaller and agy plugin validate reports zero skill-size warnings.
- All skill content moved to sibling reference files remains linked from SKILL.md and test_orchestrate_skill.py passes.

## Next action


## Related truth


## Sessions


## Progress


## Verification
