# Plot — NEXT SESSION queue

> **Surfaced automatically by the SessionStart hook
> (`plot/hooks/session_start.py`) at every new session start.**
> When the user invokes a queued item by its trigger keyword, that
> item becomes the active task for the session.

---

## Active queue

No keyword-triggered items right now. The backlog below is
ordered by size; user picks the next item explicitly each
session. (Full context lives in
[`memory/project_plot_next_session.md`](../../.claude/projects/-Users-woogis-Workspace-repo-noory-ai/memory/project_plot_next_session.md)
which the session-start hook surfaces.)

### Backlog — small wins (< 1 session each)

1. **i18n audit skill** (`plot/skills/plot-i18n-audit/`) — detect
   unused / missing / orphan locale keys. User flag 2026-05-12.
2. **`owner` field on `SketchNode`** — multi-user prerequisite
   (PRODUCT_SPEC §15 #1).
3. **Mermaid Service-Detail rendering** — UI location decision
   (PRODUCT_SPEC §15 #5).
4. **Self-loop visual verification** — `Service A → Service A`
   renders correctly in React Flow (PRODUCT_SPEC §7).
5. **Foundation single-canvas flow visual** — Mission → Core
   value → Identity visual flow check (PRODUCT_SPEC §8).

### Backlog — meta decisions (user input required)

6. **Plot repository split** — move `plot/` out of the
   `noory-ai` monorepo to its own repo. AI recommends split;
   7-step plan in the memory file. User decision pending.

### Backlog — mid-size (each = own plan, multi-commit)

7. **isomorphic-git integration** (PRODUCT_SPEC §6) — viewer +
   MCP gain canvas-versioning. Precondition for PR-style
   feedback loop (§11) enforcement.
8. **MD-as-export migration** (PRODUCT_SPEC §15 #2) —
   **user-deferred** *"이 부분은 나중에 다시 다듬어 봅시다."*
   Do not start without explicit user kick-off.
9. **Snapshot work-item layer** (PRODUCT_SPEC §10) — tasks +
   user-stories + commit-SHA provenance. Depends on (7).
10. **v0.15 Actors → v0.13 model** — re-evaluate after (8) lands
    since the data model shifts.

---

## How this file works

- The `SessionStart` hook (`plot/hooks/session_start.py`) reads
  this file at every session start and prepends each `### TRIGGER`
  heading to the assistant's context.
- The assistant then watches for the user's next message. If it
  contains a trigger keyword, the assistant executes the matching
  item.
- After completion, the assistant **moves the item to the
  "Completed" section below** with the date + commit hash, instead
  of deleting it. This preserves the audit trail.
- New items are added to "Active queue" by appending a
  `### TRIGGER — short title` section with the same structure as
  the example above.

---

## Completed

### `다음` — Architectural review: cursor / auto-layout coupling

> **Completed:** 2026-05-10 in v0.14.3.
> **Outcome:** [D-2026-05-11-C](./DECISIONS.md#d-2026-05-11-c--cursor--auto-layout-cognitive-coupling-not-mechanical-structural-gate-added).
> **Diagnosis:** the coupling was *cognitive (commit bundling)*,
> not *mechanical (shared files)*. Cursor flicker was a latent
> RF v11 + Tailwind preflight bug from v0.13.0; auto-layout work
> was the discovery trigger, not the cause. The v0.13.10 commit
> bundled both concerns and produced the misattribution.
>
> **Structural gate shipped:**
> 1. `pre_commit_gate.py::cross_cutting_bundle_check` blocks
>    commits that stage `viewer/src/styles.css` alongside feature
>    code.
> 2. `viewer/tests/styles-cursor-baseline.test.tsx` static guard
>    asserts `styles.css` has zero cursor rules.
> 3. `plot/agents/plot-verifier.md` Step 4 default now runs
>    cursor DOM probe sweep on every viewer change.
> 4. `plot/CLAUDE.md` anti-patterns table gains a row.
>
> **Original review scope** (filed 2026-05-11 by user, ref
> D-2026-05-11-B): Coupling map, causal trace, design options
> (a–d), pin via decision id, regression test, plan filing. All
> six steps completed; design choice = (b) pre-commit gate +
> static test + verifier default. Options (a) / (c) / (d)
> evaluated and rejected with rationale in D-2026-05-11-C.
