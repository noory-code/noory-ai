# Plot — NEXT SESSION queue

> **Surfaced automatically by the SessionStart hook
> (`plot/hooks/session_start.py`) at every new session start.**
> When the user invokes a queued item by its trigger keyword, that
> item becomes the active task for the session.

---

## Active queue

### `다음` — Architectural review: cursor / auto-layout coupling

> **Trigger:** user says **"다음"** as the first or near-first
> message of a Plot session.
>
> **Filed:** 2026-05-11 by user.
> **Reference:** [DECISIONS.md D-2026-05-11-B](./DECISIONS.md).

#### The problem

The user's exact diagnosis:

> "지금 문제는 오토레이아웃을 넣어달라고 했는데 이거 때문에 커서
> 관련된 코드에 영향을 받는거에요. 이거 잘못된거죠. 완전히 다른
> 영역인데 영향을 받는다? 이거 설계를 잘못한거에요."

Auto-layout (a *Layout* concern, in `EssencePlanning` per
[DOMAIN.md](./DOMAIN.md)) and cursor (a *cross-cutting visual
contract* — see [CURSOR.md](./CURSOR.md)) should be entirely
independent. The empirical record from v0.13.8 → v0.14.2 says they
were not: every auto-layout iteration triggered cursor regressions.

#### Review scope (do all of these in this order)

1. **Coupling map.** List every file modified during v0.13.8 →
   v0.14.2 in commit history:
   ```bash
   git log --name-only --pretty=format:'COMMIT %h %s' v0.13.7..v0.14.2 -- plot/
   ```
   Tag each file with its bounded context per
   [DOMAIN.md](./DOMAIN.md). Identify which files were touched in
   BOTH cursor commits AND auto-layout commits. Those are the
   coupling points.
2. **Causal trace.** For each coupling file, write a one-paragraph
   explanation of *why* the auto-layout work triggered cursor
   changes there. Specifically, was it:
   - Same component owning both concerns (god-object remnant)?
   - Shared mutation path (e.g., `onDocChange` carrying both)?
   - Shared CSS surface (cursor declarations alongside layout
     declarations)?
   - React Flow internals that respond to both kinds of mutation?
3. **Design fix.** Propose a refactor that *severs* the coupling at
   the structural level. Concrete options to evaluate:
   - **(a)** Move all cursor logic into a dedicated module
     `viewer/src/canvases/sketch/cursorContract.ts` (pure CSS
     reference, no React imports). Layout modules import nothing
     from it.
   - **(b)** Add a CI / pre-commit gate that fails any commit
     touching both `viewer/src/canvases/sketch/autoLayout.ts` (when
     re-introduced) AND `viewer/src/styles.css` simultaneously.
     Forces explicit review.
   - **(c)** Document the constraint in [DOMAIN.md](./DOMAIN.md)
     dependency-direction diagram: a new arrow "Layout ⊥ Cursor"
     (orthogonal — no read or write either direction).
   - **(d)** Refactor `useEdgesMemo` / `useNodesMemo` so that
     transient runtime state (e.g., the 3 ghost edges that polluted
     the Foundation canvas after auto-layout testing) cannot
     persist into a fresh hover session.
4. **Pin the constraint.** Whatever option(s) land, add a
   `D-YYYY-MM-DD-X` entry to [DECISIONS.md](./DECISIONS.md) and
   update [DOMAIN.md](./DOMAIN.md) so the structural rule is
   discoverable at session start (auto-surfaced by the SessionStart
   hook).
5. **Regression test.** Add a test that asserts the constraint at a
   level lower than human review (e.g., a Vitest test that fails if
   `autoLayout.ts` imports from `styles.css`-related modules; or a
   pre-commit shell check).
6. **Plan filing.** If the fix is non-trivial, file a plan under
   `~/.claude/plans/<slug>.md` and step through it
   commit-by-commit per Plot CLAUDE.md Gate 4.

#### What this review does NOT do

- Does not re-implement auto-layout. (D-2026-05-10-G removed it;
  re-introduction needs its own decision id.)
- Does not change the v0.14.2 cursor decision (D-2026-05-11-A —
  pure RF default). The review is structural, not visual.

#### Done criteria

The review is complete when:
- The coupling map exists and is committed under
  `plot/docs/ARCHITECTURE.md` or a new file.
- A new `D-YYYY-MM-DD-X` decision id pins the design fix.
- A regression test or pre-commit gate exists that prevents
  recurrence.
- The user confirms ("OK / 됐다 / 좋아요") via Gate 0.

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

(none yet)
