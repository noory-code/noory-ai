# Tool-first (Tool Usage)

Tool-selection priority when executing a flow. Work-type / language / framework agnostic.

> This file is a flow rule that is auto-loaded when placed in `.claude/rules/`. Use plain-text / backtick references only (no markdown links).

## Principle: dedicated tool > general shell

**When a dedicated tool that fits the task exists, use it first.** Do not substitute the general shell (Bash). Dedicated tools provide structured output, OS independence, and permission stability, so the input quality for judgment is higher.

| Task | Preferred tool | Avoid (shell substitute) | Reason |
|------|----------|--------------|------|
| Read a file | `Read` | `cat` / `head` / `tail` | Structured output + image/PDF/notebook support |
| Search files (by name) | `Glob` | `find` | OS-independent + fast |
| Search content | `Grep` | shell `grep` / `rg` | Structured + permission-stable |
| Edit a file | `Edit` / `Write` | `sed` / `awk` / `echo >` | Exact replacement + pre-validation |
| Work with external systems | The relevant MCP tool | Shell workaround | Server contract + auth + structured |

> Example: if the project supplies per-language LSP/MCP tools, prefer them over a general shell call for the same task. But if the project does not supply a dedicated tool, the shell may be used (optional linkage).

## File modification — dedicated-tool ladder

Modify file content in the following order. Each step down is more of a last resort:

1. `Edit` — text replacement (single/multiple)
2. `Write` — new file / full replacement
3. Terminal (`mv` / `rm`) — file move/delete only (no content modification)
4. Script — last resort (only for batch processing of 100+)

- Writing file content via a script / one-liner = **forbidden tool bypass**. Even for batch processing, prefer repeated `Edit` when possible.
- For batch scripts, **prefer cross-platform Python** (parity with the plugin OS-compatibility policy — the plugin's own scripts are pure Python). If an OS-native script is unavoidable, match the host OS (macOS/Linux → shell, Windows → PowerShell) — do not force a single OS-native default.

## Distinction from `skill-trigger-obligation`

The two rules are **at different layers** — do not confuse them.

- **`skill-trigger-obligation`** (`flow-rules.md`): when a user request matches a skill `description`, there is an **obligation to call the Skill tool** ("shall I call the skill").
- **This rule (`tool-usage`)**: the priority of **which tool to use** when executing that same task ("what to execute the tool with").

## Application

- At the start of a task, first check whether a dedicated tool exists, and use it first if so.
- Use the general shell only when the dedicated tool cannot do it (compound pipes, no dedicated tool provided, etc.).
- When using the shell, use only commands compatible with both macOS and Windows (avoid POSIX-only — parity with the plugin OS-compatibility policy).
