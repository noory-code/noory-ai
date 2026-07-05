---
name: flow-retrospective
description: "Retrospective procedure. AI-behavior evaluation (❌ not a work-result summary) + implementation/meta work branching + reference to the interactive 3-step Epic collection."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.1
---

# Retrospective

A document that unifies the retrospective template and the collection procedure.

> ⚠️ A retrospective = **AI-behavior evaluation** (not a work-result summary)

> 🎯 **The purpose of a retrospective = solely the improvement of the AI system (flow / rules / skills / hooks / tools — how the AI plans, executes, verifies, delegates)**. This is the only one. **Product / app features / business / product planning are not retrospective targets and must not go into the retrospective output (Keep/Problem/Try / backlog signals)** — that belongs to that project's product backlog / issue tracker. Every improvement signal that comes out of a retrospective must point to an AI-system asset (if a product signal leaks retrospective→upstream-publish it pollutes the shared board — the source pair of the `flow-upstream-publish` publish-eligibility guard).

## Agent Teams mapping (terminology SSOT)

The flow concepts of this procedure map to Agent Teams components as follows (parity with the `flow` skill "Agent Teams mapping model"):

| Flow concept | Agent Teams mapping |
|---|---|
| Work item (Epic/Story/Action) · state · retrospective entries | shared task list |
| No commit/merge with an empty retrospective | hooks (retrospective enforcement — TaskCompleted gate) |
| Interactive 3-step checkpoints for collect/reflect/archive | plan approval (main ↔ user) + mailbox messaging |

> Retrospective enforcement is reinforced by hooks — regardless of whether the hook blocks, perform this procedure's "no commit with an empty retrospective" gate directly. The interactive 3-step checkpoints must obtain user approval at each step (no auto-progress).

## Scope (gray-zone stated)

| Gray-zone case | Primary | Secondary |
|---------------|---------|-----------|
| Retrospective procedure (collect/reflect/archive 3 steps) | **flow-retrospective** | `flow-retrospective-templates` (template check) |
| Retrospective template (Keep/Problem/Try template, metric table, action items) | `flow-retrospective-templates` | **flow-retrospective** (checking when to write) |

**Anti-patterns**:
- Writing "work organization / result summary" in the retrospective (not AI-behavior evaluation)
- Self-evaluation ("did well", "keep it the same next time")
- Encroaching on `flow-retrospective-templates` responsibility (duplicating template detail in this skill)
- Auto-progressing checkpoints (all 3 steps require user confirmation)
- Simplifying the retrospective template (every section is required)
- Passing with a placeholder ("TODO", "TBD", "write later")

**Decision Heuristics**:
- Work type is implementation work (code change) → implementation-work template
- Work type is rule/skill/Subagent/doc → branch the metric area into meta form
- The metric does not fit the work's nature → state "not applicable" (do not leave blank)
- Priority score = (occurrence count × 10) + severity + cost saving → 🔥/🟠/🟡/🔵

**Output Quality Bar**:
- Keep/Problem/Try are all concrete behaviors/events/action items
- Action-item table: priority / item / target / content
- Retrospective-entry identification scheme (per-Epic serial number + item number)
- 3-step checkpoint output (in interactive-message form)
- Passing the hooks retrospective enforcement (placeholder blocked)

**Sanity Self-Questions**:
- "Is the retrospective an AI-behavior evaluation, or a work-result summary?"
- "Did self-evaluation ('did well') slip in?"
- "Did I delegate the template detail to `flow-retrospective-templates`, or duplicate it in this skill?"
- "Did all 3 checkpoint steps get user confirmation?"
- "Are Keep/Problem/Try/metrics/action items all written?"

---

## Work-type branching (implementation work vs meta/doc work)

The retrospective template **branches by work type**. On entering the wrap-up Step, identify the work type and apply the corresponding template.

| Type | Traits | Metric area |
|------|------|------------|
| **Implementation work** | Code change, feature implementation/fix | Build time, test pass rate, regression count, changed line count |
| **Meta/doc work** | Rule/skill/Subagent/Prompt/doc edits, AI-system-component maintenance | Changed component count, reference-graph breakage, consistency (field-standard application rate), regression impact (Claude behavior) |

**"Not applicable" allowed to be stated**: if the metric does not fit the work's nature, state it as "not applicable". However, **the template's other sections such as Keep/Problem/Try cannot be left blank** (compatible with "no simplifying the retrospective template").

---

## Part 1: Retrospective template (3 Levels)

