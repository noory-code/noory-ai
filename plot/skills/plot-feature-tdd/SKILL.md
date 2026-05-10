---
name: plot-feature-tdd
description: Implement a Plot feature (UI, MCP tool, schema, layout rule, etc.) end-to-end through the essence-aware TDD pipeline. Anchors every step back to VISION.md's three-phase cycle (Discovery / Retention / Execution) and DOMAIN.md's bounded contexts. Triggers on feature / 기능 추가 / 만들어줘 / add button / implement / 새 / 새로운 / build keywords plus a Plot context.
metadata:
  version: "1.0.0"
  category: dev-process
  type: unit
  style: procedure
  triggers: [feature, "기능 추가", "만들어줘", "추가", add, implement, "새 ", "새로운", build, refactor, redesign, restructure]
  uses: []
---

# plot-feature-tdd — essence-anchored test-first implementation

> **Why this skill exists.** Plot's volatility (six rounds on cursor;
> auto-layout misattributed for weeks) traces to features being placed
> wherever was convenient at the moment. This skill enforces a
> deterministic pipeline: VISION → phase → bounded context → entity
> sketch → SPEC check → test-first → implementation → browser verify
> → SPEC + DECISIONS update → commit. **No step is optional.**

---

## Trigger

Activate when the user asks for a new behaviour, refactor, or
restructure on Plot. Distinguish from bug-fix requests (those use
[`plot-frontend-bug-diagnosis`](../plot-frontend-bug-diagnosis/SKILL.md)
when the bug is UI; otherwise straight implementation per this skill).

If the user request is ambiguous about scope, ask one clarifying
question (≤ 1 line) — usually about which canvas / which kind /
which user persona is affected — then proceed.

---

## The pipeline (10 steps, no skipping)

### Step 1 — Re-read [VISION.md](../../docs/VISION.md) first sentence

Out loud (in your reply): the one-sentence essence. This anchors
everything that follows. If the proposed feature does not serve this
essence, **stop and ask the user** before any further step.

### Step 2 — Identify the VISION phase

Pick exactly one of:
- **Discovery (Foundation)** — surfaces the user's not-yet-articulated essence
- **Retention (anchor + cross-canvas refs)** — keeps essence visible across canvases
- **Planning (Actors / Services)** — designs value-creation machinery under the essence
- **Execution (Service-Detail / MCP tools)** — turns plans into real work
- **AICollaboration (cross-cutting)** — affects how Claude participates

The choice is binding for the rest of the pipeline.

### Step 3 — Look up the bounded context in [DOMAIN.md](../../docs/DOMAIN.md)

Map the phase to a bounded context. State which *Code home* directory
the new code belongs in. If the natural location violates the
dependency-direction rule (lower-numbered contexts must not import
from higher-numbered), stop and **redesign the abstraction** before
writing code — never break the direction to "make it work."

### Step 4 — Sketch the entity / value object touched

In ≤ 5 lines:
- Which entity from DOMAIN.md's "Entities vs value objects" table is
  changing? (Often `SketchNode`, `SketchEdge`, `CanvasDoc`,
  `ProjectDoc`, `AnchorPlacement`.)
- Adding a field, a kind, a method, a derived view, a UI surface?
- If a new entity / VO is needed, name it and show its identity rule
  (entity) or by-value semantics (VO).

### Step 5 — Check [SPEC.md](../../docs/SPEC.md) for existing coverage

- **Already specced** (the spec line matches the proposed behaviour):
  implement to the spec exactly. No more, no less.
- **Specced for a different behaviour** (proposal contradicts SPEC):
  this is a SPEC change request — invoke [Gate 0](../../CLAUDE.md)
  rules. Add a `D-YYYY-MM-DD-X` entry to
  [DECISIONS.md](../../docs/DECISIONS.md) **first**, get user
  approval if not already given, only **then** modify SPEC and
  proceed.
- **Not specced**: this is a new SPEC line. Same Gate 0 path —
  decision id first, SPEC line added, then implementation.

### Step 6 — Write the regression test FIRST (Red)

