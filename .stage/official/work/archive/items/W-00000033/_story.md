---
id: W-00000033
title: C4b: legacy-root denial gate + lifecycle views (v4-only)
kind: development
venue: codex
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000032
promotion: not_applicable
review: not_required
scope: stage/hooks/,stage/scripts/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000033 C4b: legacy-root denial gate + lifecycle views (v4-only)

## Purpose

C4 (part b) per SCHEMA_V4.md: on a schema-v4 project only, (1) the write gate denies writes under recreated legacy roots (.stage/past, .stage/present, .stage/future) using stage_topology.is_legacy_path, so stale instructions cannot resurrect the retired split topology; (2) add derived cross-family lifecycle views (planned/current/official across families) surfaced in the session context on v4 projects, restoring the ambient visibility the removed wrappers used to give. v3 behavior byte-for-byte unchanged; STAGE_SCHEMA_VERSION stays 3. Parent lineage: sibling of C4a (W-00000032).

## Scope


## Success criteria


## Related truth


## Progress

- 2026-07-13: v4 전용 legacy-root denial과 registry 기반 read-only lifecycle view를 구현하고
  회귀 테스트를 추가했다. `stage_paths.STAGE_SCHEMA_VERSION`은 3으로 유지했으며 기존 테스트
  assertion은 수정하지 않았다.

## Verification


### Executed at close — 2026-07-13

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 284 tests in 0.535s

OK

$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
