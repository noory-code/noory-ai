# Evonest MCP Tools

## Registration

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "evonest": {
      "command": "uvx",
      "args": ["evonest"]
    }
  }
}
```

Evonest data lives under `.noory/evonest/` in the target project (a legacy
`.evonest/` directory is migrated automatically on first access).

## Tools

18 tools are registered (`src/evonest/server.py`), grouped below by purpose.

### Setup

#### evonest_init

Initialize `.noory/evonest/` in a project directory.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | yes | — | Path to the target project |
| `level` | string | no | `"standard"` | Analysis depth preset: `"quick"` (haiku), `"standard"` (sonnet), `"deep"` (opus) |

Creates: `config.json`, `identity.md`, `progress.json`, `backlog.json`, dynamic mutation files, `scout.json`, subdirectories, updates `.gitignore`.

---

### Modes

#### evonest_analyze

Run the Observe phase only, saving ALL identified improvements as proposals. No code is changed.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Absolute path to target project |
| `persona_id` | string | no | — | Force a specific persona ID |
| `adversarial_id` | string | no | — | Force adversarial ID, or `"none"` to disable |
| `group` | string | no | — | Persona group filter (`"biz"`, `"tech"`, `"quality"`) |
| `all_personas` | bool | no | `false` | Run every persona once; each produces its own batch of proposals |
| `observe_mode` | string | no | — | `"auto"`, `"quick"`, or `"deep"` |
| `level` | string | no | — | Analysis depth preset, overrides `active_level` from config |

Runs in the background and returns immediately with the process PID and log path. Proposals are saved to `.noory/evonest/proposals/` for human review.

#### evonest_evolve

Run the full evolution cycle: Observe → Plan → Execute → Verify → commit/PR.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Absolute path to target project |
| `cycles` | int | no | from config | Number of cycles to run |
| `no_meta` | bool | no | `false` | Skip meta-observe |
| `no_scout` | bool | no | `false` | Skip scout phase |
| `observe_mode` | string | no | — | `"auto"`, `"quick"`, or `"deep"` |
| `persona_id` | string | no | — | Force a specific persona |
| `adversarial_id` | string | no | — | Force adversarial, or `"none"` to disable |
| `group` | string | no | — | Persona group filter |
| `all_personas` | bool | no | `false` | Run every persona once |
| `cautious` | bool | no | `false` | Pause after Plan phase and return a plan summary |
| `resume` | bool | no | — | With a paused cautious session: `true` to execute, `false` to cancel |
| `level` | string | no | — | Analysis depth preset, overrides `active_level` from config |

Runs in the background and returns immediately with the process PID and log path.

#### evonest_improve

Execute a proposal: select → Execute → Verify → commit/PR. No Observe or Plan phases run — the proposal content is the plan.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Absolute path to target project |
| `proposal_id` | string | no | — | Bare filename of the proposal to execute; if omitted, auto-selects by priority then age |
| `all` | bool | no | `false` | Process all pending proposals sequentially until none remain |

Blocks until the proposal is fully processed (build + tests + commit).

#### evonest_run — DEPRECATED

**Deprecated: use [`evonest_evolve`](#evonest_evolve) instead.** Kept for backward compatibility only (`src/evonest/tools/run.py`); emits a `DeprecationWarning` on every call and forwards to the same `run_cycles` engine call as `evonest_evolve`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the project |
| `cycles` | int | no | from config | Number of cycles to run |
| `dry_run` | bool | no | `false` | Skip execute + verify phases (redirects to analyze-like behavior) |
| `no_meta` | bool | no | `false` | Skip meta-observe even if interval reached |
| `no_scout` | bool | no | `false` | Skip scout phase even if interval reached |
| `observe_mode` | string | no | — | `"auto"`, `"quick"`, or `"deep"` |
| `persona_id` | string | no | — | Force a specific persona |
| `adversarial_id` | string | no | — | Force adversarial, or `"none"` to disable |
| `group` | string | no | — | Persona group filter |
| `all_personas` | bool | no | `false` | Run every persona once |

---

### Proposals & Personas

#### evonest_proposals

List pending proposals or mark one as done.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Absolute path to the target project |
| `action` | string | no | `"list"` | `"list"` — show pending proposals. `"done"` — mark a proposal completed and move it to `proposals/done/` |
| `filename` | string | no | `""` | Required when `action="done"`. Bare filename of the proposal |

#### evonest_personas

List, enable, or disable personas and adversarials.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the target project |
| `action` | string | no | `"list"` | `"list"`, `"enable"`, or `"disable"` |
| `ids` | list[string] | no | — | Persona or adversarial IDs to enable/disable |
| `group` | string | no | — | Filter by group (`"biz"`, `"tech"`, `"quality"`) — list action only |

---

### Identity

#### evonest_identity

View or replace the project identity document (`.noory/evonest/identity.md`).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | no | New identity content (replaces entire file) |

Without `content`: returns current identity content. With `content`: replaces the identity file.

#### evonest_identity_refresh

Re-draft `identity.md` by having Claude explore the project (same approach `evonest_init` uses to seed the initial draft).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Returns a JSON object with `current` and `draft` keys so the caller can review the proposed changes before applying them via `evonest_identity`.

---

### Status & Introspection

#### evonest_status

Show project evolution status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Returns: project path, cycle count, success/failure/rate, last run time, running state, converged areas.

#### evonest_history

View recent cycle history.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the project |
| `count` | int | no | `10` | Number of recent cycles to show |

Returns formatted history with per-cycle: timestamp, status, persona, adversarial, duration, commit message.

#### evonest_progress

Show detailed evolution statistics.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Returns: total cycles, success rate, per-persona weights and stats, per-adversarial stats, area touch counts, convergence flags.

#### evonest_config

View or update project configuration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `settings` | dict | no | Key-value pairs to update |

Without `settings`: returns current config as JSON. With `settings`: updates the specified keys and saves to `.noory/evonest/config.json`.

Example: `evonest_config(project=".", settings={"model": "opus", "verify": {"build": "make"}})`

---

### Backlog

#### evonest_backlog

Manage the improvement backlog.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the project |
| `action` | string | no | `"list"` | One of: `list`, `add`, `remove`, `prune` |
| `item` | dict | no | — | Item data for add/remove actions |

Actions:
- `list` — Show all backlog items
- `add` — Add an item. `item` should have `title` (required), `priority` (optional), `category` (optional)
- `remove` — Remove an item. `item` should have `id`
- `prune` — Remove old completed/stale items

---

### Guidance for the Next Cycle

#### evonest_stimuli

Inject an external stimulus for the next cycle.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | yes | Stimulus content (markdown) |

The stimulus is saved to `.noory/evonest/stimuli/` and consumed on the next cycle.

Example: `evonest_stimuli(project=".", content="Focus on security vulnerabilities in the auth module")`

#### evonest_decide

Drop a human decision for the next cycle.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | yes | Decision content (markdown) |

The decision is saved to `.noory/evonest/decisions/` and consumed (deleted) on the next cycle.

Example: `evonest_decide(project=".", content="Use PostgreSQL instead of SQLite for the database layer")`

---

### Scout

#### evonest_scout

Run the Scout phase on-demand to search for external developments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Extracts keywords from `identity.md`, searches externally, scores findings 1–10 against project alignment, and injects qualifying findings (≥ `scout_min_relevance_score`) as stimuli for the next cycle. Results cached in `.noory/evonest/scout.json` to prevent duplicate injections.

Returns a summary:
```
Scout complete:
  Found: 5
  Injected as stimuli: 3
  Below threshold: 1
  Duplicates skipped: 1
```

---

### Docs Sync

#### evonest_update_docs

Sync Claude Code files (skills, commands, agents, rules, CLAUDE.md) with the project's current MCP tool definitions and docstrings.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Absolute path to the target project |
| `target` | string | no | `"all"` | One of: `"all"`, `"skills"`, `"commands"`, `"agents"`, `"rules"`, `"claude_md"` |
| `dry_run` | bool | no | `true` | `true` — return proposed changes as JSON without writing. `false` — apply changes to disk |
