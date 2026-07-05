---
name: flow-completion
description: "Completion-determination conditions. Action/Story/Epic Hard Gate + pre-validation of Action docs before a Story starts + retrospective placeholder-block reference."
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Completion Rules

The completion rules for each level. This is the SSOT for the completion-determination Hard Gates across the 3 levels: Action / Story / Epic.

## Agent Teams mapping

These completion rules run on top of Agent Teams. The mapping of the completion-determination components uses the following as SSOT.

| Completion-determination concept | Agent Teams mapping |
|---|---|
| Completion Hard Gate checklist (doc/retrospective enforcement) | hooks (auto-block) |
| Per-level ✅ status (Action/Story/Epic) | shared task list status |
| Retrospective/AC verification | plan approval |
| Upward integration (Story→Epic · Epic→Initiative) | shared task list parent-task status update |

## Hard Gate: required checks before a Story starts

> The hooks gate (doc enforcement) auto-blocks. Modifying code without an Action doc is blocked.

```
□ Does at least 1 Action doc (A-NNN.md) exist?
□ Does _story.md have an Action-list table?
□ Does the _story.md Action table have a delegate_to column?
□ Is delegate_to mapped for implementation-work Actions?
□ Has the Story branch been created?
```

---

## Hard Gate: required checks before Planning Finalize

```
□ Checking the Epic directory listing, are there no 2+ folders sharing the same US-NNN prefix?
□ If a Story was renamed, has the previous Draft folder been deleted?
□ Do the folder names in the _epic.md Story table correspond 1:1 with the actual folders?
```

---

## Hard Gate: required checks when authoring an Action doc

> Details: see `flow-procedure-action`

```
□ Did you Read the Action-doc authoring procedure (flow-procedure-action)?
□ Is there a delegate_to field? (required for implementation-work Actions)
□ Is there a skill field? (where applicable)
□ Is there an expected-deliverables section?
□ Is there an Action retrospective-handling field? (if `action.rigor=none`, a config note; otherwise, for any label, a retrospective section)
□ Does the Step structure follow the template (setup → implement → wrap-up)?
```

---

## Action completion (required before commit)

```
0. Each Step in the Action doc is updated to - [x] the moment it completes during execution (not batched at wrap-up)
1. Run the Action doc's completion-criteria "verification method" → result ⬜→✅
2. Confirm the project verification command (supplied by the playbook) passes (e.g. generated-artifact sync / build verification)
3. Compare expected vs. actual deliverables
4. Confirm every Step in the Action doc is already ✅
5. Handle the Action doc retrospective (per `retrospective.levels.action.rigor` — if `none`, an omission note; otherwise, for any label, write a retrospective at that rigor)
6. The corresponding Action Step in _story.md → ✅
7. Stage & commit the changes
```

> If the Action includes structural (class/filename) changes, always confirm generated-artifact sync with the project-supplied verification command (playbook).

## Story completion (required before parent-task integration)

```
1. Confirm all Action docs are ✅
2. Run the _story.md AC "verification methods" → [x] once all pass
3. Tidy the _story.md deliverables (expected vs. actual + Scope Out)
4. Write the _story.md retrospective
5. The corresponding Story status in _epic.md → ✅
6. Parent-task integration (Story → Epic)
```

### Story completion Hard Gate

> If not all of the items below are satisfied, parent-task integration is forbidden.

```
□ Does every Action doc satisfy the action retrospective policy? (if `action.rigor=none`, omission is allowed; otherwise, for any label, the retrospective section must not be empty)
□ Has a retrospective section been written in _story.md?
□ Has the Story status in _epic.md been changed to ✅?
□ Has the _story.md AC been updated to [x]?
```

### Upward-integration Hard Gate (Story→Epic · Epic→Initiative)

> Work-unit completion = complete through parent-task integration. If integration is missing, it is incomplete.

> 🔱 **The single SSOT for the integration *gate* (enforcing whether it ran) — across every tier (Story→Epic · Epic→Initiative).** The criterion that enforces "did integration happen" lives in this one gate alone. The integration *strategy* (the per-tier method Squash/`--no-ff` + the single-branch-mode "not applicable" rule) is SSOT in `flow-branch` (§single-branch mode included). **Two-axis split**: completion = gate (what / whether) / branch = strategy (how / method).
>
> Citing sites (do not restate): `flow-procedure-story` (§7-4 · Step 1.5) · `flow-procedure-epic` (integration checkbox) · `flow-procedure-initiative` (Epic→Initiative) · `flow-phases` (the story-finish Squash step) **cite** this gate and carry only the execution method. (The gate criterion being duplicated across 4+ places was the root of "patch one place → miss the rest"; origin: flow-hardening Epic 7 + follow-up retrospective.)

