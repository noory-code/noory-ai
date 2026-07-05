# flow — harness engineering roadmap

> A strategy document derived from harness-engineering materials (OpenAI · Anthropic · MCP · A2A · ACP · Externalization · NLAH · the 6/7-component survey) and
> a **6-round adversarial debate** (Claude critiques ↔ GPT defends/attacks ↔ Copilot converges and re-attacks ↔ Claude re-reviews). See the **Appendix** at the very end for the debate summary and decision rationale.
> Not the behavior SSOT — the behavior SSOT is `rules/` · `skills/` · `hooks/`.

## At a glance (plain-language)

flow is a system that lays down a mountain of *written rules* so the AI does its work systematically. The problem is that
**we have never once verified whether those rules actually help** — so rules only ever keep getting *added*.

The two biggest losses: (1) every task unconditionally front-loads roughly 57K characters of rules (even for a small job) — it costs money, and there are so many
that they end up not being followed. (2) The automatic checkpoint (hook) only looks at whether "a document *exists*", not whether the "result is *good*".

So instead of a grand rebuild, we do **exactly 3 things, in order**:
1. **Measure first** — whether the task succeeded, its cost, how many times it stopped to ask the user, and whether the rules were actually followed. Today the record is 0.
   *Method*: slightly extend the hook that already logs tool calls (triggering rule · task id · time) plus one summary. Not a platform.
2. **Cut the rules** — keep only a small core of the always-loaded ~57K characters, and load the rest only when needed. Pair with (1) for a *before/after comparison*.
3. **Make the checkpoint real** — connect "is there a document" to the project's actual checks (tests, lint) so it looks at *result quality*.

**What we keep** (untouched): the safety guards that prevent hard-to-reverse accidents · the work folder that persists memory across sessions · the practice of keeping rules as easy-to-read
prose. **What we will not do now**: a bigger, more complex overhaul (encode everything as code · an execution engine · a security framework) — preemptively building for a problem we
have never seen is a repeat of the mistake we criticized. **We touch it only when (1) measurement shows it in the data.**

> In one line: don't pile on more — **measure first → cut → make the checkpoint real.**

---

## 0. One-line conclusion

flow is **not pointed in the wrong direction (it is a real natural-language harness, NLAH); it has simply never *measured* its own effect.**
It has *assumed* elaborate procedure equals reliability and built on top of that assumption. The next step is **not a full runtime rewrite but
a "natural-language surface + typed/verifiable seams + measurement-based pruning"** — and its first execution is the 3 stages
**Measurement (T1) → Diet (T3) → Verification (T4)**. (The 8 tracks are a *problem map*, not a parallel execution plan — pushing them in
parallel would repeat the very "elaboration without measurement" that was criticized.)

## 1. Diagnosis

### Core defects (critiques that survived)
- **Absence of a measurement signal (root).** There is no metric or benchmark to measure task outcomes. Evaluation is only retrospective (self-authored prose). → It is impossible to tell what
  works → we only add and never discard.
- **Procedural compliance ≠ reliability (Goodhart).** All 12 hook-enforced rules merely enforce *document existence*; they do not measure work quality.
  Not a "quality gate" but a "traceability gate".
- **Always-on ~57K characters (≈15K tokens) unconditional injection (self-defeating).** Independent of task size. A long context degrades instruction-following,
  so the more rules you add, the lower the compliance rate can go.
- **Mistaking the Markdown control plane for reliable runtime state.** Missing transactions · locks · migration · verification-result-as-state ·
  capability scoping · policy precedence. (This is a latent defect only in *sequential mode*; session resume already exists — it manifests under AT-on
  parallelism.)
- **Hard to falsify or ablate.** Without rule-id · flag · ablation logs, you cannot turn "does this rule work" off and measure it.

### Legitimate guards (preserved — not attack targets)
- **Irreversible-loss guard** (shared-branch protection · preventing work loss): legitimate even without a benchmark (asymmetric loss).
- **Externalized long-term memory** (the `.flow/` work tree): the Memory category of Externalization — proven value. *But the implementation relies on an
  implicit schema, so it is weak* → a hardening target, not a discard target.
- **NLAH form** (editable natural-language policy): the form the materials recommend. The problem is not the form but the *length and ablatability*.
- **Independent RT (Red Team)** (a separate teammate mode): consistent with Generator/Evaluator separation (though model diversity and a structured
  verdict are lacking).

## 2. Principles (the character of the next step)

