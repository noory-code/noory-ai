---
id: W-00000002
title: Add venue field for dual-agent work routing
kind: feature
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000004
promotion: not_applicable
venue: claude
scope: stage/
promotes:
decision_refs:
---

# W-00000002 Add venue field for dual-agent work routing

## Purpose

A solo developer runs two AI surfaces side by side (a planning/architecture
window and an implementation window) and needs each work item to declare which
surface should execute it, so the human can glance at the Active Work index and
open the right window. Stage owns the shared work SSOT, so the routing signal
belongs on the work item itself, not in either chat window.

## Scope

Add an optional `venue` frontmatter field to the work-item shape and surface it
as a column in the Active Work index. The field is advisory: it is a human
routing hint, never a hook gate. Values are project-defined (like `kind`); the
harness ships general, with the project declaring its venues and the
`kind -> venue` routing in `past/canon/vocabulary.md`. Hardcoding specific agent
names into the harness is out of scope (SSOT / generality).

Scope covers `stage/` only:
- `templates/project-stage/present/work/items/_template.md`
- `templates/project-stage/present/work/active.md`
- `templates/project-stage/present/work/items/README.md`
- `templates/project-stage/operations/artifacts.md`
- `templates/project-stage/past/canon/vocabulary.md`
- version bump + CHANGELOG

## Success criteria

- New work items carry a `venue` field; existing items without it stay valid
  (optional, empty default) — no migration required.
- Active Work index shows a Venue column.
- artifacts.md documents the field; vocabulary.md carries a general,
  clearly-marked example of project venues and `kind -> venue` routing.
- Hook parsing and audit are unchanged (no gate on venue); tests pass.

## Related truth

- `operations/artifacts.md` — work frontmatter field SSOT.
- `hooks/stage_work.py` — permissive frontmatter parser; unknown/absent keys
  are ignored/defaulted, which is why adding an optional field is not breaking.

## Progress

- Added optional `venue` field to the plugin work-item template and a `Venue`
  column to the Active Work index template.
- Documented the field in `items/README.md` and `operations/artifacts.md`;
  added a `Venue` term and example `kind -> venue` routing table to
  `official/canon/vocabulary.md`.
- Bumped both plugin manifests 0.12.1 -> 0.13.0 and added a CHANGELOG entry.
- Synced the live `.stage/work/current/_template.md` so new items in this
  repo carry the field. The live `official/canon/vocabulary.md` routing table is
  deferred to the promotion-intent flow (the canon subtree is gate-protected).

## Verification

- `python3 -m unittest discover -s stage/hooks/tests -q` — 235 tests OK.
- `python3 -m unittest discover -s stage/scripts/tests -q` — 85 tests OK.
- `python3 stage/scripts/audit_stage.py` — errors=0 (2 pre-existing KIND001
  warnings unrelated to venue).
- Confirmed no migration: the frontmatter parser ignores/defaults absent keys,
  so existing work items without `venue` stay valid.

## Retrospective

See [R-00000004](../retrospectives/R-00000004.md). Learning — an optional frontmatter field is
non-breaking because the parser defaults absent keys; canon routing edits go through the
promotion-intent flow.

## Promotion decision

`promotion: not_applicable` — the change lives in the `stage/` plugin package,
not in this repo's `.stage/official/` canon, so there is nothing to promote here.

