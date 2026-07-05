# Purpose Anchoring

A gate that, before asking the user for a decision, **first checks whether the answer can be derived from the ultimate purpose of the work**. Independent of work type, language, and framework. Enforced by default (`gate-enforcement-default-on`) — bypass only via the standard expression.

> **Position**: the detailed procedure for **(c) ambiguous application**, one of the 4 distinctions made before a `decision-criteria-first` question (the 4-distinction entry point = `decision-criteria-first`; this rule = the 3-step gate of that (c) branch). Owned by the plugin itself (does not depend on the user's personal instructions).

Why: the purpose sits at the top of the work-item hierarchy, the actual work at the bottom — as scale grows the distance widens and the AI escalates questions whose answers are derivable from the top-level purpose + lower-level documents. A behavioral rule alone is forgotten at scale, so it is enforced as a gate.

## Gate: 3 steps before escalation (asking the user) (mandatory)

1. **Read the top-level SSOT** — Read the `**ultimate purpose**` of the entry-scale top-level node (`_initiative.md`/`_epic.md`/`_story.md`). If it explicitly references a parent, follow only one level up; if the entry scale is itself the top, stop there. **Do not invent a nonexistent parent.**
2. **Attempt to derive the answer** — from the ultimate purpose + the lower-level SSOT (`_epic`/`_story`/`A-NNN.md`) and rules.
3. **Ask only when derivation is impossible** — if the answer follows from the essence, proceed without asking + **report in one line what was decided and on what basis**.

Listing options or asking a question **without exploring the essence first is itself a violation**.

## When a question is justified (escalation permitted)

Even after exploring the essence: no basis anywhere in the ultimate purpose, SSOT, or rules (genuinely undefined) / user value judgment or preference needed / a decision that is hard to reverse or has large external impact (`no-shared-branch-merge`·`subagent-deployment-timing` (d)) / risky assumption whose cost is high if wrong.

| Case | Verdict |
|---|---|
| Purpose says "unify into a single entry point"; AI asks "option A or B?" though A follows from it | ❌ Violation — derivable, yet escalated |
| Report "purpose = single entry point → deciding option A (one-line rationale)" and proceed; user intervenes only on objection | ✅ Application |
| Value judgment with no basis in purpose/SSOT (e.g. open a paid feature for free?) | ✅ Legitimate question |

## On entering work: external source → confirm purpose → plan

Work that comes in from an external source (issue tracker / messenger / external request) must, **before planning/implementation**, first check the external source to grasp the actual request and confirm the ultimate purpose — confirming the purpose late means rewriting the plan multiple times. Procedure detail: `flow-trigger-classify` (reading/classifying external sources) + `flow-scale-judgment` §confirm ultimate purpose. **Do not start implementation (write tools) with the purpose unconfirmed** — purpose confirmation is a preceding gate (consistent with `no-write-without-plan`·`no-node-without-purpose`). Those two are on-demand skills, so this always-on gate is the standing signal that keeps them from being skipped at entry; it does not duplicate the procedure.

**Direction/scope-setting work** (deciding rules/structure/scope), in addition to purpose confirmation: ① **confirm intent first with one concrete example** (do not start broadly on abstract agreement alone) ② **start from the smallest unit** and expand after verification (no full application up front) — prevents rewrites.

## Pre-judging work attribution — do not anchor unrelated work to the active Epic

Even when there is an active Epic/Story, **first judge whether the incoming work belongs to it**. If unrelated, scope it as **independent work** and newly anchor its own top-level purpose via `flow-scale-judgment` §confirm ultimate purpose (do not inherit the active Epic's purpose). The gate then operates on that independent unit.

- Counterpart of "do not invent a nonexistent parent" = **"do not attach to the wrong parent (an unrelated active Epic)"** — that makes the essence exploration spin uselessly.
- **Not a gate exemption** — keep the gate, but run it on the correct premise (the purpose of that work itself).

## Application timing

- Before composing questions at the Alignment/Assumption Gate of every Planning Phase
- When a decision branch arises during Action execution
- When the urge to "ask the user" arises during retrospective/issue handling

## Boundaries (do not confuse)

- **`decision-criteria-first`** — complementary, the two mechanisms of the flow essence (dynamic derivation, not static criteria): `decision-criteria-first` = "discern before asking" (design: what is missing/ambiguous/conflicting when stuck); this rule = "purpose derivation" (runtime: when criteria exist, re-derive from the top-level purpose).
- **`no-auto-proceed`** — no conflict: this rule eliminates unnecessary questions by deriving from purpose / no-auto-proceed preserves checkpoints (no automatic advancement after completion). Both hold — plan-approval and major-decision checkpoints stay.
- **`no-node-without-purpose`** (hook R9) — **precondition**: it injects/enforces the purpose into the node at design time (write); this rule reads and derives from it at runtime. If a node lacks a purpose, this rule has no source and is neutralized.
- Purpose-field source: `flow-scale-judgment` §ultimate-purpose interview + the per-level `**ultimate purpose**` templates in `flow-procedure-initiative`/`-epic`/`-story`/`-action`.
