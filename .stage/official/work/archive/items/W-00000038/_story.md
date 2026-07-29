---
id: W-00000038
title: C8: exhaustive migration + v4 QA (adversarial fixtures)
kind: qa
venue: codex
source:
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000037
promotion: not_applicable
review: not_required
scope: stage/scripts/,stage/hooks/,stage/skills/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000038 C8: exhaustive migration + v4 QA (adversarial fixtures)

## Purpose

C8 per SCHEMA_V4.md: exhaustive end-to-end QA hardening the v3->v4 migration and v4 operation for OTHER users' projects (this repo's own dogfood already succeeded). Adversarial fixtures: every preflight refusal (dirty tree, symlinked root, case collision, pending intents/claims, legacy promote-intent.json, mixed populated topology); abort restores cleanly mid-migration; customized/hand-edited files and non-recognizable index.md emit a merge file instead of corrupting; ko-locale projects migrate; Contract X decision identity survives; milestone closure basis/revalidation survive a migrated project; post-migration a full v4 lifecycle (roadmap+work+closure) runs clean. Add any missing regression tests; fix any defect found. v4-only paths; no v3 regression.

## Scope


## Success criteria


## Related truth


## Progress

- 2026-07-13 — Added adversarial external-project migration QA:
  - strengthened every preflight refusal fixture to compare the complete `.stage` directory
    entry/byte snapshot, git status, legacy roots, maintenance marker absence, and
    `schema_version: 3`; scenarios cover dirty content inside a relocation source, a symlinked
    `.stage`, a case-insensitive destination collision, pending intent and claim files, legacy
    `promote-intent.json`, and mixed populated v3/v4 topology;
  - confirmed ordinary `.stage/.runtime/` dirt is exempt while intent/claim files reach the
    dedicated pending-promotion refusal;
  - injected a failure after relocation and verified abort restores the exact committed v3 tree,
    removes all v4 roots/transaction files, preserves pre-existing runtime files and empty
    directories, and leaves `schema_version: 3`;
  - verified an unrecognizable customized root `index.md` remains byte-identical and receives a
    proposed v4 merge file without a maintenance marker or topology mutation;
  - verified a hand-edited project-owned operations document and an extra custom file under the
    proposals governed directory migrate without loss;
  - migrated a `language: ko` project, preserving Korean prose and selecting Korean v4 indexes;
  - migrated promoted legacy `D-` and pending stable `DE-` decisions, verifying rewritten
    `decision_refs`, preserved predecessor/supersedes links, both resolver paths, and a clean
    strict audit;
  - on a migrated project, ran theme/milestone creation, pursuit, work registration, start,
    close, archive, frozen-basis milestone closure, drifted-basis promotion refusal, successful
    promotion revalidation, and post-closure re-attribution refusal, with strict audit clean
    after every valid lifecycle transition.
- 2026-07-13 — Defect fixed (runtime-dirt preflight): `_runtime_path()` used `lstrip("./")`,
  which removed the leading dot from `.stage` and incorrectly rejected all untracked runtime
  files as dirty-tree blockers; fixed prefix normalization and added the red-first runtime/intent
  regression fixture.
- 2026-07-13 — Defect fixed (exact abort): abort restored tracked v3 content but left the empty
  `.stage/.runtime/` directory created by the migration; the journal now records pre-existing
  runtime directories and abort removes only migration-created empty directories, with a
  red-first interrupted-relocation fixture covering runtime preservation.
- 2026-07-13 — Final suites: hooks 300 tests passed; scripts 256 tests passed (including 22
  migration-focused tests). `STAGE_SCHEMA_VERSION` remains 4.

## Verification


### Executed at close — 2026-07-13

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 256 tests in 22.266s

OK

$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
