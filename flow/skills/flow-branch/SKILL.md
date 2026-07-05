---
name: flow-branch
description: "Branch strategy. Initiative/Epic/Story hierarchical naming + per-level merge (Story→Epic Squash / Epic→Initiative, Initiative→base --no-ff) + shared-branch protection (merge/push only on explicit user request) + commit-format reference."
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Branch strategy

The Flow Manager's reference document for branch creation, merge, and updating. Not tied to work type / language / framework.

## Agent Teams mapping

This guide runs on top of Agent Teams. The core gates of the branch strategy correspond to the following components.

| Branch-strategy concept | Agent Teams mapping |
|---|---|
| Shared-branch merge/push (explicit user gate) | plan approval (main ↔ user) + hooks |
| Story → Epic Squash merge | closing the parent task (shared task list) |

## Shared-branch protection (CRITICAL)

**merge/rebase/push against the project's shared branch (e.g. main/release branch — defined by the project) is executed only on the user's explicit request.**

- ❌ Forbidden: merging into a shared branch on the AI's judgment, auto-proceeding with "the Story is done so let's merge"
- ✅ Allowed: only when the user explicitly instructs directly, e.g. "merge into main", "combine them"
- On Epic/Story completion: **you must ask the user** whether to merge and wait for a response
- Squash Merge may be performed automatically only for **Story branch → Epic branch** (the Epic branch is not a shared branch)
- A simple user affirmation ("yes" / "OK") is not merge consent. Only an explicit expression carrying merge intent counts

## Branch naming

| Level | Branch name | Branch origin | PR/merge target | Merge method |
|------|----------|----------|---------|----------|
| **Initiative** | `initiative/[name]` | shared branch | shared branch | PR (`--no-ff`) |
| **Epic (within Initiative)** | `epic/[name]` | `initiative/[name]` | `initiative/[name]` | PR (`--no-ff`) |
| **Epic (standalone)** | `epic/[name]` | current branch (or shared branch) | shared branch | PR |
| **Story (within Epic)** | `story/[epic-name]/[ID]-[name]` | Epic branch | Epic branch | **Squash** |
| **Story (standalone mode)** | `story/[name]` | current branch (or shared branch) | shared branch or branch origin | PR |
| **Action** | no branch | commit onto the Story branch | - | - |

> ⚠️ Git constraint: if an `epic/foo` branch exists, `epic/foo/bar` cannot be created. `initiative/`·`epic/`·`story/` are distinct prefixes, so they do not collide.
> **Merge-method key**: only Story→Epic is Squash (compressing small Action commits). Epic→Initiative and Initiative→base use `--no-ff` (preserving per-Epic history).
> **The table above assumes sub-branch mode**. In single-branch mode (§ below), Epic/Story/Action branches are not forked and every merge (Story→Epic Squash / Epic→Initiative `--no-ff`) is "not applicable" — the commit `[epic-N][US-N][A-N]` tag stands in for the boundary. `flow-procedure-story` Step 1.5 / §7-4 follow this branch.

## Single-branch mode (Initiative/Epic — T5)

The hierarchy table above assumes **sub-branch mode** (actually forking `epic/`·`story/`). But depending on the nature of the work, **committing everything onto a single branch** can be the right fit. **Choose one of the two at entry** and record it in the SSOT (mixing them causes a described↔practiced divergence where hierarchical merges become no-ops — preventing this is the point).

### Selection criteria

