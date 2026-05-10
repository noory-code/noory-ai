# CLAUDE.md — Plot operational guide

> **Audience:** Claude Code (or any assistant) working inside `plot/`.
>
> **Relationship to other CLAUDE.md files:**
> - `~/.claude/CLAUDE.md` — global *principles* (SOLID, Clean
>   Architecture, "추측 금지", "임시 통과 금지", TDD, …). Theory.
> - `noory-ai/CLAUDE.md` — monorepo *rules* (500-line split, atomic
>   commits, plugin change rule, AI-First Docs banned phrases, …).
>   Theory + monorepo conventions.
> - **This file** — Plot-local *practical triggers, checklists, and
>   commands*. The other two files tell you *what* to value; this one
>   tells you *exactly what to do, when*. When this file disagrees with
>   the others, this file is wrong — fix this file, not the others.
>
> **Pairs with:**
> - [`docs/SPEC.md`](./docs/SPEC.md) — what Plot should *do*.
> - [`docs/DECISIONS.md`](./docs/DECISIONS.md) — *why* it does what it
>   does, and what was tried and rejected.
> - [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — what shape the
>   code is in and how to fix it.
> - [`docs/CONCEPTS.md`](./docs/CONCEPTS.md) — data model.
> - [`docs/CURSOR.md`](./docs/CURSOR.md) — canvas cursor SSOT
>   (RF defaults + the one Tailwind cancellation rule).
> - [`docs/PHILOSOPHY.md`](./docs/PHILOSOPHY.md) — value-flow / two-layer
>   thesis.
> - [`docs/ROADMAP.md`](./docs/ROADMAP.md) — release order.

---

## Session start — read these first

1. `plot/docs/DECISIONS.md` — last 5 entries. What was just decided,
   what was rolled back.
2. `plot/docs/SPEC.md` — only the canvas you're about to touch.
3. `plot/CHANGELOG.md` — last 1–2 release entries.

If the user's first message references a behaviour you don't recall,
re-read the relevant SPEC section *before* answering. **Never answer a
behaviour question from memory or from code comments alone.**

---

## Pre-action gates

### Gate 1 — Before any UI / behaviour change

```
1. Is the change covered by a SPEC.md line?
   YES → implement what the spec says, no more, no less.
   NO  → STOP. Ask the user. Get explicit "do X" approval.
         Append a D-YYYY-MM-DD-X entry to DECISIONS.md FIRST.
         Then implement.
```

**Banned reasoning:** "the code comment says X is Y, so I'll follow
that." Comments are not spec. They're stale notes from a previous
session that may never have had user approval. See
[D-2026-05-04-B](./docs/DECISIONS.md) for the canonical example: the
"synthetic anchor is read-only" comment caused the assistant to remove
anchor handles, which the user never agreed to.

### Gate 2 — Before editing an oversize file

| File | LOC (2026-05-05) | Rule |
|---|---:|---|
| `viewer/src/canvases/SketchCanvas.tsx` | 1476 | **No new responsibilities.** New behaviour → new file. Existing-file edits must hold or reduce LOC. |
| `viewer/src/canvases/SketchInspector.tsx` | 1422 | Same. |
| `viewer/src/App.tsx` | 791 | Same. |
| `viewer/src/canvases/SketchStencil.tsx` | 523 | Same. |

Per [D-2026-05-05-B](./docs/DECISIONS.md). Bug-fix edits to these
files are allowed only if they don't grow LOC. If a fix needs new
state / new handler / new render block, it goes in a new file or
waits for the split (see [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)).

### Gate 3 — Before claiming "done"

Run the actual viewer:

```bash
cd plot && uv run plot-mcp-http &              # MCP HTTP on 5190
cd plot/viewer && npm run dev                  # Vite on 5193
open "http://localhost:5193/?project_path=$ABSOLUTE_PATH"
```

Then in **the user's real browser** (not just Playwright synthetic
clicks — Playwright bypasses React Flow's d3-zoom event path on
direct `.click()` calls):

- Click the changed element. Does it do the new thing?
- Click around it. Did anything else regress?
- Resize the window. Does layout still fill?

If you can't run a real browser this session, say so explicitly. Do
not say "verified" if you only ran type-check.

### Gate 4 — Before commit (Plot plugin change rule)

Per `noory-ai/CLAUDE.md` plugin rule:

1. Bump `plot/.claude-plugin/plugin.json` `version` (patch / minor).
2. Append a section to `plot/CHANGELOG.md`. **Use the
   Added / Changed / Removed / Fixed structure.** Mention any rolled-back
   attempts honestly — same-day rollbacks belong under "Removed".
3. Append `D-YYYY-MM-DD-X` entries to `DECISIONS.md` for every
   user-visible decision in the change. Mark approval status.
4. Update `SPEC.md` if behaviour changed.
5. `git add` only the files in scope (no `git add -A` — keeps
   unrelated `.claude/settings.json` / debug PNGs out).
