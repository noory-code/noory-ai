---
name: flow-procedure-initiative
description: "Initiative creation/execution procedure. The Initiative↔Epic↔Story↔Action 4-layer + _initiative.md value proposition + Epic decomposition + Initiative retrospective reference."
user-invocable: false
metadata:
  type: procedure
  version: v1.1.0
---

# Initiative creation/execution procedure

The creation·execution·retrospective procedure for the **Initiative**, the top-level unit that bundles multiple Epics.

> Initiative = **multiple Epics bundled by a common value proposition** (a large flow that does not finish as a single 5-day+ Epic). The top of the 4 layers.

## Agent Teams mapping

| Flow concept | Agent Teams mapping |
|---|---|
| Initiative/Epic/Story/Action 4-layer work items·status | shared task list (layer dependency) |
| No finishing while the Initiative retrospective is empty | hooks (TaskCompleted gate) |
| Dependency graph — **same model across all layers (D3)**: between Epics / between Actions within a Story (`depends_on`) → topological sort → execution waves | task dependency (addBlockedBy) |

## 4-layer structure

```
Initiative (value proposition — multiple Epics)   ← _initiative.md
  └─ Epic (single goal — multiple Stories)          ← _epic.md
       └─ Story (user story — multiple Actions)      ← _story.md
            └─ Action (single verifiable task)        ← A-NNN.md
```

| Layer | Unit criterion | SSOT |
|------|----------|------|
| **Initiative** | 5 days+ / Epic ≥2 / common value proposition | `_initiative.md` |
| **Epic** | 5 days+ / Story ≥3 / single goal | `_epic.md` |
| **Story** | 1–3 days / Action ≤5 / user story | `_story.md` |
| **Action** | single verifiable task | `A-NNN.md` |

## Preconditions

- The work does not finish as a single Epic (multiple Epics + a common value proposition)
- A value proposition can be defined (the essence that bundles the Epics)

## Procedure

> **Epic→Initiative integration (2 axes — no restatement)**: the *gate* (whether to run the integration) = `flow-completion` § top-level integration Hard Gate (all-layer SSOT). The *strategy* (method·single-mode rule) = `flow-branch` (sub mode = Epic→Initiative `--no-ff` to preserve the Epic structure / single mode = merge is "not applicable," §single-branch mode). Initiative complete → a PR to the base (shared) branch is performed even in single mode (when the user specifies).

### Step 1: Create the Initiative folder + `_initiative.md`

```
{workspace}/initiative-[name]/
├── _initiative.md          # Initiative SSOT
└── epic-N-[name]/_epic.md  # each Epic (flow-procedure-epic)
```

### Step 2: `_initiative.md` required sections

```markdown
# Initiative: [title]

**Status**: ⬜
<!-- initiative-level completion marker (own status). The hook self_status judges completion from this header field only — not polluted by a sub-Epic ✅. Changed to ✅ at initiative-finish -->
**Ultimate purpose**: [= restatement of the value proposition below. Since this is the Initiative entry scale, it is the top of this tree]
<!-- The root of the purpose chain. If the entry scale is Initiative, the value proposition is the ultimate purpose (top). The sub Epic/Story/Action inherit·restate this 1 line without modification (restatement = inheritance without modification) -->
**Branch mode**: sub | single  <!-- Default sub (initiative/·epic/·story/ branching). If everything is meta·small·single-domain, single (one branch with [epic-N][US-N][A-N] tags). flow-branch §single-branch mode. Sub Epics inherit this mode. If single, Epic→Initiative·Story→Epic merges = not applicable -->

## Value Proposition
[the essence this Initiative establishes — not a mere task list]

## Philosophy (Φ1~ΦN)
[the principles that uphold the value proposition]

## Epic decomposition + dependency graph
[Epic 1 → Epic 2 → ... order + dependency relations]

## Completion criteria
[conditions for judging the Initiative complete — per Epic + value-proposition parity]

## Progress status
```

### Step 3: Epic decomposition + dependencies

- Each Epic = created via the `flow-procedure-epic` procedure
- State the inter-Epic dependency graph (Epic N is based on the output of Epic N-1)
- **The dependency model is the same across all layers (D3)**: the same pattern as the inter-Epic dependency graph propagates to the inter-Action `depends_on` within a Story. The main (lead), at any layer, schedules by dependency graph → topological sort → execution wave (independent = concurrent · dependent = next wave). Action-level detail: `flow-procedure-action` (`depends_on` source) + `handoff-protocol` §3.1.1 (lead scheduling decision layer).
- Each Epic selects·records its `**playbook**` (work type) field via `flow-playbook-selection` — if unrecorded, the execution-stage hook blocks (no-work-without-playbook). The Initiative itself does not have a playbook; the work type is picked per sub-Epic unit.

### Step 4: Initiative wrap-up (after all Epics ✅)

1. Write the Initiative retrospective (form below — value-proposition parity evaluation)
2. Measure evolution metrics (`flow-retrospective` Part 3-5 — cumulative trend)
3. Archive (`flow-archive`) + Initiative → PR to the base (shared) branch (`--no-ff`, when the user specifies — `flow-pr` / `flow-branch`)

## Initiative retrospective (value-proposition parity evaluation)

> Not an Epic-retrospective summary but a **per-value-proposition (Φ) achievement evaluation**. Form detail: `flow-retrospective-templates` Level 4.

- Achievement per Φ (was each philosophy realized in the output)
- Initiative metrics (total Stories / RETRO items / updated assets / evolution-metric trend)
- Next evolution direction

## MUST NOT

- ❌ Listing Epics without a value proposition (Initiative abuse)
- ❌ Recording Initiative status outside `_initiative.md`
- ❌ Replacing the Initiative retrospective with an Epic summary
- ❌ Omitting the Epic dependency graph
