---
name: meta-prompt-procedure
description: "Reference procedure for creating Prompt assets. Reference for the skill vs prompt boundary + promotion scorecard."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Prompt creation procedure (reference)

The reference procedure SSOT for creating Prompt assets. A simple command/script wrapper (within 50 lines) is the appropriate scope for a Prompt; anything beyond that is promoted to a Skill.

> **SSOT standard-vocabulary alignment obligation**: cite the standard-vocabulary dictionary in the plugin rules/.

## Skill vs prompt boundary

| Criterion | Prompt | Skill |
|------|----------|------|
| Complexity | low (within 50 lines) | high (100+ lines) |
| Procedure | 1-3 steps | multi-step (Step 0-N) |
| Verification | simple | Verification + Hard Gate |
| Reuse frequency | occasional | 3+ times per week |

## Skill-promotion criteria (mandatory when 2 or more apply)

| Condition | Threshold | Description |
|------|--------|------|
| Content length | over 50 lines | exceeds the recommended prompt limit |
| Procedure steps | over 3 steps | multi-step → make it a Skill |
| Verification need | Verification needed | build/test verification needed |
| External reference | references/ needed | detailed docs need to be split out |
| Reuse frequency | 3+ times per week | frequently used → make it a Skill |

## Prompt creation procedure

1. **Type judgment**: executable (script wrapper) / guide (procedure guidance) / hybrid
2. **Location decision**: `.claude/prompts/` or the standard location for Claude Code slash commands
3. **File name**: `{name}.prompt.md` (kebab-case, within 50 lines)
4. **Frontmatter**: state a one-line `description`
5. **Script (optional)**: split a complex command chain into `tools/` or `scripts/`
6. **Promotion judgment**: if 2 or more items on the scorecard above apply → switch to `meta-skill-procedure`

## Related SSOT

- `meta-skill-procedure` — Skill creation procedure (promotion target when a Prompt exceeds 50 lines)
- `meta` — the entry point for Skill / Rule / Prompt / Subagent meta management
- plugin rules/ — the standard-vocabulary dictionary
