---
name: flow-pr
description: |
  PR creation, Pull Request. Create a PR to merge completed work into a shared branch. Provides the skeleton for work completion → change cleanup → PR body authoring → sharing.
  Use in the following situations: (1) "make a PR", "create a pull request", (2) "a PR to merge into the shared branch", (3) creating a PR after a unit of work completes.
  Use this skill for any request related to PR, Pull Request, or pull requests.
user-invocable: true
metadata:
  type: procedure
  version: v1.0.0
---

# Flow PR

## Checklist

- [ ] pr/ branch created and excluded targets deleted?
- [ ] Commit history analysis complete?
- [ ] PR body file created?
- [ ] Branch push complete?
- [ ] PR created with the project PR tool?

---

## Core rules

### PR branch strategy

**When creating a PR from a work branch**:
1. Create a `pr/{name}` branch
2. Delete excluded targets, then commit
3. Create the PR from the pr/ branch

### PR excluded targets (required)

| File/folder | Reason |
|-----------|------|
| Flow work records (work-item SSOT) | AI work records (local-only) |
| Session progress-state files | Local-only |
| Session handoff files | Local-only |

> **Nature of the excluded targets**: the work-item SSOT (flow work records like Epic/Story/Action) and session temp files are not PR artifacts. Use the flow work-record path defined by the project as the excluded target.

### PR title format

`[TYPE] title`

| TYPE | Use |
|------|------|
| `[FEAT]` | New feature |
| `[FIX]` | Bug fix |
| `[DOCS]` | Docs only |
| `[REFACTOR]` | Structural improvement |

### Tag naming rule

`{type}/{description}#{N}`

- `{type}`: same as the PR type (lowercase: `feat`, `fix`, `docs`, `refactor`, etc.)
- `{description}`: work summary (kebab-case)
- `#{N}`: sequence number for the same description (starting at 1). Look up existing tags and use the next number

**Examples**:
- `feat/login-flow#1`
- `fix/null-pointer-profile#1`
- `docs/update-guide#1`

---

## Resolution procedure

### Step 1: Create PR branch and handle excluded targets

**Task**: create the pr/ branch, then delete excluded targets
**Result**: a clean pr/ branch

> ⚠️ **Confirm before deleting**: deleting the flow work records deletes the entire work-item SSOT. Confirm it runs **only on top of the pr/ branch** (no effect on the original work branch), report the deletion targets to the user in 1 line, then proceed. Check the current branch is `pr/` with `git branch --show-current`.

**Method**:
```bash
# 1. Create the pr/ branch
git checkout -b pr/{name}

# 1.5. Confirm the current branch (delete only on top of pr/ — protect the original)
git branch --show-current   # → after confirming pr/{name}, go to the next step

# 2. Delete excluded targets (limited to the pr/ branch)
#    Delete the flow work-record path defined by the project + session temp files
rm -rf {flow work-record path}
rm -f {session temp files}

# 3. Commit the deletion
git add -A
git commit -m "chore: remove PR-excluded targets (flow work records, session temp files)"
```

**Checklist**:
- [ ] pr/ branch created?
- [ ] Flow work records deleted?
- [ ] Session temp files deleted?
- [ ] Deletion commit complete?

---

### Step 2: Analyze commit history

**Task**: analyze commits after the base branch
**Result**: summary, change draft

**Method**:
```bash
# Decide the base branch (see the base-decision criteria in Step 4)
base="{shared branch — project-defined}"

# Check the commit list
git log origin/$base..HEAD --pretty=format:'%h %s'
```

**Analysis items**:
1. Group by type (feat, fix, docs, refactor)
2. Summarize each commit in prose
3. Write a one-sentence summary

---

### Step 3: Create the PR body file

**Task**: create the PR body file
**Result**: `pr-body-{branch-name}.md` (temp file in the working directory — do not hardcode POSIX absolute paths like `/tmp` (plugin OS-compat policy: macOS·Windows). Deleted in Step 5 after the PR is created)

**Method**:
1. Read the project PR template (if any) with `Read`
2. Keep the template structure, fill in all content
3. Create the `pr-body-{branch-name}.md` file

#### PR body structure

