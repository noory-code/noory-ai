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

## Tools

### evonest_init

Initialize `.evonest/` in a project directory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Path to the target project |

Creates: `config.json`, `identity.md`, `progress.json`, `backlog.json`, `scout.json`, subdirectories, updates `.gitignore`.

---

### evonest_run

Run N evolution cycles on a project.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the project |
| `cycles` | int | no | from config | Number of cycles to run |
| `dry_run` | bool | no | `false` | Skip execute + verify phases |
| `no_meta` | bool | no | `false` | Skip meta-observe even if interval reached |
| `no_scout` | bool | no | `false` | Skip scout phase even if interval reached |

Returns a summary string: `"Evonest complete: N/M cycles succeeded"`.

---

### evonest_status

Show project evolution status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Returns: project path, cycle count, success/failure/rate, last run time, running state, converged areas.

---

### evonest_history

View recent cycle history.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project` | string | yes | — | Path to the project |
| `count` | int | no | `10` | Number of recent cycles to show |

Returns formatted history with per-cycle: timestamp, status, persona, adversarial, duration, commit message.

---

### evonest_config

View or update project configuration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `settings` | dict | no | Key-value pairs to update |

Without `settings`: returns current config as JSON.
With `settings`: updates the specified keys and saves to `.evonest/config.json`.

Example: `evonest_config(project=".", settings={"model": "opus", "verify": {"build": "make"}})`

---

### evonest_identity

View or replace the project identity document.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | no | New identity content (replaces entire file) |

Without `content`: returns current `.evonest/identity.md` content.
With `content`: replaces the identity file.

---

### evonest_progress

Show detailed evolution statistics.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Returns: total cycles, success rate, per-persona weights and stats, per-adversarial stats, area touch counts, convergence flags.

---

### evonest_backlog

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

### evonest_stimuli

Inject an external stimulus for the next cycle.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | yes | Stimulus content (markdown) |

The stimulus is saved to `.evonest/stimuli/` and consumed on the next cycle.

Example: `evonest_stimuli(project=".", content="Focus on security vulnerabilities in the auth module")`

---

### evonest_decide

Drop a human decision for the next cycle.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |
| `content` | string | yes | Decision content (markdown) |

The decision is saved to `.evonest/decisions/` and consumed (deleted) on the next cycle.

Example: `evonest_decide(project=".", content="Use PostgreSQL instead of SQLite for the database layer")`

---

### evonest_scout

Run the Scout phase on-demand to search for external developments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | string | yes | Path to the project |

Extracts keywords from `identity.md`, searches externally, scores findings 1–10 against project alignment, and injects qualifying findings (≥ `scout_min_relevance_score`) as stimuli for the next cycle. Results cached in `.evonest/scout.json` to prevent duplicate injections.

Returns a summary:
```
Scout complete:
  Found: 5
  Injected as stimuli: 3
  Below threshold: 1
  Duplicates skipped: 1
```
