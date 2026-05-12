---
name: plot-code-red-team
description: Adversarial code review for a Plot branch / commit set / PR. Reads code with red-team eyes — bad-faith input, hidden coupling, rotted comments, stale spec, principle violations against the CLAUDE.md trifecta + Plot's structural guards. Triggers on review / 리뷰 / 코드리뷰 / "review the code" / "check this branch" / "I just shipped" / "before I push" plus a Plot context. Use after code is written (not before — use plot-design-red-team for pre-implementation reviews).
metadata:
  version: "1.0.0"
  category: review
  type: unit
  style: procedure
  triggers: [review, 리뷰, 코드리뷰, "code review", "review my code", "check this", "before I push", "before I commit", red-team, "공격적으로", "비판적으로", "이거 어때", "괜찮을까"]
  uses: []
---

# plot-code-red-team — adversarial code review

> **Why this skill exists.** Reviews that nod along miss the things
> Plot has been bitten by: the god `SketchNode` (1491 LOC, 8 months
> living before v0.15 caught it); cursor overrides stacking through
> six rounds because each fix was reviewed in isolation; the
> `outline` / `ring` decoration that painted outside the click target
> for two weeks before the user noticed by hand. **The fix is not
> "review harder"; the fix is "review *adversarially*."** Read the
> diff as if the person who wrote it is wrong, and prove it or
> disprove it. Then read the surrounding code the same way.

---

## Trigger

Activate when the user says:

- "리뷰해줘 / review this / check this code / 코드 봐줘"
- "이거 PR 올리기 전에" / "before I push" / "before I commit"
- "공격적으로 / 비판적으로 봐줘" / "be tough on this"
- Or volunteers a `git diff` / branch name / commit hash and asks
  for an opinion.

**Do not** activate this skill before implementation — that's
[`plot-design-red-team`](../plot-design-red-team/SKILL.md). This
skill assumes code already exists on disk.

If unclear which scope to review (working tree vs HEAD vs a range),
ask one question (≤ 1 line) and proceed.

---

## The pipeline (9 attacks, run all of them)

Run each attack in order. **Find evidence first, opinion second.**
Every finding cites a file:line. No finding is "I feel" or "I
worry"; every finding is "at viewer/src/X.tsx:42 the code does Y;
that violates rule Z because…"

### Attack 1 — What does the diff actually claim to do?

