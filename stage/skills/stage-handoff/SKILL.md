---
name: stage-handoff
description: Hand work off between LLM windows or sessions with minimal human effort. Use when ending a session, or when a work item should be carried out on a different execution surface (e.g. planning window to implementation window). Makes the venue routing and next action explicit so the human just opens the indicated window.
---

# Stage Handoff

A project may be worked by more than one surface (e.g. a Claude planning window and a Codex
implementation window). The shared work SSOT carries the routing signal so the human reads one
place to know which window to open next.

## Route by venue

- `venue` on each work item names the surface that should carry it out. It is advisory — no hook
  gates on it.
- `present/work/active.md` shows every open item with its `Venue` column. This is the routing
  view: the human opens the window whose venue has open rows.
- The project's `venue` values and any `kind -> venue` routing live in `past/canon/vocabulary.md`.
  The harness fixes no venue names.

## Before handing off, make each open item self-carrying

For every `active`/`blocked` item you are leaving:

1. Update its body with current status and the explicit NEXT action — the receiving window must be
   able to continue without you.
2. Set `venue` to the surface that should take it next.
3. Confirm `active.md` reflects the item's real status and venue.

## Session summary is automatic

On session stop, the Stage hook writes a per-session summary to
`.stage/.runtime/sessions/<session>.md` (machine-local, git-ignored). Concurrent windows each keep
their own summary — no last-write-wins. Do not hand-maintain it; keep the work items and `active.md`
current instead, since those are what the next window reads first.

## Tell the human where to go

End the handoff with one line: which venue/window has open work and what its next action is. That
is the whole human intervention.

## Verify

`python3 stage/scripts/audit_stage.py --project-root <project-root>` — every open item present in
`active.md`, no index mismatch.
