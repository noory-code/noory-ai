---
name: mashbill-design-red-team
description: Adversarial design review for a Novel proposal BEFORE implementation. Reads a SPEC change / DECISIONS entry draft / plan file / verbal proposal with red-team eyes — unstated invariants, failure modes, reversibility, VISION alignment, hidden tradeoffs, premature abstraction vs YAGNI. Triggers on design / 설계 / "review the plan" / "before I implement" / "look at this proposal" / "okay to build?" plus a Novel context. Use BEFORE code is written (use mashbill-code-red-team after).
metadata:
  version: "1.0.0"
  category: review
  type: unit
  style: procedure
  triggers: [design, 설계, "design review", "review the plan", "review the spec", "before I implement", "before I start", "okay to build", "이거 만들어도 돼", "이거 해도 돼", "이 계획", "이 방향", "이거 어때 (계획)", "spec change"]
  uses: []
---

# mashbill-design-red-team — adversarial design review

> **Why this skill exists.** Code reviews catch bad code; they don't
> catch *bad ideas*. Novel's v0.13.2 auto-edges were good code that
> the user rolled back same-day — the *idea* was wrong. The v0.10
> kinds review (D-2026-05-10-E auto-layout) shipped twice and was
> rejected twice. Catching these at the *proposal* stage is
> cheaper than catching them at the diff. **The fix is not "think
> harder"; the fix is "attack the design *before* you build it."**

---

## Trigger

Activate when the user says any of:

- "이거 만들어도 돼? / okay to build this?"
- "이 계획 / 이 방향 어때?" / "review the plan" / "review the spec"
- "before I implement / before I start"
- Or pastes a SPEC line draft, a `D-YYYY-MM-DD-X` entry draft, or
  a plan file path (e.g. `~/.claude/plans/*.md`).

**Do not** activate this skill if the user is asking to review
code already on disk — that's
[`mashbill-code-red-team`](../mashbill-code-red-team/SKILL.md). This skill
assumes the proposal is *paper*, not commits yet.

