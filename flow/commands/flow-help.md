---
description: flow plugin help — explains what the plugin is / how to use it + "what to do when it's not working" troubleshooting
argument-hint: "[topic — optional (config / playbook / hook / teams, etc.)]"
---

# /flow-help

You are a guide who **explains** the flow plugin to the user and **unblocks** them when they get stuck.
Explain clearly, and for troubleshooting use **symptom → action**. Let the user immediately know their next action (Don't Make Me Think).

> If a topic is given as an argument (`/flow-help hook`), cover only that topic; if omitted, cover everything.

## 1. What is this plugin

**A general-purpose flow planner (work-type based)** — plan with Epic/Story/Action, and evolve to work progressively better through retrospectives. It only knows "how to plan"; "what to build" (language/framework) is decided by the project context.

- **North Star**: a system where the AI understands the purpose and takes ownership of checking whether that purpose was reached.

## 2. Core usage flow

1. **Initial setup / re-tuning** — `/flow-config` (the AI understands the project → injects playbooks·teams. Re-run when the project changes)
2. **Planning** — in Plan Mode, judge scale (Epic? Story?) → decompose into Actions (human·AI collaboration)
3. **Execution** — the main assigns experts and orchestrates per the playbook procedure (performs the Action) → verify → commit → retrospective
4. **Status/improvement** — `/flow-status` (view current settings) · assessment (how to run the flow better — proactive improvement recommendations)

## 3. Commands

| Command | Use |
|------|------|
| `/flow-config` | Inject / re-tune settings (initial + thereafter) |
| `/flow-help` | This help |
| `/flow-status` | Current settings + assessment (status + assessment) |

## 4. Troubleshooting — "what to do when it's not working"

| Symptom | Cause | Action |
|------|------|------|
| **Blocked** when trying to modify code | Modifying code without an A-NNN.md (Action document) (hook) | First write the `A-NNN.md` for that Action, then modify |
| **Commit is blocked** | The in-progress Action retrospective is empty (hook) | Write the Action retrospective (Keep/Problem/Try), then commit |
| **teammate doesn't appear** | Agent Teams env not enabled | Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `.claude/settings.json` + restart the session. Without it, work still parallelizes via regular subagents (the Task tool) — sequential only for dependency-serial waves |
| **playbook not applied** | No `.flow/settings.json` | Run `/flow-config` |
| **Task status not visible** | No `.flow/workspace/` | Create the standard directories with `/flow-config` |
| **Too many unnecessary questions** | Missing purpose anchoring | Check the top-level SSOT `**ultimate purpose**` (the `purpose-anchoring` rule) — if it can be derived from the purpose, don't ask |

## 5. Learn more

- Flow procedure detail: the `flow` skill
- playbook types: `playbooks.json` / `playbooks/`
- Writing role personas: `personas-extension.md`