The per-level retrospective template for Action, Story, Epic. In the wrap-up Step, write the retrospective with the template for that level.

📚 **Template detail**: `flow-retrospective-templates`
- Level 1: Action retrospective (A-NNN.md)
- Level 2: Story retrospective (_story.md)
- Level 3: Epic retrospective (_epic.md)
- For each Level, both templates are provided — the **implementation-work / meta-doc-work variants**

---

## Part 2: Retrospective collection procedure (interactive 3 steps)

On Epic completion, collect all-level retrospectives and reflect them into the system.

> ⚠️ **Interactive skill**: at each Step, always proceed only after user confirmation.

### Preconditions

- Epic complete (all Stories ✅)
- Commit complete

### Step 1: Collect + analyze [Checkpoint 1]

1. Collect all Epic/Story/Action retrospective sections under `.flow/workspace/epic-[name]/`
2. Analyze repeated patterns (2+ times), critical issues, efficiency opportunities
3. Priority: score=(occurrence count×10)+severity+cost saving → 🔥(100+), 🟠(70-99), 🟡(40-69), 🔵(<40)

User confirmation: "Collected [N] retrospectives, derived [M] improvement items. Please confirm."

### Step 2: Identify + reflect retrospective entries [Checkpoint 2]

1. Assign identifiers to the collected improvement items (per-Epic serial number + item number) — record in the `_epic.md` retrospective section (no separate item directory)
2. Select reflection items via `AskUserQuestion` (batches of 3-5)
3. Reflect selected items into skills/rules/docs → `_epic.md` retrospective-section item state ⬜→✅

User confirmation: "[N] items reflected. The remaining [M] are kept in the archive."

### Step 3: Complete + archive [Checkpoint 3]

1. `_epic.md` retrospective section → **integrate directly** into the project archive location (the retrospective is included in the archive — no intermediate summary file)
2. Confirm backlog recording is complete

User confirmation: "Retrospective procedure complete. Shall we proceed to the next stage?"

---

## §RETRO-1-05: R3 (retrospective RT attack) self-verification

> A gate that self-attacks the retrospective body itself from an RT perspective right after writing the retrospective (right before commit). This is the retrospective-side location of the R3 mechanism, and the payload-standard SSOT is `debate-redteam` §R3.

**R3 = AI self-verification** (no external review agent — the retrospective is meta-cognition, so the Flow itself performs it). Right after writing the retrospective, perform the retrospective RT attack along the following 4 axes:

| Attack axis | Check |
|--------|------|
| **Surface Keep** | Is the Keep item verifiable by commit history / deliverables (block groundless self-evaluation) |
| **Post-hoc justification** | Problem avoidance / Try that cannot be executed / items that are all flourish and no substance |
| **Placeholder block (RETRO-1-05)** | `_empty._` / "TODO" / "write later" = 0 — parity with hooks retrospective enforcement |
| **Single-item alternative** | If the Try is a single direction only, consult one alternative |

**Record the result**: state a "R3 self-attack result" item in the retrospective Problem section. On finding a violation (surface Keep / placeholder), reinforce the retrospective body then commit.

> This §RETRO-1-05 is the retrospective-side SSOT anchor of R3. For the full R1/R2/R3 matrix + payload standard see `debate-redteam` §R3; for when R3 is called see `flow-verify-commit` §Step 5.5. The target of the `flow-procedure-action` reverse-verification grep (`R3`/`retrospective RT`).

---

## Part 3: Retrospective → evolution loop (Φ4 self-improvement — accumulate + independent reflection)

> A loop that makes the retrospective not stop at an after-the-fact record but become an **asset that makes the next work better**. But reflection is not auto-coupled to the flow unit (Epic/Story/Action); it happens **independently** (`retro-processing` — human trigger + review gate). The body of the Initiative essence (Φ4 self-improvement / Φ5 retrospective processing). Enforcement is the [[retro-evolution]] rule + `playbooks/retro-processing.md` (this procedure is the SSOT, the rule is the enforcement signal).

### 3-1. Try classification scheme (5 kinds)

Classify each retrospective Try, at writing time, into the following 5 kinds (assign a tag):