If the proposal is verbal and informal ("I'm thinking we add a
download button"), restate it as a one-line SPEC draft and ask the
user to confirm before running the attacks — that step alone often
surfaces unclear scope.

---

## The pipeline (8 attacks, run all of them)

Each attack produces zero or more findings. **Find one concrete
example of the failure mode you're naming, not an abstract worry.**
Cite SPEC.md / DECISIONS.md / VISION.md / PRODUCT_SPEC.md / DOMAIN.md
when the proposal collides with existing rules.

### Attack 1 — Re-read VISION.md's one-sentence essence

State it back. Map the proposal to one of the three phases
(Discovery / Retention / Execution) plus the AICollaboration cross-cut.

- The proposal doesn't fit any phase → **off-essence finding**.
  Either redirect to the right artifact (e.g. an Obsidian feature
  belongs in Novel's vault layer, not the React Flow canvas) or
  push back: "this serves a different product."
- The proposal *partially* fits a phase but blurs the boundary
  with another (e.g. adds Execution behaviour to a Discovery
  canvas) → **phase-leakage finding**. Either redesign, or split
  into two proposals.

### Attack 2 — Unstated invariants

For every noun in the proposal, ask "what does this assume?"

- "Service" — does the proposal assume services have parents? Per
  CONCEPTS.md they may be root or child-of-category.
- "Actor" — does the proposal assume one canvas? Per the v0.15
  reset they appear cross-canvas via ``actor_ref``.
- "Anchor" — does the proposal assume editability? Per
  D-2026-05-04-B the anchor handles stay visible AND the anchor
  name mirrors ``ProjectDoc.name`` (not editable from canvas).
- "Edge" — does the proposal assume auto-emission? Per
  D-2026-05-04-A all edges are user-drawn.

Each unstated invariant the proposal violates is a finding. Cite
the DECISIONS entry or SPEC line that pins the invariant.

### Attack 3 — Failure modes

For every interactive behaviour the proposal introduces, ask:

- **What's the worst-case input?** Empty doc, doc with 1 node, doc
  with 10,000 nodes, doc with a kind that doesn't exist yet (next
  release), doc loaded from a stale URL with `?detail=<deleted id>`.
- **What's the worst-case timing?** User clicks during a
  drag-in-progress, during a save, during a WebSocket reconnect,
  during undo.
- **What's the worst-case browser?** Tailwind preflight on a
  zoomed-in React Flow node (the v0.13.10 cursor saga). Safari
  on a touch device. A 4K monitor at 200% DPI.

If the proposal has no answer for at least one of these, it's a
**failure-mode-blind finding**.

### Attack 4 — Reversibility

Every Novel change must answer: **if the user regrets this, how
do they undo it?**

- Does the change write to disk (a `.plot/` file) without a
  matching delete / restore path? → **one-way-write finding**.
- Does the change auto-generate user-visible state (auto-edges,
  auto-layout positions, auto-collapse) that the user can't
  reverse without losing their own edits? → **user-state
  contamination finding** (canonical example: D-2026-05-04-A
  auto-edges, rolled back same-day; D-2026-05-10-G auto-layout,
  rolled back twice).
- Does the change move a file / rename a field / migrate a
  schema without a back-out? → **migration-trap finding**.

### Attack 5 — VISION / PRODUCT_SPEC alignment

Novel's PRODUCT_SPEC.md is the framing every behaviour sits inside.
Re-read the most relevant section before the proposal:

- Adds a new canvas → check PRODUCT_SPEC §canvas inventory.
- Adds a new kind → check PRODUCT_SPEC §future / out-of-scope
  (kinds parked are explicitly out-of-scope; reviving them needs
  a decision).
- Adds a new business surface → check PRODUCT_SPEC §business
  model (Novel is a global service per D-2026-05-11-D; any
  feature that locks to one language / market needs a counter-
  argument).

Each conflict is a **product-framing finding**. The proposal might
still be right and the PRODUCT_SPEC line wrong — but in that case
the spec gets updated *first* (Gate 0), not silently overridden.

### Attack 6 — Over-fit / under-fit (the YAGNI / SoC tension)

- **Over-fit:** the proposal solves exactly one user's exact
  scenario with bespoke code that won't generalize. If it adds a
  new `if (canvasKind === "foundation" && kind === "mission")` —
  that's the smell. Per global CLAUDE.md `design: YAGNI` — if the
  user didn't ask for it, don't add it.
- **Under-fit:** the proposal introduces an abstraction that
  serves only the current use, then breaks when the next
  related feature lands. Per global CLAUDE.md `design: AHA` —
  avoid hasty abstraction; abstract on the *third* repetition,
  not the first.
- **Repetition trigger missed:** the proposal copy-pastes
  existing code for a third time without proposing the
  abstraction. → **abstraction-debt finding**.

### Attack 7 — Hidden tradeoffs

For every benefit the proposal names, ask **what does this make
harder?**

- "Faster save" → does it skip a validation that catches a class
  of bugs?
- "Simpler UI" → does it remove a state indicator the user relies on
  for invariant Y?
- "Better defaults" → does it lock users into a choice they'd
  override if they knew the option existed?

Force the proposal author to name the tradeoff. If they can't, it
likely doesn't have one — meaning it's free, meaning the
hesitation is misplaced. If they can name it, the tradeoff
becomes the discussion.

### Attack 8 — Scope drift

The proposal probably starts as "add X." Read it again and count
the implicit additions:

- Touches more than one bounded context (DOMAIN.md) → **scope
  drift finding**.
- Introduces a flag / setting / preference → ask "what's the
  default and why?" (defaults are SPEC). Flags multiply user
  states the codebase must support; YAGNI applies.
- Mentions "future" use cases as justification → strike them.
  Novel specs only what ships now.

---

## Report format

Output **one section per attack** that fired a finding (skip
attacks where the proposal is clean). Each finding is:

```
### A<n> — <one-line title>

- **Concrete example:** <the input / scenario / line in the proposal
  that exhibits the failure mode>.
- **Rule violated:** <citation to VISION.md / PRODUCT_SPEC.md /
  SPEC.md / DECISIONS.md / CLAUDE.md / DOMAIN.md>.
- **Severity:** Critical / Major / Minor.
  - **Critical** = redesign needed (off-essence, user-state
    contamination, one-way write).
  - **Major** = scope / invariant rewrite before implementation
    (unstated invariant, scope drift, abstraction debt).
  - **Minor** = phrasing / clarification (unclear default, missing
    tradeoff name).
- **Suggested redirect:** <one specific change to the proposal — a
  rephrased SPEC line, an added DECISIONS clause, a scope cut>.
```

Close with a **verdict line**:

- ✅ **READY TO IMPLEMENT** — no findings, or only Minor findings
  the user accepts. The implementation can start.
- 🟡 **REVISE FIRST** — at least one Major finding; the proposal
  text needs a rewrite (and possibly a SPEC / DECISIONS update)
  before code starts.
- 🔴 **REDESIGN** — at least one Critical finding; the proposal
  has a structural flaw. Don't just edit the wording; rethink the
  approach.

---

## Anti-patterns this skill rejects

- **"It depends":** vague gates that punt the decision to
  implementation time. The proposal must commit to a default; the
  default is testable.
- **"In the future we might…":** every "might" is a feature flag
  the codebase has to keep on life-support. Strike it. If the
  future is concrete, file a separate decision.
- **"Users will figure it out":** if the proposal needs a tutorial
  / tooltip / training to be usable, the design is failing
  ``ux: Don't Make Me Think``. Push back.
- **"For consistency with X":** consistency is *one* argument, not
  the *only* argument. If X is also wrong, propagating it doubles
  the debt. Cite the rule X embodies, not X itself.
- **Pile-on:** if the proposal is small (≤ 5 lines of SPEC text)
  and clean, say so and stop. Don't manufacture findings.

---

## Calibration & evolution

After the review fires, watch what the user does:

- User merges the proposal as-is and the implementation lands clean
  → review is calibrated; the proposal was strong.
- User edits the proposal per the findings → next review trusts
  your bar.
- User pushes back on a finding ("that's not what this means") →
  update your model. The user knows Novel better than the skill
  does; ask for the SPEC / DECISIONS clarification you missed.

Per the user's 2026-05-12 direction
(``memory/project_red_team_review_skill.md``):
*"이런 것들이 만들어지면 차차 정형화된 워크플로우로
진화되어야합니다."* The natural evolution path:

1. **Phase 1 (now):** invoked manually via trigger phrases on each
   proposal.
2. **Phase 2 (after several uses):** hook on PR creation that
   asks "should mashbill-design-red-team have run on the underlying
   decision?" (read-only nudge).
3. **Phase 3 (mature):** part of a composed slash command —
   e.g. ``/plot-propose <text>`` that runs design red-team →
   appends approved entry to DECISIONS.md → marks the implementation
   as gated on the verdict.

Don't pre-build Phase 2 / 3. Let usage shape the workflow.
