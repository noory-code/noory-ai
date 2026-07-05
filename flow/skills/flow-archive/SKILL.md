---
name: flow-archive
description: "Archiving procedure. Extracts and consolidates the retrospectives of a completed entry-scale unit (Initiative/Epic/Story) into (retro-{unit-name}.md — one per unit) and preserves it in git — the input to independent apply (retro-processing). + workspace/archives distinction + reference to the 2-stage user checkpoint."
user-invocable: false
metadata:
  type: procedure
  version: v2.0.1
---

# Archiving procedure (retrospective extraction/consolidation — one flat `retro-{name}.md` per entry scale)

A procedure the flow manager loads in the `archive` Phase. After a **top-level flow unit (entry scale — Initiative/Epic/Story)** completes, it **extracts and consolidates the retrospectives** of that unit's tree and preserves them permanently (git).

The work itself (code/doc changes) already lives permanently in the repo files, git history, and PR. So archives are not a wholesale copy-paste of the completed work but **a retrospective set (`retro-{unit-name}.md`) that is the input to independent apply (`retro-processing`)**.

> ⚠️ **Interactive skill**: user confirmation is required at each Step.
> 🔒 **PR-precondition hook enforced (`no-finish-without-archive`, Rule 11)**: if the `.flow/archives/retro-{workspace directory name}.md` for a completed (✅) entry-scale unit is missing, a PreToolUse hook **blocks** `gh pr create` and merges into a shared branch. That is, archive (retrospective extraction + commit) must be done **before the PR**.

## Position in the retrospective lifecycle (② extraction/consolidation)

Of [[retro-evolution]]'s 3 retrospective stages, this handles **② extraction/consolidation/preservation**:
- **① Accumulation**: accumulated in the `## Retrospective` section of `_epic`/`_story`/`A-NNN` as work proceeds (each work type's retrospective stage)
- **② Extraction/consolidation/preservation (this procedure)**: extract the retrospectives of the completed entry-scale unit into a single `retro-{unit-name}.md` file (flat) + git commit
- **③ Apply (independent)**: process the `retro-*.md` files with `playbooks/retro-processing.md` (human trigger + review), then delete the applied files (empty the queue)

## workspace / archives distinction (SSOT)

| | Location | git | Content |
|---|------|-----|------|
| **workspace** | `.flow/workspace/` | **gitignore (volatile)** | in-progress work SSOT (`_epic`/`_story`/`A-NNN`) |
| **archives** | `.flow/archives/` | **tracked (committed)** | completed-unit retrospectives (`retro-{name}.md` flat, no folder) — the unapplied-retrospective queue |

> Because the work itself lives in the repo/git/PR, archives preserve **only the retrospectives**, not a wholesale copy-paste of the work documents.

## Retrospective unit — one `retro-{name}.md` per entry scale, flat (SSOT)

The retrospective file is **one per top-level unit (entry scale) that started the work**. Place `retro-{unit-name}.md` directly under `archives/` **flat, without a folder** — when several people run in parallel, each work has a unique filename so there is no collision.

| Starting unit (entry scale) | Retrospective file (flat — no folder) | Consolidation scope |
|---|---|---|
| Started as **Initiative** | `archives/retro-initiative-[name].md` **(one)** | that Initiative + retrospectives of **all its Epics/Stories/Actions** |
| **Epic** started independently | `archives/retro-epic-[name].md` **(one)** | that Epic + its Story/Action retrospectives |
| **Story** started independently | `archives/retro-story-[name].md` **(one)** | that Story + its Action retrospectives |

> Key: **do not create a folder** — `retro-{unit-name}.md` flat directly under `archives/`. `[name]` = the entry-scale unit name (including the initiative-/epic-/story- prefix, e.g. `retro-epic-foo.md`).
> **`archives/` = the unapplied-retrospective queue**: after independent `retro-processing` improves and applies to main, **delete** that `retro-*.md` (empty the queue). So a `retro-*.md` remaining in archives = a not-yet-applied retrospective. (Work started as an Initiative is not split per sub-unit but consolidated into one — consistent with `flow-scale-judgment` entry scale.)

## Preconditions

- The entry-scale unit (Initiative/Epic/Story) is complete (everything below in the tree is ✅)
- Retrospectives complete (the unit tree's retrospective sections + each sub-node's retrospective)

## Procedure

### Step 1: Extract/consolidate retrospectives → `retro-{unit-name}.md` + git commit [checkpoint 1]

1. Scan `workspace/[name]/` (the entry-scale unit tree) → extract the `## Retrospective` (Keep/Problem/Try) sections of every `_initiative.md`/`_epic.md`/`_story.md`/`A-NNN.md`.
   - **Filename computation self-check (common to all tools)**: `[name]` is the directory basename directly under `.flow/workspace/` **itself**. Do not strip or guess the `initiative-`/`epic-`/`story-` prefix.
   - **Rule 11 contract**: the hook's `completed_unarchived()` judgment also looks at `.flow/archives/retro-[name].md`. Both Claude Code (`Bash`) and VS Code Copilot (`run_in_terminal`) use the same contract.
   - e.g. `workspace/story-agent-teams-model/` → `archives/retro-story-agent-teams-model.md` (O), `archives/retro-agent-teams-model.md` (X — `story-` missing).
2. Create `archives/retro-[name].md` **(one)** — **consolidate the extracted retrospectives together with source metadata**:
   - Format: for each retrospective, **source** (node ID: `A-NNN`/`US-NNN`/`epic`, date) + Keep/Problem/Try + the **Try 5-kind classification tag** (rule/skill/playbook/memory/backlog)
   - Consistent with the input format of `retro-processing` procedure ① (collect the retrospective set — source list)
3. **Verify before git commit**: confirm that `.flow/archives/retro-[name].md` actually exists. Even if a `retro-*.md` with a different name exists, do not accept it as this unit's archive.
4. **git commit**: `git add .flow/archives/retro-[name].md && git commit -m "chore(...): archive [name] retrospective"`

> Does not copy-paste the entire completed work (`_epic`/`_story`/`A-NNN`) — the work itself is in git/PR. archives = retrospective consolidation only.
> To the user: "Retrospective extraction/consolidation complete (`retro-{unit-name}.md`, [N] node retrospectives). Committed to git. Please review."

### Step 2: Clean up workspace [checkpoint 2]

1. Check: `retro-{unit-name}.md` git-tracking (commit) complete.
2. User choice:
   - **Keep**: keep `workspace/[name]/` (for reference — but gitignored, so volatile)
   - **Delete**: `rm -rf .flow/workspace/[name]/` (the retrospectives are already preserved permanently as `retro-{unit-name}.md`)

> To the user: "Keep or delete the workspace? (the retrospectives are preserved permanently as `retro-{unit-name}.md`)"

## Outputs

| Item | Location | git |
|------|------|-----|
| Consolidated entry-scale unit retrospective | `.flow/archives/retro-[name].md` | **tracked (committed)** |
| Work content (code/docs) | repo files / PR | already tracked |
| workspace original | if kept, `.flow/workspace/[name]/` | gitignore (volatile) |

> Existing wholesale-copy-paste archives (old-model outputs) are kept as-is — not migrated. The `retro-{unit-name}.md` approach applies from new Epics onward.