Add a Vitest unit test (or MCP tool integration test, depending on
the layer) that:
1. Asserts the **post-implementation** behaviour as specced.
2. **Fails** before the implementation lands (Red).

For UI behaviour that JSDOM can't observe (cursor, layout, animation),
add a **Playwright assertion script** to commit alongside the change
(see [`plot-frontend-bug-diagnosis`](../plot-frontend-bug-diagnosis/SKILL.md)
for the probe templates).

For pure logic in `viewer/src/canvases/sketch/*.ts` modules and
`plot_mcp/`, normal unit tests cover it.

### Step 7 — Implement minimally to pass the test (Green)

Write only the code needed to flip the failing test to passing. No
speculative additions. No unrelated polish. The diff is the smallest
possible response to the test.

If the implementation tempts you to grow `SketchCanvas.tsx`,
`SketchInspector.tsx`, `App.tsx`, or `SketchStencil.tsx`, **stop and
read [Gate 2](../../CLAUDE.md)** — those files have a no-growth
ceiling. Put new behaviour in a new file under
`viewer/src/canvases/sketch/` (or other appropriate context dir).

### Step 8 — Browser-verify with the [`plot-verifier`](../../agents/plot-verifier.md) sub-agent

If the change touches UI, invoke the `plot-verifier` agent:
1. It navigates to the affected canvas.
2. Performs the user-visible interaction (click, hover, drag).
3. Captures screenshot + DOM probe.
4. Reports back: "matches spec" or "diverges, here's how."

If the verifier reports a divergence, **return to Step 7** with the
verifier's diagnosis. Do not ship a divergent change.

For MCP / backend-only changes, browser verification is skipped;
`uv run pytest` is the equivalent gate.

### Step 9 — Update SPEC + DECISIONS + CHANGELOG (Gate 0 + Gate 4)

Per [Gate 0](../../CLAUDE.md): user confirmation pins the spec
**immediately**. The new behaviour goes into SPEC.md verbatim, the
`D-YYYY-MM-DD-X` entry is appended to DECISIONS.md, the CHANGELOG
gets a release section. Bump `plugin.json` version (patch for
fixes, minor for features, major for behavioural breaks).

### Step 10 — Commit + push per [Gate 4](../../CLAUDE.md)

Commit message format: `type(plot): vX.Y.Z — short summary`. Body
mirrors the CHANGELOG section. Co-author trailer included. Push to
`origin/main` in the same step.

---

## The non-negotiables

| Rule | Why |
|---|---|
| **Test first.** Red → Green. | Without a failing test, you have no proof the implementation does what was promised. |
| **One context per change.** | If a change spans two bounded contexts, split it into two changes. The "I'll just touch both" pattern is how layering breaks. |
| **No SPEC drift.** Confirmed behaviour goes into SPEC.md *in the same commit cycle* — never deferred. | Drift is the cause of "we keep re-asking the same questions" pain. |
| **Browser-verify all UI changes.** | TypeScript and JSDOM don't observe cursors, layouts, or animation timing. |
| **Never grow SketchCanvas / SketchInspector / App / SketchStencil.** | Per [Gate 2](../../CLAUDE.md). New behaviour → new file in the matching context's directory. |
| **Never auto-emit user-visible state.** | Per [Plot CLAUDE.md rule 7](../../CLAUDE.md). All edges, layouts, labels are user-authored unless explicitly approved. |

---

## Cross-references

- [`VISION.md`](../../docs/VISION.md) — the essence and three phases.
- [`DOMAIN.md`](../../docs/DOMAIN.md) — bounded contexts and code homes.
- [`SPEC.md`](../../docs/SPEC.md) — current behaviour SSOT.
- [`DECISIONS.md`](../../docs/DECISIONS.md) — change-log SSOT.
- [`CLAUDE.md`](../../CLAUDE.md) — operational gates that make this skill enforceable.
- [`agents/plot-verifier.md`](../../agents/plot-verifier.md) — Step 8 sub-agent.
- [`plot-frontend-bug-diagnosis/SKILL.md`](../plot-frontend-bug-diagnosis/SKILL.md) — companion skill for UI bug-fix track.