Read the commit message / PR description (or ask the user for one
if it's a working-tree review). State the **claim** in one
sentence: "this change adds X / fixes Y / refactors Z".

Then read the diff. List **what the diff actually does** as a
mechanical inventory:

- Files touched (count + paths).
- LOC added / removed.
- New exports / removed exports.
- New dependencies / removed dependencies.

**Tension check:** does the inventory match the claim? Specifically:

- Did the claim say "fix bug" but the diff also adds a feature?
  → **Scope creep finding**.
- Did the claim say "refactor" but tests changed beyond names?
  → **Behaviour-change-disguised-as-refactor finding**.
- Did the claim say "small" but ≥ 3 files touched in unrelated
  directories? → **Cross-cutting bundle finding** (the
  ``pre_commit_gate.cross_cutting_bundle_check`` rationale).

### Attack 2 — Bad-faith input

For every new function / handler / parser the diff introduces, ask:

- What if the input is **null / undefined**? Does the code crash or
  silently swallow it?
- What if the input is the **wrong type** (e.g. a number where a
  string was expected from the wire)? Does the runtime check catch
  it, or does TypeScript trust the cast?
- What if the input contains **path traversal** (`../` / `..\\`)?
  The `_details_path_is_safe` validator (plot_mcp/models.py:153)
  is the canonical example of the check the codebase expects;
  anything new that touches a filesystem path must satisfy the
  same shape.
- What if the input contains **secrets / PII**? Does it leak into
  logs, error messages, or the URL bar?

Cite each finding with the file:line and the specific input that
breaks the code.

### Attack 3 — Code-as-spec violations

Plot's [Gate 1](../../plot/CLAUDE.md) is non-negotiable: **comments are
not spec.** For every user-visible behaviour the diff changes,
verify there is a SPEC.md line or a `D-YYYY-MM-DD-X` entry in
DECISIONS.md that approved it.

- The diff changes how the canvas reacts to a click but SPEC.md is
  silent → **un-specced behaviour finding**.
- The diff cites a code comment as its justification ("the comment
  says X is read-only so I removed Y") → **comment-as-spec
  violation finding**. The canonical example is D-2026-05-04-B.
- The diff edits SPEC.md but no DECISIONS entry was filed in the
  same commit → **decision-trail-broken finding**.

### Attack 4 — Hidden coupling

Look for code that *acts like* it's local but reaches across module
boundaries silently:

- A handler that closes over `docRef` / `flowRef` / mutable refs
  declared elsewhere in the same file → **closure-shared state
  finding** (v0.13 SketchCanvas anti-pattern, now mostly cleaned
  up but watch for regressions in the App.tsx hooks).
- A prop name that doesn't match its semantic (`onChange` that
  actually deletes; `availableActors` that includes orphans) →
  **prop-semantic-drift finding**.
- A new file that imports from a higher-numbered bounded context
  than its own (per DOMAIN.md dependency direction) →
  **architecture-direction violation finding**.

### Attack 5 — God dispatch

The v0.15 reset removed god `SketchNode`, god `SketchInspector`,
and god `SketchCanvas`. The static guard in
``viewer/tests/structural-guards.test.tsx`` enforces this on every
commit, but the *new* per-kind file the diff adds can still smuggle
the anti-pattern back:

- New file under `nodes/{kind}/` or `inspectors/{kind}/` that
  references > 1 kind literal → **micro-god finding**. Per-kind
  files narrow with **one** `node.kind !== "X" return null` line
  and reference their own kind only. The shared chrome lives in
  `BaseNode.tsx` / `BaseInspector.tsx`, not in a sibling file.
- New `switch` / chained `if-else` on `node.kind` in any file
  outside `domain/createBlankNode.ts` → **god-dispatch regression
  finding**.

### Attack 6 — Cross-cutting visual bundle

Per D-2026-05-11-C the `pre_commit_gate.cross_cutting_bundle_check`
blocks staging `viewer/src/styles.css` alongside any
non-test viewer / plot_mcp feature file. If the gate isn't
currently triggering on the diff but the diff *changes a visual
SSOT* (cursor, anchor border, focus ring, RF override) alongside a
feature commit:

- **Cognitive scapegoat finding** — the visual change will be
  blamed on the feature change next time someone bisects. Split
  the diff or call it out explicitly.

### Attack 7 — LOC budget creep

The structural-guards.test.tsx file has named ceilings. The
diff might pass the test (still under ceiling) and still be a
red flag:

- A canvas-internal file grew by > 50 LOC in one commit → ask
  "what new responsibility did this file just absorb?" If the
  answer is "none, just adding to an existing feature", that's the
  pattern that turned `SketchCanvas` into a god. Push for a
  per-concern hook extraction (see App.tsx split D-2026-05-12-H
  for the template).
- A per-kind file grew above 100 LOC → its kind-specific logic is
  overflowing. Push for a `inspectors/{kind}/Composition.tsx`-style
  helper (Service's CompositionList is the precedent).

### Attack 8 — Rotted comments

Grep the touched files for:

- `TODO` / `FIXME` / `XXX` / `HACK` — note each. If the diff adds
  one, ask why it isn't a `D-YYYY-MM-DD-X` decision instead.
- Comments that reference removed code paths (e.g. mentioning
  `SketchInspector.tsx` which was deleted in v0.15.0) →
  **stale-comment finding**.
- Comments that say what (`// increment counter`) instead of why
  → push for rewrite or removal.

### Attack 9 — Test coverage

For each behaviour change the diff makes, find the test that
fails without the diff:

- If no such test exists → **regression-bait finding**. Per
  CLAUDE.md "methodology: TDD" — bug fix without a test = the
  bug returns.
- If the test was added but exercises an implementation detail
  (e.g. asserts a Tailwind class name) instead of behaviour →
  **brittle-test finding**.
- If the test seeded data bypasses `createBlankNode` →
  **schema-drift finding** (fixtures must use the domain factory;
  per D-2026-05-12-E sweep).

---

## Report format

Output **one section per attack** that fired a finding (skip attacks
where the diff is clean). Each finding is:

```
### A<n> — <one-line title>

- **Evidence:** <file:line>: <code excerpt or paraphrase>
- **Why it's wrong:** <rule violated, with citation to CLAUDE.md /
  DECISIONS.md entry / SPEC.md line>
- **Severity:** Critical / Major / Minor.
  - **Critical** = ship-blocking (security, data corruption,
    deleted god file resurrection).
  - **Major** = needs a fix before merge (un-specced behaviour,
    god-dispatch regression, cross-cutting bundle).
  - **Minor** = follow-up acceptable (rotted comment, LOC creep
    under ceiling).
- **Suggested fix:** <one specific change, ≤ 3 lines or a clear
  pointer>.
```

Close with a **verdict line**:

- ✅ **MERGE OK** — no findings, or only Minor findings the user
  accepts.
- 🟡 **MERGE WITH FIXES** — at least one Major finding; list the
  blocking findings by id.
- 🔴 **DO NOT MERGE** — at least one Critical finding; explain
  the blocking risk in one sentence.

---

## Anti-patterns this skill rejects

- **Nodding review:** "looks good to me" / "lgtm" with no evidence.
  Always cite a file:line, even for approval.
- **Style nits posing as substance:** "I prefer X over Y" is a
  Minor at best; a Major requires a rule violation, not a
  preference.
- **Speculative concerns:** "what if a future user…" without a
  concrete failure mode is not a finding. Either name the input
  that breaks the code or move on.
- **Pile-on:** if the diff is small (≤ 50 LOC) and clean, say so
  and stop. Don't manufacture findings to justify the review.

---

## Calibration

After the review lands, watch what the user does:

- User merges as-is and the change works → next review is calibrated.
- User asks for fixes you flagged → next review trusts your bar.
- User pushes back on a finding ("that's not what this means") →
  update your model. The user knows Plot better than the skill
  does; bring back the receipts before insisting.

The skill stays useful as long as findings convert to changes. If
five consecutive reviews produce zero findings, the codebase has
internalised the rules — the skill is doing its job by being
obsolete. (Same shape as `reset_complete_check` retiring after
v0.16.0 originally would have.)
