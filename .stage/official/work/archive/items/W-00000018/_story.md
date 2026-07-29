---
id: W-00000018
title: Schema v4 official-zone design freeze
kind: design
venue: claude
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000018
promotion: not_applicable
review: not_required
scope: stage/docs/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs: DE-00000009
---

# W-00000018 Schema v4 official-zone design freeze

## Purpose

Freeze the schema v4 design agreed in the 2026-07-12 dual debates and the post-verdict zone-rename amendment: topology registry interface, official-zone layout (`past/` renamed `official/`, `present/`/`future/` wrappers removed), planned/current/official lifecycle vocabulary, Contract X decision identity, terminal_disposition ownership, migration contract, and roadmap interfaces — as the canonical design document C2-C9 implement against.

## Scope

- Author the canonical schema v4 design document under `stage/docs/` (new file), covering: root topology, topology-registry interface, lifecycle vocabulary and gate mapping, decision identity (Contract X), `milestone:` and `terminal_disposition` frontmatter contracts, closure snapshot/revalidation, migration contract, defense triage, and the C2-C9 card map.
- Bump plugin versions and add a CHANGELOG entry per the repository's plugin-change rule.
- Out of scope: any code, template, hook, or `.stage/` topology change (C2-C8), and doc rewrites of existing operations/skills files (C9).

## Success criteria

- The design document states every interface C2-C8 need, with no undefined term: registry family/zone table shape, relocation map, marker/journal semantics, DE identity resolution rules, closure basis fields.
- Every debate ruling is traceable: the document's decisions match the debate-2 round-10 verdict and its debate-1 amendment, with deferred defenses listed with their triggers.
- Design review confirmed by the owner (kind=design passes per operations/verification.md), with decisions recorded in `decisions/pending/`.

## Related truth
- Debate record: Codex thread 019f5637-2372-7d51-9727-a470c4b5b533 (2026-07-12, 5+10 rounds).


## Progress

- Debate 1 (5 rounds) closed roadmap semantics; debate 2 (10 rounds) closed the topology; the
  round-10 verdict shipped with no dissent. Post-verdict amendment renamed the authorization
  zone `past/` → `official/` (owner ruling, Codex APPROVE with intent-preflight conditions).
- `stage/docs/SCHEMA_V4.md` authored and amended; DE-00000009 recorded and amended; plugin
  0.23.1 → 0.23.2 with CHANGELOG entries; commits 6a36a40a, 3b2085c3 pushed.
- Owner approved the design in session ("official 로 합시다", "제대로 만들어 봅시다") after
  ruling every open fork personally.

## Verification

Executed this session:

```
$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ test -s stage/docs/SCHEMA_V4.md
[exit 0]

```

## Retrospective


## Promotion decision
