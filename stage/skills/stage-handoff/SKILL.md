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
- `work/active.md` shows every open item with its `Venue` column. This is the routing
  view: the human opens the window whose venue has open rows, or a bridge-equipped window
  executes them by delegation (below).
- The machine-readable role policy lives in `settings.json` `venue_routing` (`kind -> venue`);
  what each venue means belongs to the project's canon (e.g. `official/canon/vocabulary.md`). The
  harness fixes no venue names. Registration derives the venue from the policy without asking the
  human; a contradicting venue registers only with `--decision <DE-id>` naming a decided decision
  that declares `authorizes: venue_exception`, and a kind routed to the reserved value `split`
  registers as separate design/implementation items with `parent` lineage.

## Delegated execution

`venue` names the surface that EXECUTES the work — the agent whose model produces the
artifact — not the window that hosts it. A window equipped with a bridge to another venue's
executor (e.g. a Claude window carrying a Codex plugin) may therefore carry out that venue's
card by delegation instead of waiting for a human to switch windows:

- The hosting window forwards the card's self-carrying body (purpose, completed context,
  remaining problem, success criteria, NEXT action) to the venue's executor through the
  bridge, and stays responsible for monitoring the run to completion.
- The delegated executor works under the same Stage gates as a native window — registration,
  scope, and commit gates apply to the bridged process identically.
- The hosting window reviews the delegated output before the card closes (see
  `operations/review.md`, Cross-venue review). Delegation transfers execution, never review:
  the executor of a card and the reviewer of that card must be different venues.
- Decision points do not delegate: an unresolved product or design decision still routes back
  as a planning-venue item (below), and the human still owns promotion approvals.
- Delegation is optional per card. When no bridge is available, the routing view's default
  applies: the human opens the venue's window.

### The delegated run, end to end

Delegation splits one card between two agents, so say once who does what. The executor produces
the change. Everything that turns a change into a record belongs to the host, because the host is
the reviewer and a record must not be written by the agent whose work it attests to.

1. The host makes the card self-carrying (below) and states the constraints the executor cannot
   read off the card: start the card with `start_work.py` before touching governed files, write
   tests first where the project requires it, and **do not commit**.
2. The executor starts the card, produces the change, and reports what it changed and what it
   ran. It leaves the working tree dirty on purpose.
3. The host reviews that output against the card's success criteria, and re-runs the checks
   itself rather than trusting the executor's transcript.
4. The host commits the source while the card is still open (`operations/after.md`).
5. The host closes the card with `close_work.py`, then archives it.

Telling the executor to commit costs a full run: a bridged executor often cannot write to `.git`
at all, and the refusal lands after the implementation is finished, when the only remaining step
was the one it could not take. The host was going to commit anyway — it holds the review.

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
