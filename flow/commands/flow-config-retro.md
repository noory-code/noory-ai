---
description: Set the retrospective rigor label — recommend .flow/settings.json retrospective.levels from ground-truth inspection, then inject/update on explicit user confirmation. Detailed procedure in references/flow-config-retro-procedure.md
argument-hint: "[level — optional: when adjusting a single level of action/story/epic/initiative]"
allowed-tools: Read, Glob, Grep, Edit, Bash(uv:*)
---

# /flow-config-retro

You are the administrator (Flow Manager) who configures the flow plugin's **retrospective rigor policy** to fit the project.

This command is an explicit-invocation entrypoint. Load the detailed procedure from `commands/references/flow-config-retro-procedure.md` with `Read`, then follow it exactly.

## Execution order

1. `Read flow/commands/references/flow-config-retro-procedure.md`
2. Ground-truth inspect `.flow/settings.json`, the active playbook, and existing retrospective patterns.
3. Explain the `none|minimal|template|template+rt` labels in the user's language.
4. Present a recommendation per action/story/epic/initiative.
5. Patch settings only after explicit user confirmation.
6. Confirm the hook reads the settings via ground-truth inspection of the retrospective policy reader.

## Core principles

- Do not write immediately after recommending/interviewing. STOP before explicit confirmation.
- Preserve existing `playbooks` / `agents` values.
- `initiative.rigor=none` is not allowed.
- The SSOT for the label definitions is `flow-retrospective` Part 4.

## Completion output

```text
✅ flow-config-retro done — retrospective schema/guard/reader parity confirmed.
```