> **Natural-language surface + typed/verifiable seams + measurement-based pruning.**
> The body is natural language (keeping NLAH's strength); only the *boundaries* are typed, *verification* is executable, and *removal* comes after measurement.

- **Not a runtime rewrite.** Going to a full typed state store / full task runtime / full security platform makes it "a different system"
  and loses NLAH's editability and generality.
- **Self-application.** This roadmap follows the very principles it preaches — *measure first, minimal change, verify the effect*. No 8-track
  parallelism.

## 3. MVP — immediate (3 stages, 80% of the effect at single-maintainer dogfood scale)

| Order | Track | What | Done signal (measured) |
|:--:|------|------|----------------|
| **T1** | **Measurement & Evaluation** *(prerequisite; gates the rest)* | Start from minimal logging: `rule_id` · `rule_hit` · `task_outcome (rework rate · defect leakage)` · `token/time` · `checkpoint_cost` · `user_correction`. Separate AI-behavior metrics from product-outcome metrics. + a natural-language-policy adherence probe (M2). | before data collected + metric schema |
| **T3** | **Context Diet & Policy Loading** *(most urgent)* | Turn always-on rules into a short core + situational on-demand loading. Cache-stable prefix. Policy precedence/conflict. **Pair with T1 for a before/after measurement** (does the diet reduce adherence?). | always-on tokens under target + adherence not degraded |
| **T4** | **Mechanical Quality Gate Adapter** | Connect the document-existence hook to *actual quality checks*: call and record a project's thin `commands[]` config (`test`/`lint`/`analyze`/`required_checks`) and block on it. **Verification results become first-class state** (checks[]). | project command call + result recording works |

## 4. Deferred seams — gated on T1 data (scaled down and delayed, not deleted)

Only narrowly typify/runtime-ify the seams whose repeated failure has been *confirmed by measurement*.

- **Typed Envelope (T5, scaled down)**: not a full typed state store. Schema-validate only the *envelope fields* of Action/Handoff/Check/Review.
  compatibility = **embedded typed frontmatter or a generated view (single SSOT)** — *no separate sidecar
  JSON* (dual-SSOT drift, a `ssot-write-only` violation).
- **Lifecycle Runtime (T6, scaled down — the biggest overreach)**: not a full task runtime. **Only the minimal lock/lease needed to prevent
  AT-on parallel races.** Lower priority if the AT-off default holds.
- **Security & Trust Boundary (T8, scaled down)**: not a full security platform. Start with **separating the trusted-policy / untrusted-task
  channels + a hook health check (fail-closed)**. (prompt injection — trigger-classify external sources)
- **Risk-based Intensity (T7 → absorbed)**: not a separate large track. Attach it to the T1 metrics + T3 loading as a low/medium/high
  flow profile + `checkpoint_cost` measurement + sandbox-liveness to reduce checkpoints.
- **Catalog Pruning (former T4 → absorbed)**: not an independent track. Remove skills/playbooks based on the T1 usage-instrumentation results.
- **Failure decision policy (M4)**: the decision rule for retry/ask/hold/rule-disable candidates when measurement or verification fails.

## 5. What we will not do (explicit)

- Discarding the work tree (externalized memory) / abandoning the NLAH form / a full typed state store / a full distributed task runtime /
  a full agent security platform / removing the irreversible-loss guard / **pushing 8 tracks in parallel**.

## 6. First-class measurement metrics (established by T1)

Product outcomes (rework rate · defect leakage) · tokens/cost (KV-cache hit rate) · **checkpoint_cost** (number of unnecessary questions · waiting · the urge to
work around) · **natural-language-policy adherence** (rule compliance rate · change after the diet) · verifier result (verification pass/fail).
→ Avoid the "we observe but don't evaluate" trap (89%/52%): observation must always be paired with evaluation.

## 7. References
- Decision rationale (debate summary): the **Appendix** at the very end of this document
- Materials: OpenAI Harness Engineering · Anthropic Building Effective Agents/MCP · Google A2A · IBM ACP ·
  Externalization in LLM Agents · Natural-Language Agent Harnesses · Agent Harness Survey (6/7-component)
- Internal: `docs/ARCHITECTURE.md` · `CONCEPTS.md` · `rules/flow-rules.md`

---

## Appendix — why it was decided this way (debate summary)

> Derived from a 6-round adversarial debate (Claude critiques ↔ GPT defends / 7-component attack ↔ Copilot converging critique ↔ Claude re-reviews). The long transcript was scratch and has been deleted; only the core rationale is preserved here.

**Why only 3 MVPs (no 8-track parallelism)**: pushing 8 tracks at once is itself a repeat of the criticized "elaboration without measurement". At the scale of a single or small-team dogfood, the 3 — Measurement (T1) → Diet (T3) → Verification (T4) — deliver 80% of the effect. Measurement gates the rest.

**Why the non-goals are deferred (T5/T6/T8)**: they are preemptive builds for problems never seen, so only after measurement. The full versions over-correct NLAH's strengths (natural-language editability and generality) — not a typed/runtime rewrite but only a "natural-language surface + verifiable seams". T6 (lifecycle lock) manifests only under AT-on parallelism (not the default), so it is the lowest priority.

**3 items where the critique overstated and retreated (do not re-litigate)**:
- "Unfalsifiable dogma" → overstated. Gate enforcement forbids *runtime bypass*, not *maintainer ablation*. But the absence of ablation tooling (rule flag/log) does make *operational* falsification hard → resolved by T1.
- "Universality forecloses mechanical enforcement at the source" → overstated. Base layer = universal / quality mechanical enforcement = a project-layer adapter, so they coexist → TS-003.
- "All collaboration contracts typed" → overstated. Judgment content is rightly natural language; only the *envelope* (delegate_to/AC/verdict) is typed.

**Preservation decisions that survived the attacks**: irreversible-loss guard · externalized long-term memory (work tree) · independent RT · NLAH form · hook = governance existence.
