---
name: flow-playbook-selection
description: "AI playbook selection mechanism. On entering Plan Mode: Read .flow/settings.json → select a playbook by work kind (fall back to general when unclassified, no fixed default) → user confirmation → record in _epic.md + the override Read procedure. Reference this when deciding which way of working to apply as a work item starts."
user-invocable: false
metadata:
  type: procedure
  version: v1.2.0
---

# AI playbook selection mechanism

The procedure by which the flow manager (main) selects, **on entering Plan Mode**, the playbook to apply to a work item (Epic/Story). The flow SKILL loads this guide on entering the Planning Phase.

> **Essence**: after the general planner is installed, it grasps the **kind** of the work (feature/bug/refactoring/docs, etc.) and selects the way of working (playbook) that fits. The selection result is temporary (per Epic), so it is recorded in `_epic.md` (not in the permanent setting `.flow/settings.json`).

## The 4 selection steps (on entering Plan Mode)

1. **Read settings.json** — **explicitly Read** `.flow/settings.json` (auto-loading impossible — `.flow/` is not auto-injected into context). Grasp the active `playbooks[]`
2. **Select the playbook (deliverable first signal → boundary cross-check)** — do not guess by name; judge in two steps:
   - **2a. Deliverable kind / target path first signal** — first look at **what the work touches** (which kind of deliverable / which path). The deliverable kind — code logic / plugin-or-tool asset / docs / infra-or-build / external-library evaluation, etc. — is the first signal of the work type. (E.g. fixing a plugin/AI-tool asset path → that asset-development type; pure docs → the docs type — the path/deliverable is a stronger signal than the name.)
   - **2b. Candidate boundary cross-check (mandatory)** — after narrowing the candidate by the first signal, **actually Read that candidate's `## Applies to` and its `Not suitable (→ X)` boundary and cross-check it against the work**. The `→ X` routing in `Not suitable` is the disambiguator that points to the exact candidate (you must read it for it to work). Do not skip it by name/intuition.
   - If it fits nowhere, use **`general`** (general fallback). ⚠️ No fixed `default` — judge per work by deliverable/boundary (no fixed value / no forced name-guessing).
3. **User confirmation** — with the work's nature as the basis, **a single recommendation + rationale + one alternative for consultation** (parity with `decision-criteria-first` MN3 — no forced option enumeration; since the criteria are already clear from settings and work nature, the AI recommends and the user confirms) → plan approval
4. **Record in `_epic.md`** — record the confirmed playbook in the `_epic.md` `**playbook**` field by work-type name (e.g. `refactor`)

## Selection UX (conversation flow — Clear Feedback)

> How to conduct step 3 (user confirmation) in conversation. **Same tone** as `/flow-config` / persona writing: AI actively recommends → the person confirms (Don't Make Me Think — the person need not know the playbook names/differences).

The AI reads settings + the work's nature and presents **recommendation + rationale + alternative** at once (no offloading the burden onto the person via option enumeration):

> "By its nature this work I recommend **[playbook]** — rationale: [why this fits].
> (Alternative: **[Y]** — [when it's better]. If the work kind is ambiguous, the general `general` is also possible.)
> Shall we go with this?"

- The person only **confirms/changes** (Don't Make Me Think) — the AI explains the difference between playbooks with rationale and the person judges.
- **Clear Feedback**: after confirmation, state explicitly "→ recorded `[method]` in `_epic.md`".
- ⚠️ **purpose-anchoring parity**: when the recommendation is clearly derivable from the work nature + settings, **a single recommendation (+ one alternative)** — no forced option enumeration (`decision-criteria-first` MN3). Only genuine ambiguity that cannot be derived goes to the person.

## override Read procedure (step 3 — load the selected playbook body)

After confirming the playbook in the 4 steps, when loading its body:

1. **Read settings.json** → confirm the active playbook (reuse step 1 above)
2. **Check whether an override exists** — check `.flow/playbooks/{playbook}.md` via Glob/Read
   - **Exists** → use the project override (name collision = project wins)
   - **Absent** → use the plugin default `playbooks/{playbook}.md`
   > ⚠️ **Ground-truth inspect the plugin default first (`verify-before-assert` parity)**: judge active/path by the **actual directory/file existence** (`ls`/Glob), not by stale comments / path strings. **The existence of the plugin default playbook path is normal** (the normal state of no override), not a defect — do not mistake the absence of a plugin default for a defect, or declare a stale comment to be the current standard.
3. **Load context** → Read the selected playbook → apply the Action flow per its procedure (Step/AC/Hard Gate/feedback loop)

> Catalog (`playbooks.json`) ⊇ active (`settings.json playbooks[]`) ⊇ selected (`_epic.md playbook`). The `playbooks[]` in settings must be a subset of the catalog.
>
> **Subset verification (in step 2)**: cross-check that every `playbooks[]` item in settings is present in the `playbooks.json` catalog. If an active playbook is not in the catalog → report to the user (expand the catalog or correct settings). **But project-derived (override) playbooks are outside the catalog, so they are a subset exception**.

## Explicit user bypass

Bypassing the selection procedure only on explicit user expression (skip / move on / bypass / skip it). No AI-self-judgment bypass (`gate-enforcement-default-on` parity).

## Verification

- A record of an explicit settings.json Read call exists (a `.flow/settings.json` Read in the conversation/tool log)
- Deliverable first signal + boundary cross-check: traces that the candidate was narrowed by the work's deliverable kind / target path, and that candidate's `Applies to`/`Not suitable` were Read and cross-checked (no name-only selection — 2a·2b)
- Playbook recorded in `_epic.md`: `grep "\*\*playbook\*\*" _epic.md` → a method-name hit
- Selected playbook body loaded: confirm existence of one of the override path `ls .flow/playbooks/{method}.md` or the plugin default `ls playbooks/{method}.md`
- Subset parity: settings `playbooks[]` ⊆ `playbooks.json` catalog (grep cross-check, override exception)