| Signal | Mode |
|------|------|
| All meta / small-scale / **single-domain** (e.g. organizing one plugin's docs/rules) · no parallel isolation needed | **Single branch** — commit everything onto one `initiative/[name]` (or `epic/[name]`) |
| **Multi-domain / large-scale** · parallel Story/Action execution (Agent Teams) · needs isolation of conflicts on the same target | **Sub-branch** — fork `epic/`·`story/` per the hierarchy table |

> The default is **sub-branch** (hierarchy table). Single branch is chosen when the above signals are clear. The borderline is a user confirmation.

### Single-branch mode rules

1. **Boundary tracking via commit tags**: instead of splitting branches, track Epic/Story/Action boundaries with the commit-message `[epic-N][US-N][A-N]` prefix (a substitute for branch forking).
2. **Merge stage = state "not applicable" explicitly (no no-op disguise)**: when single-branch is adopted, the Story→Epic Squash / Epic→Initiative `--no-ff` merges **physically do not happen**. State "merge = not applicable (single branch)" in `_initiative.md`/`_epic.md`. Do not record it as if `--no-ff` was done.
3. **The final shared-branch merge stays the same**: even in single-branch, the PR that goes to the shared branch (main, etc.) at the end is performed normally (user-explicit — parity with shared-branch protection).
4. **Mode switch**: if a multi-domain / parallel need surfaces mid-progress, you may fork into sub-branches from that point (commits already piled onto the single branch keep their boundaries via tags).

## Flow

### Initiative-based flow (multiple Epics — a common value proposition)

```
shared branch
  └── initiative/[name]                          (forked from the shared branch)
        ├── epic/[name-1]                         (forked from initiative)
        │     ├── story/[name-1]/US-001  → Squash → epic/[name-1]
        │     └── PR (--no-ff) → initiative/[name]
        ├── epic/[name-2] → PR (--no-ff) → initiative/[name]
        └── PR (--no-ff) → shared branch
```

> Only Story→Epic is Squash. Epic→Initiative and Initiative→base use `--no-ff` (preserving per-Epic history).

### Epic-based flow

```
shared branch (or current branch)
  └── epic/[name]
        ├── story/[epic-name]/US-001-[name]  → Squash Merge → epic/[name]
        ├── story/[epic-name]/US-002-[name]  → Squash Merge → epic/[name]
        └── PR → shared branch
```

### Story standalone-mode flow

```
shared branch (or current branch)
  └── story/[name]
        ├── Action commits
        └── PR → shared branch (or branch origin)
```

## Creating an Epic branch

```bash
# Default: from the current branch
git checkout -b epic/[name]

# Explicitly from the shared branch
git checkout [shared branch]
git pull origin [shared branch]
git checkout -b epic/[name]
```

## Creating a Story branch (standalone mode)

```bash
# Default: from the current branch
git checkout -b story/[name]

# Explicitly from the shared branch
git checkout [shared branch]
git pull origin [shared branch]
git checkout -b story/[name]
```

## Action commit (standalone mode)

```bash
# Commit after working on the Story branch
git add [target files] .../A-NNN.md
git commit -m "[story-name][action-title] work description"
```

**Commit message format**:
```
[story-name][action-title] work description

Example:
[bugfix-auth][investigate] identify the cause of auth token expiry
[bugfix-auth][fix] add null check
```

## Story standalone mode: retrospective + archiving + PR

```bash
# 1. Write the retrospective
# - Write the _story.md retrospective section (see `../flow-retrospective/SKILL.md` Level 2)

# 2. Archiving
# - Organize the main deliverables
# - Move to the permanent location (if needed)

# 3. Create the PR
# - Use the flow-pr procedure
# - Title: "[story-name] Story done: [summary]"
# - Target the shared branch (or branch origin)

# 4. Delete the Story branch (required — immediately after merge)
git branch -d story/[name]
```

> **Story selection guide**

| Criterion | Story standalone mode | Epic-based |
|------|----------------|----------|
| **Work scale** | 1-3 days, simple | 5+ days, complex |
| **Sub-tasks** | 5 or fewer Actions | 3 or more Stories |
| **Domain** | single | multiple domains |
| **Completion procedure** | retrospective + archiving + PR | same + Epic management |
| **Example** | bug fix, doc update, small feature | large feature, system build |

> 💡 **Standalone mode has completeness similar to an Epic**: retrospective / archiving / PR are all required

## Creating a Story branch (within an Epic)

```bash
git checkout epic/[name]
git pull origin epic/[name]  # reflect the previous Story merge
git checkout -b story/[epic-name]/[ID]-[name]
```

## Action commit

```bash
# Commit after working on the Story branch
git add [target files] .../A-NNN.md
git commit -m "[epic-name][story-ID][action-title] work description"
```

### Commit message format

```
[epic-name][story-title][action-title] work description

Example:
[auth][US-001-token][design] design the token-refresh flow
[auth][US-001-token][implement] implement the refresh-request logic
[auth][US-001-token][test] add expiry-case tests
```

## Story completion: Squash Merge

> **In single-branch mode, this merge command = not applicable** (§ single-branch-mode rules #2). The below assumes sub-branch mode.

```bash
# 1. Move to the Epic branch
git checkout epic/[name]

# 2. Squash Merge
git merge --squash story/[epic-name]/[ID]-[name]

# 3. Commit
git commit -m "[epic-name] [ID]-[name] done: [Story summary]

- [main change 1]
- [main change 2]"

# 4. Delete the Story branch (required)
git branch -d story/[epic-name]/[ID]-[name]
```

> ⚠️ **Do not skip the Squash Merge (assumes sub-branch mode)**: even with no changes, an empty commit Merge is required. (**Single-branch mode is the exception — the merge itself is not applicable**, § single-branch mode)
> ⚠️ **Deleting the Story branch is required**: delete immediately after the Squash Merge. Leaving it accumulates stale branches.

## Epic → Initiative / Initiative → base merge (`--no-ff`)

> **In single-branch mode, the Epic→Initiative merge = not applicable** (§ single-branch-mode rules #2). The below assumes sub-branch mode. (However, the Initiative→base final PR is performed even in single-branch mode.)

In Initiative-based mode, the upper merge is performed as `--no-ff` (non-squash) rather than Squash, to preserve per-Epic history.

```bash
# Epic done → into the Initiative branch (--no-ff merge/PR)
git checkout initiative/[name]
git merge --no-ff epic/[name]      # not Squash — preserve the Epic commit structure

# Initiative done → PR into the base (shared) branch (--no-ff, only on user-explicit)
# Use the flow-pr procedure; the merge follows the §shared-branch-protection rule
```

> ⚠️ **Per-level merge method (do not confuse)**: Story→Epic = `--squash` / Epic→Initiative and Initiative→base = `--no-ff`.
> Shared-branch (base) merge/push only on user-explicit (§ shared-branch protection above).

## Cautions

- No working directly on the Epic branch → always on a Story branch
- When using `git add .`, confirm the current directory is the repo root
- Confirm `pwd` before a `git` command: return to the root after working in a sub-package
- Pattern: `cd /path/to/repo && git add -A && git commit ...` (absolute path)
