# Fix: write-epic skill generates incorrect directory structure

## Problem

When Claude executes the `write-epic` skill without an existing project context, it generates epics and stories in a flat/incorrect structure — creating top-level `goals/` or `epics/` directories instead of nesting under the full `workspace/phase/` hierarchy.

**WRONG — what Claude currently generates:**
```
goals/
  {goal-name}/
    _goal.md
    {epic-name}/
      _epic.md
      stories/
        US-001-{name}/
          _story.md
epics/          ← sometimes generated as top-level
  {epic-name}/
    _epic.md
```

**CORRECT — expected canonical structure:**
```
workspace/
  phase/
    {year}-P{N}-{phase-name}/         ← e.g. 2026-P1-foundation
      goals/
        {GN}-{goal-name}/             ← e.g. G0-infrastructure
          _goal.md
          artifacts/
            use-case/
            concept/
          epics/
            {NN}-{epic-name}/         ← e.g. 01-auth
              _epic.md
              stories/
                {US|TS}-{NNN}-{name}/ ← e.g. US-001-login
                  _story.md
                  steps/
                    S-001-{name}.md
published/
  identity/
  service-map/
  concept/
  journey/
  schema/
```

## Root Cause

The `write-epic` SKILL.md Workflow section specifies paths without the full `workspace/phase/` prefix:

```
# Ambiguous — current
Story 분해 → `stories/[US|TS]-NNN/_story.md`
```

Claude infers a reasonable but incorrect top-level placement. The full path from repo root is never stated.

## Required Fix

### 1. Add Directory Structure section to `write-epic/SKILL.md`

```markdown
## Directory Structure

Epic and all children live under the phase/goal hierarchy:

workspace/phase/{phase-id}/goals/{goal-id}/epics/{NN}-{name}/
  _epic.md
  stories/
    {US|TS}-{NNN}-{name}/
      _story.md
      steps/
        S-NNN-{name}.md
```

### 2. Fix all path references in Workflow steps

```yaml
# Replace ambiguous:
Story 분해 → `stories/[US|TS]-NNN/_story.md`

# With explicit full path:
Story 분해 → `workspace/phase/{phase-id}/goals/{goal-id}/epics/{NN}-{epic-name}/stories/{US|TS}-{NNN}-{name}/_story.md`
```

### 3. Add phase/goal resolution step to Workflow

Before creating any files, the skill must resolve the current phase and goal:

```yaml
0. Resolve context:
   - Read progress.md → get current phase-id and goal-id
   - If progress.md missing → ask user for phase name and goal name
   - Set base_path = workspace/phase/{phase-id}/goals/{goal-id}/epics/
```

## Files to Update

- `solera/skills/write-epic/SKILL.md`
- `solera/skills/write-goal/SKILL.md` — same issue for goal path
- `solera/skills/write-story/SKILL.md` — same issue for story path

## Acceptance Criteria

- [ ] Claude generates `workspace/phase/{phase-id}/goals/{goal-id}/epics/{NN}-{name}/_epic.md`
- [ ] Claude generates stories under `epics/{NN}-{name}/stories/{US|TS}-{NNN}-{name}/_story.md`
- [ ] No top-level `epics/` or standalone `goals/` directory is ever created
- [ ] On a fresh repo with no `progress.md`, Claude asks for phase/goal names before creating files