6. `git commit` with `type(plot): vX.Y.Z — short summary` first
   line; body uses **Added / Changed / Removed / Fixed** sections
   matching the CHANGELOG; ends with the `Co-Authored-By` line.
7. `git push origin main` in the same step.

---

## During-action rules

### Translate the global principles into Plot triggers

| Global principle | Plot trigger |
|---|---|
| `honesty: 추측 금지` | Don't guess what a function does. `grep` for it. Click the button in the browser. If you can't verify in this session, write "I don't know — verify before next change" in your reply. |
| `behavior: 임시 통과 금지` | No CSS-only fixes for behaviour bugs. Find the component that owns the responsibility, fix the responsibility. (Today's hover bug is the canonical example: CSS tone-down was a bandaid; the real cause is the SketchCanvas god component — see ARCHITECTURE.md.) |
| `behavior: 부분 완료 금지` | If a fix touches 5 places, finish all 5 in the same commit. If you can only do 3, ship none and leave a DECISIONS entry "in progress, blocked by X". |
| `behavior: 요청 대체(silent) 금지` | If the user asked for X but you think Y is better, **say so** and ask. Don't ship Y silently. |
| `thinking: SSOT` | Anchor placement SSOT = `ProjectDoc.anchors`. Project name SSOT = `ProjectDoc.name`. Foundation typed text SSOT = `foundation/{kind}-{id}.md`. Never read these from a second source. |
| `thinking: MECE` | Before adding a node kind, an edge kind, or a new canvas, audit the existing ones. New ≠ overlap with existing. New + existing must cover every case the user described. |
| `design: YAGNI` | If the user didn't ask for it, don't add it. The auto-edges in v0.13.2 violated YAGNI and were rolled back same day. |
| `design: 패턴 2회+ 시 추상화` | First time you write something, leave it. Second time, copy it. Third time, abstract — and only if the abstraction reads cleaner than the duplication. (AHA: Avoid Hasty Abstraction.) |
| `design: SOLID/SRP` | Hard signal: any single file > 500 LOC violates the project rule. SketchCanvas at 1476 violates it 3×. See Gate 2. |
| `architecture: Clean Architecture` | New domain logic (transforms, math, graph queries) goes in pure modules without React imports. UI files import from domain, never the reverse. |
| `ux: User-Centricity` | Test against the user's stated workflow. "User selects node → Inspector appears" is a workflow; verify it end-to-end after every relevant change. |
| `ux: Don't Make Me Think` | If a user has to ask "what is this badge?", you have a UX bug, not a knowledge gap. Either the visual or the spec is missing. |
| `ux: Clear Feedback` | Every action that mutates the doc must show some visual response within ~100 ms (handle hover, drag preview, save indicator). Silent success is a bug. |
| `ux: Visual Hierarchy` | 1 화면 = 1 Primary CTA. The Foundation canvas's primary CTA is "place / edit a Foundation node". Anything that competes (e.g. a giant "Auto layout" button on the toolbar) is wrong. |
| `ux: Accessibility` | The ⚠ badge must hit ≥ 4.5:1 contrast against **every** card colour in the Foundation palette (cream / pastel-orange / pastel-yellow). Verify before changing the badge. |
| `methodology: TDD` | Bug fix without a test = the bug will return. Write the regression test first (Red), make it pass (Green), then refactor. |

### Plot-specific operational rules

1. **Code comments are not spec.** If you read a comment that says
   "X is read-only" or "X is auto-generated", you may *act on it*
   only if SPEC.md confirms. Otherwise treat it as a stale note.
2. **Behaviour decisions belong in DECISIONS.md, not in code comments.**
   Code comments may reference a `D-YYYY-MM-DD-X` id but should not
   contain the decision itself.
3. **Same-day rollbacks are honest.** If you ship a change and the
   user rolls it back the same session, document both — the addition
   in CHANGELOG `Added` / `Changed`, the rollback in `Removed`, and a
   `Rejected` DECISIONS entry. Don't hide the attempt.
4. **Anchor ≠ Service circle.** The synthetic project anchor must be
   visually distinguishable from a yellow Service circle on every
   canvas it appears on. Per
   [SPEC §Anchor](./docs/SPEC.md#anchor-the-centre-node).
5. **All edges are user-drawn.** Never auto-emit edges. If the
   relationship between two nodes is implicit, leave it implicit
   visually — the user will draw the edge if they want it shown.
   Per [SPEC §Edges](./docs/SPEC.md#edges) and
   [D-2026-05-04-A](./docs/DECISIONS.md).
6. **No auto-layout.** Layout encodes user intent.
   Per [SPEC §Auto-layout](./docs/SPEC.md#auto-layout) and
   [D-2026-05-04-D](./docs/DECISIONS.md).
7. **The user controls every line, every position, every colour.**
   The canvas is a co-drawing surface (Plot's PHILOSOPHY.md). Any
   automated change to user-visible state needs explicit consent.

### Commands you'll use often

```bash
# Run viewer + MCP for manual verification
cd plot && uv run plot-mcp-http &
cd plot/viewer && npm run dev

# Type-check viewer
cd plot/viewer && npx tsc --noEmit

# Run viewer tests (note: 2 pre-existing failures from JSDOM
# localStorage + a missing useSketchHistory import; fix these
# before any architecture work — see ARCHITECTURE.md migration order)
cd plot/viewer && npx vitest run

# Run MCP tests
cd plot && uv run pytest

# Type-check MCP
cd plot && uv run mypy plot_mcp/

# Lint
cd plot && uv run ruff check plot_mcp/ tests/
cd plot && uv run ruff format plot_mcp/ tests/
```

---

## Communication rules

1. **Match the user's language.** User asks in Korean → answer in
   Korean. Code, comments, commit messages, docs stay English (per
   noory-ai CLAUDE.md "Language" section).
2. **Brief over verbose.** A clear sentence beats a clear paragraph.
   Don't explain three options when one is clearly right; just ask
   which they want.
3. **Show evidence, not opinion.** "Mission node Inspector shows
   `_md_warnings: ['missing or empty section for typed field
   what_we_do']`" beats "I think the badge means missing fields".
4. **Don't expand scope silently.** If the user says "remove X",
   remove X. If removing X needs Y to also change, *ask first*. Don't
   ship X+Y as one commit unless you've named both.
5. **Acknowledge mistakes plainly.** "I treated a code comment as
   spec; that was wrong" is better than three paragraphs of
   meta-justification.
6. **When the user repeats a frustration, the next reply must address
   the structural cause, not just re-fix the symptom.** Today's "why
   doesn't work accumulate?" was structural; the answer was SPEC +
   DECISIONS + ARCHITECTURE + this file — not another tactical CSS
   change.

---

## Anti-patterns (things this guide is here to stop)

| Anti-pattern | Concrete example seen | Counter |
|---|---|---|
| **Add features that nobody asked for** | v0.13.2 auto-edges between anchor and Foundation children | Gate 1: ask first, get approval, log decision. |
| **Treat code comments as spec** | "synthetic anchor is read-only" → hid anchor handles | "Code comments are not spec" rule. Verify against SPEC.md. |
| **CSS-only fixes for behaviour bugs** | Hover handle tone-down via CSS opacity | "임시 통과 금지" trigger: find the responsible component, fix the responsibility. |
| **Editing god components further** | Adding a 30-line auto-edge block to the 1476-line SketchCanvas | Gate 2: hold or reduce LOC; new responsibilities go in new files. |
| **Claiming "verified" without browser** | Type-check passes ≠ feature works | Gate 3: open the URL, click the thing. |
| **Silently rolling user-visible state** | (Hypothetical) Auto-rebalance Foundation nodes radially | Rule 7: any automated change to user-visible state needs explicit consent. |
| **Burying decisions in commit messages** | (Past pattern) "fix anchor click → no Inspector" with no DECISIONS entry | Gate 4: every user-visible decision = a `D-YYYY-MM-DD-X` entry. |
| **Decorating a node with paint-outside-box CSS** | `outline` + `outline-offset-2` + `ring-1` on the project anchor — clicks on the visible decoration passed through to the pane (see D-2026-05-08-G) | Use `border` (part of border-box, hit-tested). Inset `box-shadow` is OK; outset isn't. Visual extent and click target of an interactive node must coincide. |
| **Adding any cursor / handle / pan override on top of RF defaults** | v0.13.3 → v0.13.5 stacked six rounds of cursor / handle interventions; each fix introduced or revealed the next round's bug, ending with a full reset in v0.13.6 (see D-2026-05-10-C) | Default to React Flow vendor CSS (`reactflow/dist/style.css`, `@reactflow/node-resizer/dist/style.css`). To deviate, open a fresh `D-YYYY-MM-DD-X` entry, get user approval, and add the rule to `styles.css` with an `!important` comment naming the decision id. The override stack itself is the regression engine — never grow it without an audit trail. |

---

## Open meta-rules (not yet enforced; awaiting setup)

- **Session-start readback hook** — automate the "read DECISIONS.md +
  SPEC.md before answering" gate. Today this is a manual rule; a
  SessionStart hook (or skill) should surface the relevant entries
  automatically. See pending decision item.
- **Pre-edit gate hook** — block writes to `SketchCanvas.tsx` /
  `SketchInspector.tsx` / `App.tsx` / `SketchStencil.tsx` unless the
  edit reduces LOC, with a confirmation prompt. Today this is a
  manual rule.
- **Pre-commit gate** — run type-check + viewer tests + a "behaviour
  smoke" set (Foundation renders without auto-edges; anchor remains
  draggable; ⚠ badge contrast ≥ 4.5:1). Today only the first two run.

These will get added when one of them blocks real work; do not build
hooks speculatively (YAGNI).
