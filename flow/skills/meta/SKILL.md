---
name: meta
description: |
  Create and manage Skills, Rules, Prompts, and Subagents. Meta management of AI system components.
  Use in the following situations: (1) "make a Subagent", "create a subagent", (2) "make a skill", "write a SKILL.md",
  (3) "make a rule", "make an instruction", (4) "make a prompt", "write a .prompt.md".
  Use this skill for any request to create/manage an AI system component (Skill/Rule/Prompt/Subagent).
user-invocable: true
metadata:
  type: procedure
  version: v1.0.0
---

# Meta

A skill that creates/edits AI system components (Skill, Rule, Prompt, Subagent).
It judges the appropriate type from the user's request, loads the procedure doc, and executes it.

## Rules

1. **Judge the type first**: on receiving a request, judge the type with the Decision Tree, then load the procedure doc.
2. **Load the procedure doc**: after judging, reference the relevant procedure skill and follow the procedure.
   - Subagent create/edit procedure: `meta-agent-procedure/SKILL.md`
   - Skill create/edit procedure: `meta-skill-procedure/SKILL.md`
   - Rule create/edit procedure: `meta-rule-procedure/SKILL.md`
   - Prompt create/edit procedure: `meta-prompt-procedure/SKILL.md`
3. **Check for duplicates**: before creating, check for similar items in `.claude/skills/` + installed plugin skills (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/list-all-skills.py"`), `.claude/rules/`, `.claude/agents/`.
4. **Give the rationale**: concisely explain the type-judgment result to the user (e.g., "a Subagent is appropriate because multi-turn autonomous judgment is needed").

## Decision Tree

Criteria for judging the type from the user's request:

```
Analyze request
  │
  ├─ Explicit keyword?
  │   ├─ "make a Subagent/subagent" → meta-agent-procedure
  │   ├─ "make a skill" → meta-skill-procedure
  │   ├─ "make a rule/instruction" → meta-rule-procedure
  │   └─ "make a prompt" → meta-prompt-procedure
  │
  └─ Type unclear? → apply the criteria below
      │
      ├─ Multi-turn conversation + autonomous judgment + orchestration of multiple skills?
      │   └─ YES → Subagent (meta-agent-procedure)
      │
      ├─ Perform a fixed procedure step by step?
      │   └─ YES → Skill (meta-skill-procedure)
      │
      ├─ Declarative rule auto-applied to a project/folder scope?
      │   └─ YES → Rule (meta-rule-procedure)
      │
      └─ Simple command collection / script wrapper?
          └─ YES → Prompt (meta-prompt-procedure)
```

### Criteria summary

| Condition | Subagent | Skill | Rule | Prompt |
|------|-------|-------|------|--------|
| Multi-turn conversation needed | O | X | X | X |
| Autonomous judgment (what to do) | O | X | X | X |
| Orchestration of multiple skills | O | X | X | X |
| Perform a fixed procedure | X | O | X | X |
| Auto-applied to a file scope | X | X | O | X |
| Simple command/script | X | X | X | O |

## Flow

### Phase 1: Judge the type

1. Analyze the user's request
2. Decide the type with the Decision Tree
3. Explain the rationale to the user in 1 line
4. If unclear, confirm with the user

### Phase 2: Check for duplicates

1. Search for similar items in the relevant type folder
   - Skill: `.claude/skills/`
   - Rule: `.claude/rules/`
2. On finding a duplicate, report to the user (choose edit vs new creation)

### Phase 3: Execute the procedure

1. Reference the relevant guide skill and perform the procedure
2. Follow the procedure doc's resolution procedure 100%
3. After creation completes, report the result

## MUST NOT

- Load the procedure doc immediately without judging the type
- Skip the procedure doc's steps or replace them with your own procedure
- Skip checking for duplicates with existing components
- Decide the type without a rationale
- Use the procedure skill's content by guessing without loading it