> **Branch-mode branching**: the checks below assume **sub-branch mode**. **In single-branch mode, integration and the integration commit = "not applicable"** (`flow-branch` §single-branch-mode rule #2 — do not look for a merge commit that does not exist. If you look for it, the gate becomes inoperable). The mode = the `**Branch Mode**` field in `_epic.md`/`_initiative.md`.

```
[Sub-branch mode — confirm integration ran]
□ Integration completed (Story→Epic = Squash / Epic→Initiative = --no-ff — the method is per flow-branch)
□ Verifiable from the integration commit history
□ (Story→Epic) Consider deleting the Story branch (keeping it is also OK)

[Single-branch mode — integration = not applicable]
□ Every child of this unit is ✅ + the retrospective is non-empty (reuse the completion Hard Gate — measurable)
□ Commits are verifiable at the boundary via `[epic-N][US-N][A-N]` tags (`git log --oneline | grep`)
□ The `_story.md`/`_epic.md` merge record states "integration = not applicable (single branch)" (no faking a no-op)
```

**Impact if violated**: entering the next unit with the change missing from the parent task → downstream dependencies break.

## Epic completion (required before PR)

> 🎯 **Completion anchor = PR creation (PR creation = end of work)**: once all Stories are ✅, run 1–5 below **in one continuous pass** and finish immediately — do not defer to a separate "epic-finish later" step (deferral is exactly the cause of 🔄 drift). **At the moment the PR is created the workspace is complete (`_epic` header ✅)**, and **merging the PR is a manual user follow-up** — the merge is not detected or automated (the workspace already ended at PR creation; it does not wait for an external merge signal).
>
> ⚠ **Drift defect (to block)**: all Stories ✅ but the `_epic` header is still 🔄 + no PR = **completion un-anchored (drift)**. Finish via this procedure right after the last Story completes. (For the no-PR completion case, see §issue4 below — there, the archive is the closing anchor.)

```
1. Confirm all Stories ✅
2. Write the _epic.md results/retrospective
2.5. _epic.md header **Status** → ✅ (the epic-level completion marker — the target of the hook self_status determination, separate from child Step ✅)
3. Retrospective procedure (interactive, 3 stages)
4. Archive procedure (interactive, 2 stages) — 🔒 **PR must come first** (below)
5. Create the PR (the flow-pr skill)
```

> If the retrospective section is empty, commit/integration/PR is forbidden (the hooks gate auto-blocks).
> 🔒 **archive = PR first (hook-enforced — `no-finish-without-archive`, Rule 11)**: step 4 (archive) must come before step 5 (PR). If a completed (✅) item's retrospective has not been extracted/consolidated into `archives/retro-{unit-name}.md` (flat, no folder) and you attempt `gh pr create` / a shared-branch merge, **the hook blocks it** (prevents skipping the text procedure). The enforced target is only the `retro-{unit-name}.md` extraction — keeping/deleting the workspace is free (`flow-archive`). initiative-finish is the same.
> ⚠️ **Header status marking required** (2.5): on epic/initiative completion, the header must be changed to `**Status**: ✅` for the hook to recognize completion (self_status). If omitted, a completed epic keeps being seen as active — this prevents a recurrence of the status-misjudgment defect. Initiative completion is the same (`_initiative.md` header status ✅).

### Hard Gate: the 4 axes before a completion report (required just before asserting completion)

> Just before emitting a completion report (asserting "complete" to the user), confirm the 4 axes with measurement commands. If even 1 axis fails, completion is un-anchored — reporting is forbidden.

```
□ 1. SSOT status ✅ — `_epic.md`/`_initiative.md` header `**Status**: ✅` (self_status — see 2.5 above)
□ 2. Archive exists — `archives/retro-{unit-name}.md` extraction complete (enforced = the no-finish-without-archive rule R11; do not restate)
□ 3. tracked workspace file count 0 — `git ls-files .flow/workspace | wc -l` = 0 (the workspace must be git-ignored — if tracked, the ignore config is missing. `directory-standard` workspace = ignored)
□ 4. PR/merge target confirmed — for the PR case, is the base of `gh pr create` the intended target / for the no-PR case (issue4), state the reason
```

### No-PR completion cases (issue4)

Not every Epic ends with a PR. The following cases **skip the PR step** — instead of step 5 (create PR), they close via archive:

| Case | Example | Completion method |
|--------|-----|----------|
| **sandbox / PoC only** | virtual-project validation, an experiment directory | confirm deliverables + archive (no PR needed) |
| **docs-only / internal meta** | only work-item docs/retrospective, 0 code produced | retrospective + archive (no PR needed) |
| **mid-Initiative Epic** | a batched PR planned at Initiative wrap-up | Epic integration only; the PR is at Initiative wrap-up |

> **Determination criterion**: "Are this Epic's deliverables code/assets destined for a shared branch?" → If No, it is a no-PR completion. **Blocks ambiguous status determination** — a sandbox/docs Epic is not misjudged as "incomplete, missing PR". The PR timing is stated in the `_epic.md` completion criteria (e.g. "the PR is at Initiative wrap-up").
