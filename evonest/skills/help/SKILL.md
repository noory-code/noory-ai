---
name: help
user-invocable: true
description: Explain what Evonest is, list all available MCP tools, and guide the first step.
metadata:
  version: "1.0.0"
  category: meta
  type: reference
  style: guide
  triggers: [what is evonest, evonest help, evonest tools, how to use evonest, evonest get started]
  uses: []
---

# Evonest Help

> Autonomous code evolution engine — observe, plan, execute, verify.

## Overview

Evonest is an MCP-native code quality engine that runs improvement cycles on your project. It rotates through 20 specialist personas (security auditor, performance engineer, etc.) to find and fix issues across different dimensions. All changes are proposed first — you review before anything executes.

Each tool takes `project` (absolute path) as its first argument.

## Available MCP Tools

| Tool | When to use |
|------|-------------|
| `evonest_init` | First-time setup — creates `.evonest/` in the target project |
| `evonest_analyze` | Scan and save ALL improvements as proposals (no code changes) |
| `evonest_improve` | Execute one proposal (`proposal_id=...`) or all (`all=True`) |
| `evonest_evolve` | Full cycle: Observe → Plan → Execute → Verify → commit/PR |
| `evonest_status` | Show project status summary |
| `evonest_proposals` | List pending proposals |
| `evonest_history` | Show cycle history |
| `evonest_config` | Read or update `.evonest/config.json` |
| `evonest_identity` | Read or write `.evonest/identity.md` |
| `evonest_identity_refresh` | Re-draft identity.md by having Claude explore the project |
| `evonest_backlog` | Manage the improvement backlog |
| `evonest_stimuli` | Add a stimulus (external input for the next observe cycle) |
| `evonest_decide` | Record a human decision (constrains future proposals) |
| `evonest_progress` | Show progress report |
| `evonest_scout` | Run scout phase — search for ecosystem changes and inject as stimuli |
| `evonest_personas` | List, enable, or disable personas and adversarials |
| `evonest_update_docs` | Sync skills/commands/agents/rules/CLAUDE.md with current code |

## Quick Start

**First time on a new project — say:**

> Initialize evonest for this project, then analyze it for improvements.

Evonest will run `evonest_init`, set up `.evonest/`, then `evonest_analyze` to generate the first batch of proposals.

**Review and apply proposals:**

> Show me the evonest proposals, then apply the top one.

**Fully autonomous — say:**

> Run 3 evonest evolution cycles on this project.
