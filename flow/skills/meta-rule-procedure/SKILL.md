---
name: meta-rule-procedure
description: "Rule creation procedure. Reference for auto-load location (`.claude/rules/`) + constraints as principle+reason over prohibition + MUST/SHOULD/MUST NOT distinction + duplication verification procedure."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Rule creation procedure

The procedure for creating and editing `.claude/rules/*.md` auto-load rule files.

> **Standard-term consistency duty**: notation for persona / years of experience / Layer / Phase / flow units cites the standard-term table in the plugin rules/. No coining terms·arbitrary compound words.

## TL;DR (5 core points)

1. **Step 1→2→3→4**: determine type → state the applicable scope → write the rule → verify duplication
2. **Declarative**: "what"-centric, in the form "shall ~"
3. **Principle+reason over prohibition**: MUST NOT (prohibition) only for hard constraints; the default is to explain "why" (§constraint expression)
4. **SSOT**: no duplication, link-reference existing rules (`.claude/rules/` auto-load)
5. **Verifiable**: compliance can be judged objectively

---

## Checklist

- [ ] Applicable scope stated in the body?
- [ ] `.claude/rules/*.md` file written? (TL;DR + principle/reason + MUST/SHOULD if needed, MUST NOT only for hard constraints)
- [ ] Written in declarative form? ("shall ~")
- [ ] `.claude/rules/` directory location confirmed? (auto-load)
- [ ] No duplication with existing rules?

## Resolution procedure

### Step 1: Determine type

**Work**: decide new creation vs edit of an existing one
**Result**: work type confirmed
**Branch**: new → Step 2 / existing → read the rule file → Step 2

**Checklist**:
- [ ] Confirmed existing rules? (`ls .claude/rules/`)
- [ ] Decided new/edit?

### Step 2: State the applicable scope

**Work**: state the applicable scope in the first section of the rule body
**Result**: body "Applicable scope" section

| Pattern | Description |
|------|------|
| All work | `> **Applicable scope**: all work` |
| Specific work area | `> **Applicable scope**: [the relevant work area (e.g., code writing / documentation / design)]` |
| Specific Phase | `> **Applicable scope**: every Action execution in the Epic/Story/Action flow` |
| Specific tool | `> **Applicable scope**: every tool-use point` |

**Checklist**:
- [ ] Applicable scope stated in the body's first section?
- [ ] Scope not ambiguous / not excessive?

### Step 3: Write the rule

**Work**: write the rule based on the template
**Result**: `.claude/rules/*.md` file

**Template**:
```markdown
# [rule title]

> **Applicable scope**: [all work / specific work area / specific Phase, etc.]

## TL;DR (core)

1. **[principle 1]**: [what — and why it should be so]
2. **[principle 2]**: [what — why]

## Principles (why)

- [state the constraint with its reason — "do X, because Y". A reason lets the model generalize beyond the case]

## MUST / SHOULD (if needed)

- [affirmative requirement (MUST)·recommendation (SHOULD). Omit if the principle suffices]

## MUST NOT (only when there is a hard constraint)

- [only when the act itself is a failure. If it can be expressed as principle+reason, do not put it here. If none, omit this whole section]

## Checklist

- [ ] [item]
```

**Checklist**:
- [ ] TL;DR + principles (why) written?
- [ ] Expressed as principle+reason instead of prohibition? (MUST NOT only for hard constraints)
- [ ] Checklist included?

### Step 4: Integration

**Work**: check for duplication with existing rules + verify the impact on Skill / Subagent bodies
**Result**: rule activated (`.claude/rules/` auto-load), confirmed no duplication

**Duplication check procedure**:
1. Scan the existing rule list:
   ```bash
   ls .claude/rules/
   ```
2. Search for duplication by similar keywords:
   ```bash
   grep -rn "core-keyword" .claude/rules/
   ```
3. Check for MUST/MUST NOT conflicts between rules:
   ```bash
   grep -n "MUST\|MUST NOT\|SHOULD" .claude/rules/*.md | head -30
   ```