```markdown
## Summary
{1-2 sentences on the core purpose of the whole PR}

## Related
- Work item: {work-item SSOT link — if any}
- Issue: {issue number — if any}

## Changes
- {change 1}
- {change 2}
- {change 3}

## Testing
- [x] Build passed (project verification command)
- [x] Tests passed (project verification command)
- [x] Manual testing complete

## Screenshots
N/A (architecture/docs changes only)

## Checklist
- [x] Code self-review complete
- [x] Necessary docs updated
- [x] Related tests added/updated
```

#### PR body authoring rules

**Summary** (required):
- Summarize the core purpose of the whole PR in 1-2 sentences

**Related** (optional):
- Work-item link: check the work-item SSOT (Epic/Story, etc.) path
- Issue number: add if any

**Changes** (required):
- Based on commit history, bullet points
- Group by commit type (order: feat → fix → docs → refactor)
- Use clear English verbs: Add, Remove, Update, Fix, etc.

**Testing** (required):
- `[x] Build passed` (project verification command)
- `[x] Tests passed` (project verification command, "N/A" if none)
- `[x] Manual testing complete`

**Screenshots** (conditional):
- UI changes present: add screenshots
- No UI changes: "N/A (architecture/docs changes only)"

**PR title rules**:

| TYPE | Use | Example |
|------|------|------|
| `[FEAT]` | New feature | `[FEAT] Add login feature` |
| `[FIX]` | Bug fix | `[FIX] Fix null-reference bug` |
| `[DOCS]` | Docs only | `[DOCS] Write guide` |
| `[REFACTOR]` | Structural improvement | `[REFACTOR] Standardize architecture` |
| `[TEST]` | Tests only | `[TEST] Add login tests` |
| `[CHORE]` | Config/tooling | `[CHORE] Change build config` |

**Checklist**:
- [ ] Summary written?
- [ ] 3+ changes?
- [ ] Testing checkboxes complete?

---

### Step 4: Push and create the PR

**Task**: push the branch, then create the PR with the project PR tool
**Result**: PR URL

> **Project PR tool**: PR creation/push is performed with the tool the project provides (e.g., GitHub / GitLab — project-supplied). The procedure below is a tool-agnostic common skeleton; the actual commands follow the project tool's spec.

**Method**:
```bash
# 1. Push the branch (required! otherwise an interactive prompt may appear)
git push -u origin pr/{name}

# 2. Create the PR with the project PR tool
#    - base: shared branch (project-defined)
#    - head: pr/{name}
#    - title: [TYPE] title
#    - body: pr-body-{branch-name}.md (file input — preserves multiline)
```

> Creating a PR without pushing may trigger a "push where?" style prompt.
> Use **file input** for the PR body instead of an inline string (prevents multiline breakage).

#### Base branch decision (when the user does not specify)

> 🚨 **Decision order (enforced)**:
> 1. **User-specified** — as-is (highest priority)
> 2. **Work-item SSOT explicit base** — exactly the base specified in the work-item (Epic/Story) doc (no automatic default inference)
> 3. **Standalone work** — the work branch's specified base
> 4. **None of the above** — confirm with the user (no automatic default inference)

| Current branch | base decision |
|------------|----------|
| `pr/*` (work-cleanup PR) | **Work-item SSOT explicit base** or user-specified |
| `pr/*` (standalone) | User-specified or shared branch (project-defined) |
| Work branch (within a higher-level unit) | **Higher-level unit base** |
| Work branch (standalone) | User-specified or shared branch (project-defined) |
| Lower-level unit branch | The corresponding higher-level unit branch (Squash merge — not a PR) |

> **Core principle**: no automatic default inference of the shared branch. **Enforce the work-item SSOT's explicit base**.
>
> **Impact if violated**: automatic default inference → risk of merging into the wrong base + applying unrelated changes.

**Edit PR / check status**:
- Edit body / edit title / check status is performed with the corresponding command of the project PR tool.

**Checklist**:
- [ ] git push complete?
- [ ] base branch confirmed?
- [ ] PR body file input used?
- [ ] PR URL confirmed?

---

### Step 5: Cleanup

**Task**: delete temp files, report result
**Result**: PR creation complete

**Method**:
```bash
rm pr-body-*.md
```
