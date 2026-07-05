---
name: meta-skill-procedure
description: "Skill creation procedure. References the Reference vs Procedure decision + frontmatter standard + Progressive Disclosure + trigger-conflict verification."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Skill creation procedure

Procedure doc for creating and modifying SKILL.md files.

> **SSOT standard-language parity obligation**: persona / years-of-experience / Layer / Phase / flow-unit notation cites the standard-language dictionary table in the plugin rules/. No coining compound neologisms (parity with `meta-skill-writing` Anti-patterns).

## Scope (gray-area explicit)

| gray-area case | Primary | Secondary (must pass review) |
|---------------|---------|------------------------|
| Skill creation timing/order (when/how) | **meta-skill-procedure** | `meta-skill-writing` (confirm the authoring standard) |
| frontmatter standard / Persona 7 fields / Verification format | `meta-skill-writing` | **meta-skill-procedure** (confirm the registration procedure) |

**Anti-patterns**:
- Encroaching on `meta-skill-writing`'s responsibility (duplicating the detailed frontmatter authoring rules in this skill)
- Confusing Reference and Procedure ("how-to question" vs "work request")
- Exceeding 500 lines without splitting into references/
- Creating a new one after skipping the trigger-keyword-conflict verification
- Missing the description trigger keyword → no Claude Code auto-load signal
- Violating the frontmatter field order (`name → description → metadata`)

**Decision Heuristics**:
- "How do I use this tech?" → Reference
- "Do this work for me" → Procedure
- Body ≥ 500 lines → split into `references/`
- Examples ≥ 100 lines → split into `assets/`
- Repeatedly executed command → split into `scripts/`
- Trigger duplication found → merge into the existing skill or differentiate the description

**Output Quality Bar**:
- frontmatter field order: `name` → `description` → `metadata` (+ `user-invocable`)
- SKILL.md body ≤ 500 lines
- Detail exceeding 200 lines → split into `references/`
- description trigger keyword explicit (Claude Code auto-load signal)
- Report the duplication-search `grep` result
- Include a Verification section (verifiable commands)

**Sanity Self-Questions**:
- "Is this authoring rule not `meta-skill-writing`'s responsibility? (procedure only in this skill)"
- "Can I state the basis for judging Reference vs Procedure in one line?"
- "Is the SKILL.md body within 500 lines, or does it need a references/ split?"
- "Did I run the trigger-keyword duplication `grep`?"
- "Did I make the description trigger keyword explicit? (Claude Code auto-load signal)"
- "Did I keep the frontmatter field order `name → description → metadata`?"

## Summary

| Item | Content |
|------|------|
| **Deliverable** | SKILL.md file |
| **Type** | Reference (how to use a tech), Procedure (problem-solving procedure) |
| **Reference** | `meta-skill-writing/SKILL.md` (skill authoring guide) |

---

## Checklist

- [ ] Skill-type decision done? (Reference vs Procedure)
- [ ] SKILL.md file written? (Frontmatter + per-type structure)
- [ ] Verification section written?
- [ ] description trigger keyword made explicit? (Claude Code auto-load signal)
- [ ] (over 200 lines) split into a references/ folder?

## Solution procedure

### Step 1: Judge the skill type

**Work**: decide Reference vs Procedure type
**Result**: skill type fixed

| Type | Nature | Question form | Example |
|------|------|----------|------|
| **Reference** | "This tech is used like this" | how-to question | `guide-<library>` (external marketplace library guide) / `guide-<convention>` (coding-convention guide) |
| **Procedure** | "This problem is solved like this" | work request | `flow-*`, `meta-*`, per-role implementation skills |

**Checklist**:
- [ ] "How do I use this tech?" → Reference
- [ ] "Do this work for me" → Procedure

### Step 2: Judge new/modify

**Work**: decide new creation vs existing modification
**Branch**: new → Step 3 / existing → read SKILL.md → Step 3

### Step 3: Write SKILL.md

**Work**: write the document from the per-type template
**Result**: SKILL.md file
**Related material**: `meta-skill-writing/SKILL.md`

| Type | Template |
|------|--------|
| Reference | see `meta-skill-writing/SKILL.md` |
| Procedure | see `meta-skill-writing/SKILL.md` |

**Frontmatter required fields** (agentskills.io order):
```yaml
---
name: {skill-name}         # required. lowercase + hyphen, ≤ 64 chars
description: {description including the trigger condition}  # required. 1-1024 chars
metadata:
  type: reference  # or procedure (project-proprietary field)
  version: v1.0.0  # project-proprietary field
---
```

> Order: `name` → `description` → `metadata` (agentskills.io required → project-proprietary order)

**Checklist**:
- [ ] Frontmatter includes name, description, metadata?
- [ ] Field order: name → description → metadata?
- [ ] Structure matching the type used?
- [ ] SKILL.md body within 500 lines? (Progressive Disclosure Stage 2 budget)
- [ ] Verification section written?

### Step 4: Decide the resource folders

**Work**: judge whether scripts/references/assets/ are needed
**Result**: resource folder structure

| Folder | Condition | Progressive Disclosure |
|------|------|----------------------|
| scripts/ | repeatedly executed scripts | Stage 3 (on-demand) |
| references/ | detailed guide over 200 lines | Stage 3 (on-demand) |
| assets/ | templates/images/examples | Stage 3 (on-demand) |

> **When exceeding 500 lines**: split the detailed reference material into `references/` to keep SKILL.md within 500 lines.
> See `meta-skill-writing/SKILL.md` § Progressive Disclosure.

**Checklist**:
- [ ] SKILL.md within 500 lines?
- [ ] Content over 200 lines → split into references/?
- [ ] Examples over 100 lines → split into assets/?

### Step 5: Trigger verification

**Work**: make the description trigger keyword explicit + confirm no duplication
**Result**: skill auto-load signal activated, no duplication confirmed

> **Claude Code Skill auto-load mechanism**: when a keyword in the `description` field matches the user message, the Skill auto-loads. No separate registration file needed.

**Duplication-check procedure**:
1. Scan the existing skill list (project + installed plugin skills):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/list-all-skills.py" | sort -u
   ```
2. Search for duplicates by similar trigger keyword:
   ```bash
   grep -rn "key keyword" .claude/skills/*/SKILL.md ~/.claude/plugins/marketplaces/*/plugins/*/skills/*/SKILL.md
   ```
3. Confirm the description trigger conflict (that a different skill isn't triggered by the same trigger):
   ```bash
   grep "description" .claude/skills/*/SKILL.md ~/.claude/plugins/marketplaces/*/plugins/*/skills/*/SKILL.md | grep -i "key keyword"
   ```

> On finding a duplicate: merge into the existing skill or differentiate the description.

**Checklist**:
- [ ] Trigger keyword made explicit in the description field?
- [ ] Existing-skill duplication confirmed with grep?
- [ ] Is the description parity with the user's natural-language expression?
