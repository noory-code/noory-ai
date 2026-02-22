---
name: claude-plugin-ref
description: "Claude Code plugin development reference for this monorepo (evonest, distill). Covers plugin structure, manifest, hooks, skills, commands, agents, MCP servers, and marketplace."
user-invokable: true
---

# Claude Code Plugin Development Guide

Plugin development patterns for this monorepo and Claude Code plugin system reference.

## Directory Structure

```
<package>/
├── .claude-plugin/
│   ├── plugin.json          # manifest (required)
│   └── marketplace.json     # marketplace registration (optional)
├── skills/
│   └── <skill-name>/
│       └── SKILL.md         # skill definition
├── commands/
│   └── <command>.md         # slash command
├── hooks/
│   └── hooks.json           # hook event definitions
├── agents/
│   └── <agent-name>/
│       └── AGENT.md         # agent definition
└── src/                     # MCP server code
```

**Important**: skills/, commands/, hooks/, agents/ live OUTSIDE `.claude-plugin/`. Referenced via relative paths in plugin.json.

## plugin.json Manifest

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "One-line description",
  "author": { "name": "author-name" },
  "skills": "./skills/",
  "commands": ["./commands/foo.md", "./commands/bar.md"],
  "hooks": "./hooks/hooks.json",
  "agents": "./agents/",
  "mcpServers": {
    "server-name": {
      "command": "uv",
      "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}", "python", "-m", "my_module"]
    }
  }
}
```

Field reference:
- `skills`: directory path (auto-discovery) or file array
- `commands`: file path array (directory path NOT supported)
- `hooks`: path to hooks.json file
- `agents`: directory path or file array
- `mcpServers`: `${CLAUDE_PLUGIN_ROOT}` = plugin root absolute path (substituted at runtime)

## Hooks

### hooks.json Schema

```json
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python script.py"
          }
        ]
      }
    ]
  }
}
```

**Warning**: Each event array entry MUST be wrapped in `{ "hooks": [...] }`.
Placing `{ "type": "command", ... }` directly causes a schema error.

### Hook Events

| Event | Trigger | matcher target |
|-------|---------|---------------|
| `PreToolUse` | Before tool call | Tool name (Bash, Write, Edit, etc.) |
| `PostToolUse` | After tool call | Tool name |
| `Stop` | After response completes | - |
| `SubagentStop` | After subagent completes | - |
| `SessionStart` | Session starts | - |
| `SessionEnd` | Session ends | - |
| `UserPromptSubmit` | After user message submitted | - |
| `PreCompact` | Before context compaction | - |
| `Notification` | On notification | - |

### Hook Types

**command**: Execute a shell command
```json
{ "type": "command", "command": "python script.py" }
```

**prompt**: LLM prompt for tool use decisions
```json
{
  "type": "prompt",
  "prompt": "Is this Bash command safe? Answer ALLOW or BLOCK.",
  "decision": { "allow": "ALLOW", "deny": "BLOCK" }
}
```

### Hook Input (stdin JSON)

Command hooks receive JSON via stdin:
- `hook_event_name`: event name
- `tool_name`: tool name (PreToolUse/PostToolUse)
- `tool_input`: tool input parameters
- `tool_output`: tool output (PostToolUse only)
- `transcript_path`: conversation log path
- `session_id`: session ID

### Hook Response (stdout JSON)

```json
{"continue": true}                          // proceed
{"continue": true, "suppressOutput": true}  // suppress output
{"decision": "block", "reason": "..."}      // block tool use
{"decision": "approve"}                     // auto-approve
```

## Skills

### SKILL.md Structure

```markdown
---
name: my-skill
description: Skill description (used for trigger matching)
user-invocable: true
allowed-tools: ["Bash", "Read", "Write"]
---

# Skill Title

Skill content (instructions, workflows, etc.)
```

Frontmatter fields:
- `name`: skill name (required)
- `description`: trigger description — model uses this to decide when to invoke (required)
- `user-invocable`: if true, callable via `/skill-name`
- `disable-model-invocation`: if true, disables automatic model triggering
- `allowed-tools`: list of allowed tools
- `model`: specify model (sonnet, opus, haiku)
- `context`: array of additional context file paths

## Commands

### Command File Structure

```markdown
---
description: Command description
argument-hint: "[arg1] [--flag]"
---

Command instructions.

Use $ARGUMENTS to reference user arguments.
```

Frontmatter fields:
- `description`: command description (required)
- `argument-hint`: argument hint (optional)

Commands are invoked as `/plugin-name:command-name`.

## Agents

### AGENT.md Structure

```markdown
---
name: my-agent
description: >
  Agent trigger conditions.
  Be specific: "when the user asks to...", "after creating..."
allowed-tools: ["Read", "Grep", "Glob"]
---

# Agent System Prompt

Instructions for what the agent should do.
```

## MCP Servers

### Adding MCP Server to plugin.json

```json
"mcpServers": {
  "server-name": {
    "command": "uv",
    "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}", "python", "-m", "module"],
    "env": { "KEY": "value" }
  }
}
```

Server types:
- **stdio**: `command` + `args` (most common)
- **sse**: `url` field
- **http**: `url` field

### MCP Patterns in This Monorepo

evonest: `uv run --directory ${CLAUDE_PLUGIN_ROOT} evonest`
distill: `uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m distill`

## Marketplace

### marketplace.json

Place in repo root or inside package at `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "description": "Description",
      "plugin": ".claude-plugin/plugin.json"
    }
  ]
}
```

`plugin` path is relative to marketplace.json location.

### Installation

```
/install-plugin <github-url>
```

Local install (during development):
```
/install-plugin /absolute/path/to/plugin-dir
```

## This Monorepo Structure

```
noory-ai/
├── evonest/
│   ├── .claude-plugin/
│   │   ├── plugin.json
│   │   └── marketplace.json
│   ├── skills/evonest/SKILL.md
│   └── commands/{analyze,evolve,improve,identity}.md
└── distill/
    ├── .claude-plugin/plugin.json
    ├── skills/distill/SKILL.md
    └── hooks/hooks.json
```

## Common Mistakes Checklist

- [ ] Missing `{ "hooks": [...] }` wrapper in hooks.json entries
- [ ] `author` must be an object `{ "name": "..." }`, not a string
- [ ] `skills` directory path must end with `/` (e.g. `"./skills/"`)
- [ ] `commands` must be an array of file paths (directory path not supported)
- [ ] marketplace.json `plugin` path must be relative to marketplace.json location
- [ ] `${CLAUDE_PLUGIN_ROOT}` only works in MCP args (not in hook commands)
- [ ] `.claude/settings.local.json` should be in .gitignore (personal settings)
