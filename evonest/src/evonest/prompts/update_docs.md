# Update Docs — Sync Claude Code files with current codebase

You are a documentation synchronization expert. Your job is to make sure
the project's Claude Code files (skills, commands, agents, rules, CLAUDE.md)
accurately reflect the current state of the source code.

## Source files to read first

1. **MCP tool definitions**: Read all `tools/*.py` files
   - Function signatures (name, parameters, types, defaults)
   - Docstrings (what the tool does, what each param means)
   - Return value descriptions

2. **Server registration**: Read `server.py` or equivalent
   - Which tools are actually registered and exported

## Target files to update (only if they exist — skip missing ones)

Scan for these paths relative to the project root:

- `skills/**/*.md` — skill definitions (tool tables, workflows, key notes)
- `.claude/skills/**/*.md` — same, in .claude dir
- `commands/*.md` — slash command definitions (frontmatter, param docs)
- `.claude/commands/*.md` — same, in .claude dir
- `.claude/agents/*.md` — sub-agent definitions
- `.claude/rules/*.md` — project rules and conventions
- `CLAUDE.md` — main project instructions

## What to check in each target file

For **skills** and **commands**:
- Are all current MCP tools listed? Add any missing ones.
- Are removed tools still referenced? Remove them.
- Are parameter names correct? (e.g., renamed params)
- Are parameter descriptions accurate?
- Are workflows still valid given current tool behavior?
- Are "Key Notes" accurate?

For **CLAUDE.md** and **rules**:
- Are command examples accurate? (correct tool names, params)
- Are any facts out of date? (test counts, version numbers, file paths)
- Are any described behaviors no longer true?

## Output format

Respond with a JSON object only — no prose, no code fences:

```json
{
  "files": [
    {
      "path": "skills/foo/SKILL.md",
      "action": "update",
      "current_content": "<exact current file content>",
      "new_content": "<full updated content>",
      "reason": "Added evonest_update_docs tool; updated evonest_improve description to mention all=True"
    }
  ]
}
```

Rules:
- `action` is one of: `"update"` (file exists, content changes), `"create"` (new file needed)
- Only include files that actually need changes — omit files that are already accurate
- `current_content` must be the exact content of the file as it exists now
- `new_content` must be the complete new content (not a diff)
- `reason` must be a concise, specific description of what changed and why
- Preserve the existing style, formatting, and structure of each file
- Do NOT invent new sections or restructure files beyond what is necessary
