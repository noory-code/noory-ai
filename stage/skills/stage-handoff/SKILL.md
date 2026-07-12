---
name: stage-handoff
description: Hand Stage work off between LLM windows or sessions with minimal human effort. Use this when ending a session, writing a handoff, or when a work item should move to a different execution surface (e.g. a planning window handing implementation to a Codex window) — anytime work needs to pass between agents or be picked up later. Makes the venue routing and the next action explicit so the human just opens the indicated window.
---

# Stage Handoff

A project may be worked by more than one surface (e.g. a Claude planning window and a Codex
implementation window). The shared work SSOT carries the routing signal so the human reads one
place to know which window to open next.

## Route by venue

- `venue` on each work item names the surface that should carry it out. No hook gates on it, but
  when the project declares a role policy the audit checks consistency (VENUE001-VENUE005).
- `present/work/active.md` shows every open item with its `Venue` column. This is the routing
  view: the human opens the window whose venue has open rows.
- The machine-readable role policy lives in `settings.json` `venue_routing` (`kind -> venue`);
  what each venue means belongs to the project's canon (e.g. `past/canon/vocabulary.md`). The
  harness fixes no venue names. Registration derives the venue from the policy without asking the
  human; a contradicting venue registers only with `--decision <DE-id>` naming a decided decision
  that declares `authorizes: venue_exception`, and a kind routed to the reserved value `split`
  registers as separate design/implementation items with `parent` lineage.

## Before handing off, make each open item self-carrying

For every `active`/`blocked` item you are leaving, its body must answer five things the receiving
window cannot ask you: purpose, completed context (what is already done and verified), the
remaining problem, the success criteria, and the explicit NEXT action.

1. Update the item body with those five elements in human-readable language.
2. Set `venue` to the surface that should take it next.
3. Confirm `active.md` reflects the item's real status and venue.

## Route decisions back, not sideways

An implementation venue that hits an unresolved product or design decision does not decide it and
does not stall: register a planning-venue item that carries the implementation evidence and the
exact decision needed, link the blocked item (`parent` or body reference), and hand off. Each
transition names one unresolved decision or one executable next action — that is what keeps
bidirectional handoffs from looping.

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
