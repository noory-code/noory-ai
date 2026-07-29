---
id: W-00000010
title: Configurable per-stage, per-strength review in settings.json
kind: feature
venue: claude
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000010
promotion: not_applicable
scope: stage/hooks, stage/scripts, stage/skills, stage/templates, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000010 Configurable per-stage, per-strength review in settings.json

## Purpose

Add a review config to .stage/settings.json: per-stage strength (design/implementation/promotion) mapped to project-defined, verdict-emitting review COMMANDS. close_work runs the configured review like a --check (exit-code bound, evidence embedded), fail-closed when a required review command is missing. Strength levels are named slots the project binds to real commands, so the label is bound to execution, not theater. Red-teamed design (Option A + strength map).

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
Ran 250 tests in 0.510s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 107 tests in 3.389s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
