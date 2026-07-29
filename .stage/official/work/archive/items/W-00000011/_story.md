---
id: W-00000011
title: Optional, field-driven review requirement on work items
kind: feature
venue: claude
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000011
promotion: not_applicable
scope: stage/hooks, stage/scripts, stage/skills, stage/templates, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000011 Optional, field-driven review requirement on work items

## Purpose

Add an optional 'review' frontmatter field (not_required/pending/passed). Absent or not_required = review bypassed (optional). review: pending = an item cannot be completed until review: passed. close_work runs the configured review only when the field is pending (fail-closed if no command), then sets passed. The completion gate + audit enforce it like verification; the enum gate validates the value. Default not_required, so it is opt-in per item and existing items are unaffected.

## Scope


## Success criteria


## Related truth


## Progress


## Verification

Executed this session:

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 253 tests in 0.517s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 110 tests in 3.582s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
