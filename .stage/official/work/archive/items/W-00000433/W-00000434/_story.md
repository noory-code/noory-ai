---
id: W-00000434
title: Package Stage as a native Antigravity plugin and sync releases
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s tests -q"
  - "python3 -m unittest stage/scripts/tests/test_release_plugin.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000434
promotion: not_applicable
review: not_required
scope: stage/.antigravity-plugin/plugin.json,stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,tests/test_plugin_contracts.py,.github/workflows/plugin-contracts.yml,README.md,stage/README.md,CLAUDE.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000434 Package Stage as a native Antigravity plugin and sync releases

## Purpose

Deliver Stage as a valid native Antigravity plugin whose manifest stays in sync with Claude and Codex on release.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- agy plugin validate --json ./stage exits 0 with zero errors (loading 1 hook group and 13 skills, with pre-existing multi-host and >24KB skill warnings documented).
- release_plugin.py and plugin contract tests validate and bump Claude, Codex, and Antigravity manifests together.

## Next action


## Related truth


## Sessions


## Progress


## Verification

- Checks at close 2026-11-27: 2 passed — `python3 -m unittest discover -s tests -q`; `python3 -m unittest stage/scripts/tests/test_release_plugin.py`
- Load at close 2026-11-27: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