| Class | Update target | Signal |
|------|----------|------|
| **Rule candidate** | Procedure enforcement/prohibition (rules/) | Repeated violation / needs a Gate / "must not ~" |
| **Skill candidate** | Procedure/guide body (skills/) | Procedure gap / patterning into the body / "how to ~" |
| **Playbook candidate** | Way of working (playbooks/) | Same pattern ≥3 times → new / application failure ≥2 times → fix (evolution procedure = `playbooks/README` SSOT). **But only universal ways of working** — a specific implementation pattern (e.g. extracting a specific util) is a skill candidate or a project delegation (playbook-generality principle wins) |
| **Memory candidate** | Project-context facts | Project-specific fact / preference / non-obvious decision |
| **Backlog** | Follow-up batch | Cannot reflect immediately / non-blocker Mid·Low |

> **Memory candidate = project delegation (Φ1)**: the plugin provides only the classification category. The actual memory mechanism (storage location/format) is provided by the installed project (plugin non-goal).
> **Playbook candidate = evolution-procedure delegation**: the detailed new/fix criteria are `playbooks/README` (evolution-mechanism SSOT). This table is classification + cross-ref (0 duplication).
> **Ownership routing ([[retro-evolution]] M5)**: rule/skill candidates (plugin-core skills/rules/hooks) = the installing user can only **propose upstream** (cannot modify the installed artifact directly) — this upstream proposal is published by `flow-upstream-publish` as a detailed ticket to the project-designated board (`settings.upstream_board`) (leak prevention) / dogfood (the plugin's own repo) = direct / playbook·memory = project-owned.

### 3-2. Retrospective accumulation stages (3 levels — not reflection)

> Each level only **accumulates/organizes** the retrospective; it does not do asset update (reflection). Reflection is the independent `retro-processing`.

| Level | Retrospective timing | Try handling (accumulation) |
|------|----------|---------|
| **Action retrospective** | A-NNN.md wrap-up | Assign the 5-kind classification tag to the Try |
| **Story retrospective** | _story.md wrap-up | Integrate Action Trys + priority (High/Mid/Low) + next-Story handover table |
| **Epic retrospective** | _epic.md wrap-up | Integrate Action/Story Trys + **on archiving, extract/aggregate `retro.md`** (the input to independent reflection — `flow-archive`). Not asset update — the update is the independent `retro-processing` |

### 3-3. Retrospective accumulation → independent reflection (flow-decoupled)

Retrospective reflection (asset evolution) is **not auto-coupled to entering a flow unit (Epic/Story/Action)**. The retrospective accumulates while working, and reflection happens independently (human trigger + review):

- **Accumulate**: at each work type's retrospective stage, the retrospective piles up in the SSOT (`A-NNN.md`/`_story.md`/`_epic.md`). Teammates go this far — work + retrospective accumulation.
- **Preserve**: on archiving, extract/aggregate the retrospective (`retro.md`, including source metadata) and permanently preserve it as the input to independent reflection (`flow-archive`).
- **Reflect (independent)**: process the piled-up retrospectives with `playbooks/retro-processing.md` (human trigger → repeated-pattern identification → review gate → reflect). Not coupled to Epic/Story wrap-up — the person who triggers is the owner (no role identification needed).

> ⚠️ **Do not confuse — personal-work completeness is separate**: "reflect the improvements of the immediately preceding work into the current work without omission" (a full sweep of impacted targets) is not retrospective *reflection* but the *completeness* discipline of the current work → the `flow-procedure-action` full sweep handles it. It differs from retrospective-based auto-preemptive-reflection (old M2).

### 3-4. TaskCompleted hook linkage

Blocking completion when the retrospective is not written (the "Agent Teams mapping" above — the TaskCompleted gate) = **accumulation guarantee**. The enforcement of independent reflection (no reflection without review) is handled by the `playbooks/retro-processing.md` Hard Gate + the [[retro-evolution]] rule (this procedure cross-refs, no body duplication).

### 3-5. Evolution metrics (Φ4 measurement — analyst)

Metrics that objectively measure "is the context evolving". **3 quantitative + 1 qualitative** (measurability principle). Measured at the independent-reflection (`retro-processing`) point:

| Metric | Type | Measurement method |
|--------|:---:|----------|
| **Try → asset reflection rate** | Quantitative | Of the classified Trys, the ratio actually reflected into an asset (rule/skill/playbook/memory) = updated Try count / total classified Try count. **Measurement point = right after the independent reflection (`retro-processing`) completes** (measuring before reflection is always 0 / prevents circular reference) |
| **Same-mistake repeat frequency** | Quantitative | Count of the same Problem recurring (same-Problem count across Epics — **decrease = evolution**) |
| **Updates per retrospective** | Quantitative | Asset updates per one retrospective = updated asset count / retrospective count |
| **Essence parity** | Qualitative | Whether the update aligns with the project/Initiative essence (value proposition) — decision criteria: aligned / partial / deviated |

> **Measurement point**: at independent-reflection (`retro-processing`) execution (cumulative trend — whether the repeat frequency decreases is the core indicator of evolution). The metric-measurement obligation is in the [[retro-evolution]] rule.

---

## Part 4: Retrospective rigor label (rigor — project custom)

> Express the retrospective rigor as an **abstract label** rather than a raw number (character count), and the project pins its own policy in the `retrospective` section of `.flow/settings.json`. The hook (Rule 2 / Rule 11) reads this label and branches the decision. The `/flow-config-retro` command exclusively handles the user interface.

### §4-1 Label 4-level definition

| Label | Meaning | Hook decision criteria |
|------|------|---------------|
| `none` | Retrospective exempt | Pass (but the `initiative` level cannot be `none`-exempt — §4-4 guard) |
| `minimal` | Placeholder block only | No placeholder pattern (TODO / TBD / write later / after work) + body ≥ 1 line |
| `template` | KPT 3-section body recommended | The hook-compatible decision is KPT 1+ marker+5 chars, or non-placeholder body ≥ 30 chars (§4-5). The writing standard is the KPT 3 sections. |
| `template+rt` | Template + R3 self-attack result stated | `template` hook decision + `R3 self-attack result` section (or a §RETRO-1-05-parity marking). The writing standard is stating the R3 4-axis result. |

### §4-2 4-level × label matrix (settings recommended defaults)

| Level | Recommended default | Application location |
|------|------------|----------|
| `action` | `template` | The `## Retrospective` body check of the in-progress Action (current hook Rule 2 target) |
| `story` | `template` | The `_story.md` Story retrospective section (indirectly forced by the archive check — Rule 11) |
| `epic` | `template+rt` | The `_epic.md` Epic retrospective section + R3 self-attack (strategy evaluation) |
| `initiative` | `template+rt` (cannot be `none`-exempt — §4-4) | The `_initiative.md` value-proposition (Φ) parity evaluation + evolution-trend measurement |

### §4-3 settings.json schema

Add a `retrospective` section to `.flow/settings.json` to customize the per-project retrospective policy:

```json
{
  "retrospective": {
    "levels": {
      "action":     { "rigor": "template" },
      "story":      { "rigor": "template" },
      "epic":       { "rigor": "template+rt" },
      "initiative": { "rigor": "template+rt" }
    }
  }
}
```

**Field definitions**:
- `retrospective.levels.{level}.rigor`: one of the 4 labels (`none` / `minimal` / `template` / `template+rt`). Label meaning = §4-1.
- Levels: `action` / `story` / `epic` / `initiative`, 4 kinds.
- Behavior when absent: apply the §4-5 migration default.

### §4-4 initiative guard (no exemption)

**`initiative.rigor = none` is not allowed.** Even if pinned in settings, the hook ignores it and forces `template+rt` + prints a stderr warning.

**Rationale**: the Initiative retrospective = **value-proposition (Φ) parity evaluation** (not an Epic-retrospective summary — parity with `flow-procedure-initiative` Level 4). Per-Φ achievement + evolution-metric trend measurement is **the very essence** of proving evolution. Exempting it makes the Initiative's reason for existing (value proposition + self-improvement Φ4) disappear.

### §4-5 Migration default

The default label mapping for existing projects where the `retrospective` section is absent in `.flow/settings.json`:

| Level | default | Decision rationale |
|------|---------|----------|
| `action` | `template` | Equivalent to the current hook Rule 2 `check_retro_not_empty` behavior — KPT 1+ marker+5 chars, or non-placeholder body ≥ 30 chars. This equivalence is slightly weaker than the §4-1 `template` definition (KPT 3 sections), but empirically a KPT 1+ marker accompanied by body ≥ 1 line almost always passes — compatibility guaranteed. |
| `story` | `template` | Consistent if the Story retrospective section has a KPT body. The archive check (Rule 11) stays as is. |
| `epic` | `template+rt` | State the R3 self-attack result in the body right after the retrospective — parity with the current `§RETRO-1-05`. |
| `initiative` | `template+rt` | §4-4 guard. `none` not allowed; `template+rt` suits the value-proposition parity evaluation. |

**Compatibility-safety guarantee**: this default maps so that the hook behavior of a settings-unset project **stays identical to the current one**. Unless the user explicitly states a `retrospective` section in `.flow/settings.json`, there is no change to the retrospective enforcement rigor.

### §4-6 Per-label example retrospectives

Pass/fail examples for each label. (The template itself is `flow-retrospective-templates`' responsibility — see §4-7 responsibility boundary.)

#### Example — `none`

Retrospective exempt — no body needed. (But the `initiative` level cannot be `none`-exempt.)

#### Example — `minimal` pass

```markdown
## Retrospective

This Action proceeded per the procedure.
```

→ 0 placeholder patterns + 1 body line → pass.

#### Example — `minimal` fail

```markdown
## Retrospective

TODO
```

→ Placeholder pattern (`TODO`) detected → fail.

#### Example — `template` pass

```markdown
## Retrospective

### Keep
Measured the impact baseline with a pre-grep → accurate scope

### Problem
Guessed the settings schema and corrected once

### Try
Read first before a schema change (verify-before-assert)
```

→ All 3 KPT markers present + each body ≥ 5 chars → pass.

#### Example — `template` fail

```markdown
## Retrospective

### Keep
Went well

### Problem
None

### Try
Same next time
```

→ Keep ("went well") self-evaluation + body < 5 chars → fail. (Parity with the `flow-retrospective-templates` self-evaluation prohibition.)

#### Example — `template+rt` pass

```markdown
## Retrospective

### Keep
During A-001, wrote §4-3 schema after confirming parity with the settings.json pattern — 0 drift

### Problem
When writing the §4-6 example retrospectives, did not pre-check the template-SSOT (templates) responsibility boundary → found and corrected in R1

### Try
When writing template/example separately, pre-verify the responsibility boundary with the `meta-skill-procedure` Scope table

### R3 self-attack result
- Surface Keep: 0 (Keep body verifiable by deliverables)
- Post-hoc justification: 0
- Placeholder: 0
- Single-item alternative: consulted 1 alternative for the §4-7 cross-ref location (templates Level 1–4 each vs 1 line at the end — adopted 1 line at the end)
```

→ KPT + R3 4-axis result stated → pass.

#### Example — `template+rt` fail

```markdown
## Retrospective

### Keep
Implementation complete

### Problem
None

### Try
Same next time

### R3 self-attack result
None
```

→ Keep self-evaluation + R3 result not stated (`None`) → fail.

### §4-7 Responsibility boundary (templates SSOT separation)

| Responsibility | Location |
|------|------|
| **Label definition + decision criteria + examples** | This SKILL Part 4 (procedure/enforcement-dependent, so co-located with the procedure SSOT) |
| **The retrospective template itself** (Keep/Problem/Try template, metric table, action-item template) | `flow-retrospective-templates` (single template SSOT) |
| **cross-ref** | 1 line in `flow-retrospective-templates`: "per-label example retrospectives: see this SKILL Part 4 §4-6" |

> Avoiding template/example SSOT encroachment: the per-label examples (§4-6) are dependent on the label definition, so they stay in this SKILL. The template (Level 1–4 standard) is templates-single. Both are connected by cross-ref.

### §4-8 Enforcement mechanism (hook Rule 2 / Rule 11)

| Label | Rule 2 (`check_retro_not_empty` Action body) | Rule 11 (`no-finish-without-archive`) |
|------|----------------------------------------------|---------------------------------------|
| `none` | Check exempt (except `initiative`) | `archives/retro-<name>.md` check exempt (except `initiative`) |
| `minimal` | No placeholder + body ≥ 1 line | Archive-existence check (current behavior) |
| `template` | KPT 1+ marker+5 chars, or non-placeholder body ≥ 30 chars (compatibility-safe) | Archive-existence check (current behavior) |
| `template+rt` | `template` + `R3 self-attack result` section | Archive-existence check (current behavior). Checking the R3 content inside the archive is the responsibility of the finish procedure/review, not the hook. |

> The hook-branching implementation is TS-003 (US-003-hook-enforcement) scope. This §4-8 is the SSOT body of the label ↔ hook-behavior mapping — do not overstate the implementation scope.

---

## Writing rules & cautions

**Rules**: Keep (concrete behavior/pattern), Problem (objective fact), Try (executable improvement), action items (target file + priority)
**Forbidden**: self-evaluation ("did well"), ignoring the retrospective template, auto-progressing checkpoints, **no simplifying the retrospective template** — when writing an Action/Story retrospective, always write every section of the template (metrics, Keep, Problem, Try, what was needed, action items). If not applicable, state "none".
**Principle**: retrospective = AI-behavior evaluation (not a work-result summary)