4. Check the change impact (whether the same rule exists in a Skill / Subagent body):
   ```bash
   grep -rn "core-keyword" .claude/skills/ .claude/agents/
   ```

> On finding duplication: integrate into the existing rule or replace with a link reference.

**Checklist**:
- [ ] Located in the `.claude/rules/` directory? (auto-load)
- [ ] Checked duplication with existing rules via grep?
- [ ] No MUST/MUST NOT conflict?

---

## Rule vs skill vs hook — 2 orthogonal axes (location × enforcement)

Decide rule/skill/hook by **2 independent axes**. Do not split rule/skill by reliability (bypass prevention).

### Axis 1 — location (rule vs skill): "an always-on constraint across many tasks, or a single procedure"

| Property | Rule | Skill |
|------|-----|------|
| Location | `.claude/rules/*.md` | `.claude/skills/{name}/SKILL.md` |
| Nature | Always-on constraint — task-independent (what, declarative) | Single procedure — only when doing that task (how, procedural) |
| Application | Automatic/always-on (session load) | On trigger (description match) |

- **Rule identification**: a constraint that must always be kept across many tasks (tool priority·question discipline·architecture floor constraints, etc.). A specific skill may not be loaded at the firing moment → always-on load needed.
- **Skill identification**: "how to do X" is needed only at that task's point (how to commit·how to delegate, etc.). That task = loading that skill = the needed point coincides → inherent to the skill.

### Axis 2 — enforcement (hook): "must it not be bypassed" (independent of location)

- Rule/skill text has **equal enforcement power** — both are bypassed if the model does not follow. "Making it a rule means it will never be unobserved" is false (text rules have bypass cases too).
- **Only hooks (code) actually prevent bypass.** When a step is driven by a procedure, text suffices, but for high-miss-cost things like **irreversible acts (commit/merge/push) + entry gates**, enforce with a hook.
- That is, "it gets bypassed, so let's move it to a rule/always-load" has no effect — bypass prevention is via a hook or procedure-driven.

### Reduction principle (ceremony vs core)

- Keep **only the core** in a rule. Cut content already in other rules/skills/higher guidance·repeated examples·residue of finished work (ceremony).
- Do not put the same fact in two places (SSOT). If duplicated, make one the canonical source and the rest a reference.

### Constraint expression — principle+reason over prohibition

When encoding a constraint, the base form is **principle+reason** ("do X, because Y"). Use prohibition (MUST NOT/❌) only for a **hard constraint** where the act itself is a failure.

- **Why**: blocking every problem from a retrospective with a one-line prohibition makes prohibitions pile up infinitely, bloating rules·skills and making rules that fit only that case with no generalization. Giving the reason (why) lets the model judge beyond the case — today's models understand reasons and act.
- **Default behavior**: before adding a new prohibition, tighten or fix the existing guidance with a reason (edit first, add second).
- **Hard-constraint exception**: only things where the negative form is clearer, like irreversible·safety·contract violations (misuse of commit/merge/push, etc.), are MUST NOT. Even then, add a one line on why it is hard.
- **Self-consistency**: this principle itself is stated with a reason as above, not as "do not prohibit".

> This section = the common canonical source (SSOT) for writing rules·skills·playbooks. Skill writing is `meta-skill-writing`, retrospective reflection references this section in `retro-processing` procedure ③.

### On self-discovery of a violation (self-correction format)

If the AI discovers a rule violation on its own, report in the following format then correct: `[self-correction notice] location / violation / correction / origin`.

## Link policy

**`.claude/rules/*.md` files**:
- ❌ **Prohibited**: actually working markdown links `[text](file.md)`
- ✅ **Allowed**: plain-text reference `see file.md` or backticks `` `file.md` ``
- **Reason**: since the AI must load and read the file directly, a clickable link causes confusion

**SKILL.md and references/*.md files**:
- ✅ **Allowed**: markdown links `[text](file.md)` may be used
