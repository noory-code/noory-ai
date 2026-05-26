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
> **Pairs with (read in this order on session start):**
> 1. [`docs/VISION.md`](./docs/VISION.md) — **the essence** + 3-phase cycle. Single source of truth above everything else. Read first, every session.
> 2. [`docs/PRODUCT_SPEC.md`](./docs/PRODUCT_SPEC.md) — **product-level decisions** (platforms, business model, MVP scope, symbol system, canvas inventory, future / out-of-scope). Read second; it is the framing every other doc sits inside.
> 3. [`docs/DOMAIN.md`](./docs/DOMAIN.md) — bounded contexts, ubiquitous language, dependency direction. Use to decide *where* code goes.
> 4. [`docs/SPEC.md`](./docs/SPEC.md) — what Plot should *do* per canvas.
> 5. [`docs/DECISIONS.md`](./docs/DECISIONS.md) — *why* it does what it does, and what was tried and rejected (last 5 entries auto-surfaced by the SessionStart hook).
> 6. [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — what shape the code is in and how to fix it.
> 7. [`docs/CONCEPTS.md`](./docs/CONCEPTS.md) — data model (kinds / fields).
> 8. [`docs/CURSOR.md`](./docs/CURSOR.md) — canvas cursor SSOT.
> 9. [`docs/PHILOSOPHY.md`](./docs/PHILOSOPHY.md) — value-flow / 10 principles.
> 10. [`docs/ROADMAP.md`](./docs/ROADMAP.md) — release order.

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

### Gate -1 — Re-anchor to the essence (every session, before answering anything)

The single rule that keeps every other rule honest. Plot's essence
(from [`docs/VISION.md`](./docs/VISION.md)):

> **Plot 은 본질을 모르는 사람이 본질을 찾고, 그걸 놓치지 않으면서, 그
> 본질 아래에서 서비스를 쉽게 기획·개발할 수 있게 AI 와 협업하는
> 툴이다.**

This sentence + the last 5 DECISIONS entries are auto-surfaced via
`hooks/session_start.py` at SessionStart. **Read both before
formulating the first answer.** When this gate disagrees with any
other rule, this gate wins; fix the other rule.

When the user makes a request, classify it against the three phases
(Discovery / Retention / Execution per VISION.md). If it doesn't fit
any phase or threatens the cycle's reversibility, **stop and ask**
before proceeding.

### Gate 0 — User confirmation pins the spec (immediately, before any other action)

The single most important rule for making work *accumulate* across
sessions. Without this gate, confirmed behaviour evaporates between
sessions and the next session re-asks questions the user already
answered. (See the v0.13.3 → v0.13.6 cursor saga for what happens
when this gate is missing.)

**Trigger — fires the moment the user's message contains any of:**

| 한국어 | 영어 |
|---|---|
| 승인합니다 / 승인 / 그래 / 좋아 / 좋아요 / 네 좋아요 | approved / OK / ship it / looks good |
| 됐다 / 됐어 / 이제 됐다 / 맞아요 / 맞다 | works / right / correct / done |

**Execution order (no skipping, no batching, before any other tool call):**

1. **State the confirmed behaviour in one sentence.** Extract from
   the user's message + the immediately preceding context what,
   precisely, was just approved. Write it as one declarative line —
   the same shape that would go into SPEC.md.
2. **Locate the behaviour in [`docs/SPEC.md`](./docs/SPEC.md).**
   - YES, it exists there → verify the existing text matches the
     confirmed behaviour exactly. If it diverges, edit SPEC.md
     immediately so the spec text and the confirmed behaviour are
     pixel-identical.
   - NO, it does not exist → add a new line / table row / section
     to the appropriate canvas. If the location is genuinely
     unclear, ask the user where it goes — never invent a section.
3. **Append a `D-YYYY-MM-DD-X` entry to [`docs/DECISIONS.md`](./docs/DECISIONS.md).**
   Use the template at the top of that file. Approval line:
   `**Approval:** Accepted by user, YYYY-MM-DD.`
4. **Stage SPEC + DECISIONS into the current commit cycle.** If a
   commit has already shipped before the confirmation arrived,
   open a docs-only follow-up immediately:
   `docs(plot): pin D-YYYY-MM-DD-X to SPEC`. The version bump is
   patch-level when only docs changed.

**Banned shortcuts:**

- *"다음에 정리하겠습니다"* / *"I'll do this later"* — the next
  session does not see this conversation. Not pinning now = never
  pinned. Same severity as `behavior: 부분 완료 → 금지` in the
  global CLAUDE.md.
- *"이미 이번 commit 에 들어갔다고 가정"* — verify by reading the
  staged diff. Don't assume a SPEC line exists because you intended
  to write one.
- *"한 confirmation 으로 여러 동작을 한꺼번에 batch"* — each
  confirmed behaviour gets its own 1-4 cycle. If three things were
  approved in one message, three SPEC updates + three D entries.
- *"Confirmation 의미가 모호하니 그냥 넘어감"* — if the trigger
  fires but you cannot identify the confirmed behaviour, ask
  *"어떤 동작을 승인하신 건지 한 줄로 확인 부탁드립니다"* before
  doing anything else.

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

### Gate 2 — Before editing a file near its LOC budget

Per [D-2026-05-12-F](./docs/DECISIONS.md). The v0.15 structural
reset (D-2026-05-12-B) deleted `SketchInspector.tsx` (Phase 2.10)
and `SketchNode.tsx` (Phase 3.5); the remaining oversize file is
`App.tsx`. Every canvas-internal file has a runtime-enforced LOC
ceiling — see `viewer/tests/structural-guards.test.tsx`.

| File | LOC (2026-05-12) | Ceiling | Rule |
|---|---:|---:|---|
| `viewer/src/App.tsx` | 478 | 485 | v0.27.7 (D-2026-05-27-B) raised 430 → 485 to hoist 9 Canvas / ServiceDetailCanvas prop callbacks out of inline arrows into useCallback. Follow-up: move callbacks into a useAppCallbacks hook to reclaim LOC. |
| `viewer/src/canvases/SketchCanvas.tsx` | 427 | 440 | v0.18.0 Phase 3 (D-2026-05-16-E) raised 420 → 440 to thread the publish handler through to SketchInspectorBindings. **No-growth henceforth** — new responsibilities → new sketch hook or wrapper. |
| `viewer/src/shell/*.tsx` | ≤ 90 | — | App-chrome components (Header / CanvasTabs / HelpCheatsheet / ServiceDetailModal / states). Each owns its slice of chrome JSX; new chrome → new file in `shell/`. |
| `viewer/src/hooks/use*.ts` | varies | — | App-shell hooks (useProject / useCanvasPersist / useProjectSocket / useUrlSync / useAvailableNodes / useAppKeyboard). Per-concern; do not bundle. |
| `viewer/src/canvases/nodes/BaseNode.tsx` | 227 | 250 | Chrome SSOT for all 15 per-kind node renderers. New visual responsibilities → per-kind file. |
| `viewer/src/canvases/inspectors/BaseInspector.tsx` | 256 | 270 | v0.18.0 Phase 3 (D-2026-05-16-E) raised 220 → 270 to absorb the version badge + publish button + confirm-dialog handler. Chrome SSOT for all 15 per-kind inspectors. New chrome → here; new typed-field body → per-kind file. |
| `viewer/src/canvases/{Foundation,Actors,Services,ServiceDetail}Canvas.tsx` | 16-23 | 150 | Props-only thin shells. **Never** put behaviour here — push it into a sketch hook or BaseNode chrome flag. |
| `viewer/src/canvases/nodes/{kind}/index.tsx` × 15 | ≤ 19 | 100 | Per-kind node renderer; wraps `BaseNode` with kind-specific chrome flags + body override. |
| `viewer/src/canvases/inspectors/{kind}/index.tsx` × 15 | ≤ 167 | 250 | Per-kind inspector; renders inside `BaseInspector`'s slot. |
| ~~`viewer/src/canvases/SketchInspector.tsx`~~ | — | absent | **DELETED** in v0.15.0 (Phase 2.10). Re-creating fails `structural-guards.test.tsx`. |
| ~~`viewer/src/canvases/SketchNode.tsx`~~ | — | absent | **DELETED** in v0.15.5 (Phase 3.5). Re-creating fails `structural-guards.test.tsx`. |

**Raising a ceiling** = open a fresh `D-YYYY-MM-DD-X` entry that
either (a) names the new responsibility the file legitimately
absorbed, or (b) accepts a refactor follow-up. **Never** edit the
test ceiling without the decision id.

**Lowering a ceiling** (i.e. enforcing the planned target after a
split) = the same — pin via a decision so the next session knows
what changed.

If a fix to one of these files needs new state / handler / render
block AND grows LOC past the ceiling, it goes in a new file or
waits for the planned split (see
[`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)).

### Gate 3 — Before claiming "done"

**Use the [`plot-verifier`](./agents/plot-verifier.md) sub-agent.**
For any UI change in `viewer/`, invoke `plot-verifier` to navigate
the browser, screenshot the change, and probe the DOM. Do not claim
"done" until the verifier returns **MATCHES SPEC**.

For UI bugs specifically, the [`plot-frontend-bug-diagnosis`](./skills/plot-frontend-bug-diagnosis/SKILL.md)
skill is the upstream procedure (probe → diagnose → fix → re-probe).

For features, the [`plot-feature-tdd`](./skills/plot-feature-tdd/SKILL.md)
skill is the end-to-end pipeline; Step 8 invokes the verifier.

The legacy "manual" path below is kept as a fallback for sessions
where the Playwright MCP is offline:

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

### Debugging UI bugs the user sees but Playwright can't reproduce (D-2026-05-27-A)

When the user reports "노드가 사라짐" / "버튼이 안 눌림" / similar
visual bug and Playwright synthetic events fail to reproduce it (RF's
d3-drag / d3-zoom event paths often reject `dispatchEvent` /
`page.mouse` flows), the bug is in the user's real Chrome process
— not in your Playwright instance. **Do not keep guessing.**

**The two-MCP debug workflow:**

1. **Playwright MCP** — your scratch browser. Use for: synthetic
   probes, automated regression runs, taking before/after screenshots,
   simulating drags that DO work (most do). Cannot observe the user's
   actual Chrome process.

2. **chrome-devtools MCP** — bridges into a real Chrome instance.
   Use for: reading the user's live console messages, evaluating JS
   in their page, inspecting DOM state at the moment of the bug.

**When the user says "지금 사라졌다 / 봤제?"** — do NOT reply "no, I
can't see your browser." That is true but useless. Instead:

```
1. Confirm the user has chrome-devtools attached:
     list_pages → should show their page (not just about:blank)
2. Pull console + DOM immediately:
     list_console_messages({types: ["error", "warn"]})
     evaluate_script(() => /* DOM probe of the suspect element */)
3. Match the captured state against the DIAG logs you planted
   in the code earlier.
```

**Plant DIAG logs proactively when chasing a vanish / state-corruption
bug.** Five high-value points to instrument:
- `handleNodesChange` (SketchCanvas) — incoming changes + before/after node count.
- `applyEdit` (useCanvasPersist) — `console.error` on `next.nodes.length < prev.nodes.length`.
- `useNodesMemo` filter — `console.error` when `out.length === 0 && doc.nodes.length > 0`.
- `handleExternalCanvas` (useStableHandlers) — warn when fresh < cached.
- `useEffect` for fitView — log every run + the values it gates on.

Tag each log `[DIAG vX.Y.Z (D-id)]` so they can be grep-removed before
ship.

**Symptom decoder:**

| User says | Likely diagnostic class | First probe |
|---|---|---|
| "노드가 사라졌다" | (a) doc nodes wiped, OR (b) render filter hides them, OR (c) RF `visibility: hidden` lock, OR (d) viewport off-screen | DOM: `getComputedStyle(node).visibility` + `node.getBoundingClientRect()` vs RF rect |
| "정렬 누르니까 사라졌다" | viewport stayed; new layout off-screen | `viewport.style.transform` before vs after; `rf.fitView` call site |
| "드래그하니까 사라졌다" | RF `useNodesInitialized` re-flipped false; mount-time gate held | console logs of fitView effect runs; check `visibility: hidden` count |
| "확대 후 드래그하니까 사라졌다" | same as above but more obvious because zoomed in | same |

**Never claim a fix without observing it in the user's Chrome via
chrome-devtools MCP.** A Playwright pass that didn't reproduce the bug
proves nothing about whether your fix works for the user.

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
6. **Auto-layout is Foundation-only opt-in.** The
   `FoundationCanvas` wrapper passes `enableAutoLayout={true}` to
   `SketchCanvas`; no other wrapper may. The trigger touches
   `x`/`y` only and lands via the regular `onDocChange` (Cmd+Z
   undoes it). Per [SPEC §Auto-layout](./docs/SPEC.md#auto-layout)
   and [D-2026-05-13-L](./docs/DECISIONS.md). The isolation contract
   is pinned by `viewer/tests/auto-layout-isolation.test.tsx` —
   never opt other wrappers in without a fresh `D-` entry that
   updates that test.
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
| **Bundling a cross-cutting visual change with a feature change in one commit** | v0.13.10 shipped `styles.css` cursor patch + auto-layout button move together. The visual fix turned out to address a latent RF v11 + Tailwind preflight bug that had existed since v0.13.0; the auto-layout feature commit became the cognitive scapegoat for ~6 cursor rounds (see D-2026-05-11-C). | Pre-commit gate (`pre_commit_gate.py::cross_cutting_bundle_check`) blocks. Split into two atomic commits: visual fix first (own D-id), feature second. The static guard `viewer/tests/styles-cursor-baseline.test.tsx` further locks `styles.css` to zero cursor rules. |
| **Hardcoding user-facing UI text in a viewer component** | Plot is a global service (user direction 2026-05-10: *"이건 글로벌 서비스가 될거거든요"*). A hardcoded English or Korean string in a `.tsx` file bypasses the i18n resource bundle and creates per-component sprawl that resists later migration. | Route every user-facing string through `useTranslation()` + `t("namespace.key")`, with the value added to BOTH `viewer/src/i18n/locales/en.json` (primary) and `viewer/src/i18n/locales/ko.json` (Korean). The `i18n-keys-parity.test.tsx` static guard fails the build if locales drift. See D-2026-05-11-D. |
| **Treating raw JSON as a domain entity (no `fromJson` boundary)** | Pre-v0.15 god `SketchNode` interface: UI code read `.what_we_do` directly off the wire shape, no class, no invariant check, no normalisation. The v0.15 reset (D-2026-05-12-B) retired this by introducing 15 per-kind classes in `viewer/src/domain/{Kind}.ts` with `fromJson` / `toJson` / invariant boundaries. Adding a 16th kind without the class is the new shape of the old mistake. | Every new kind lands as a domain class via [`plot-entity-template`](./skills/plot-entity-template/SKILL.md) (14-step walk). The `fromJson` method is the **JSON↔domain boundary** — invariants throw `DomainParseError` there, not in UI validation. Three static guards enforce no regression: `no-god-import.test.tsx` (Phase C, types.ts re-export only + per-kind file exists + `{Kind}Json` exported + `registerKindParser` called), `entity-roundtrip.test.tsx` (Phase D, `fromJson` ∘ `toJson` is identity for every kind), and server-side `test_schema_parity.py` (Pydantic ↔ TS interface drift). See D-2026-05-13-D / E. |

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
