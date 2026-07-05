---
description: Show Skill tool usage statistics — top used + unused skills
argument-hint: "[--top N] [--period today|week|30d|all] [<skill_name>]"
---

# /skill-stats

You show the user Claude Code's Skill-tool call statistics.

## Input parsing

Argument: `$ARGUMENTS`. If empty, defaults to `--top 10 --period all`.

Supported options:
- `--top N` — the top N most-used (default 10)
- `--period today|week|30d|all` — the aggregation period (default `all`)
- `<skill_name>` — passing a single argument switches to detail mode for that skill

Option-parsing rules:
- A single token that does not start with `--` → **single-skill detail mode**
- Otherwise → **summary mode**

## Data sources

1. **Log file**: `$HOME/.claude/skill-usage.jsonl`
   - Read the file (empty/missing → treat as EMPTY).
   - If the file is missing or empty, print "No call history yet. Invoke any skill once and try again." and exit.
   - If the log stays empty, guide the user through the troubleshooting order: `python3` availability / hook-load check.
2. **Full skill list**: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/list-all-skills.py" | sort -u`
   - If the output is empty, tell the user to consult the troubleshooting guide below.
   - In particular, guide them to check the `CLAUDE_PLUGIN_ROOT` path, that `python3` is on PATH, and whether an installed `SKILL.md` exists.

## Aggregation

Each log line is JSONL: `{ts, skill, args, cwd, session_id}`.

- `--period today` = on or after UTC today (`YYYY-MM-DD`)
- `--period week` = from 7 days ago
- `--period 30d` = from 30 days ago
- `--period all` = no filter

Per-skill aggregation: `count`, `first_ts`, `last_ts`.
`unused_for` = (current UTC) - `last_ts`. If calls are 0, then `∞`.

`unused_for` format:
- < 1 day → `<1 day`
- 1–59 days → `N days`
- 60 days or more → `N months` (30 days = 1 month, approximated)
- `∞` → never invoked

## Output — single-skill detail mode

```text
# <skill_name>

- Total calls: N
- First call: <ISO ts> (or "—" if 0)
- Last call: <ISO ts> (or "—" if 0)
- Unused for: <unused_for>

## Last 5 calls

| ts | cwd | args |
|---|---|---|
| 2026-05-24T... | &lt;cwd&gt; | "..." |
```

## Output — no data / discovery failure

If the log file is missing or empty:

```text
No call history yet. Invoke any skill once and try again.

If it stays empty, check the troubleshooting steps in order:
1. python3: available on PATH (python3 --version)
2. hook load: whether the skill-usage PreToolUse hook exists in /hooks
3. settings: .flow/settings.json skill_usage.enabled is not false
```

If the full-skill-list discovery output is empty:

```text
Could not discover the skill list.

Consult the troubleshooting guide and check the following:
1. Whether CLAUDE_PLUGIN_ROOT points at the flow plugin root
2. Whether python3 "${CLAUDE_PLUGIN_ROOT}/scripts/list-all-skills.py" runs directly
3. Whether a SKILL.md exists in the installed user/project/plugin skill directories
```

## Output — summary mode (default)

```text
# Skill usage statistics (period: <value>)

Total captured calls: N (after applying the period filter)
Total registered skills: M

## Most-used skills (top <N>)

| Skill | Calls | Last Used | Unused For |
|---|---:|---|---|
| <skill> | 42 | 2026-05-26 | <1 day |
| ... |

## Unused skills

| Skill | Calls | Last Used | Unused For |
|---|---:|---|---|
| <skill> | 0 | — | ∞ |
| <skill> | 3 | 2026-04-15 | 41 days |

> Scope limit: this section enumerates **only installed skills that have a SKILL.md on disk** (user-global / project-local + marketplace plugins). Built-in skills (deep-research, verify, code-review, run, init, simplify, loop, schedule, etc.) and connector skills (slack:*, atlassian:*, etc.) have no SKILL.md on disk — **so when invoked they are counted under "Most-used skills", but they will never appear under "Unused skills" here.** In other words, a skill absent from this table ≠ definitely unused. Trust the cleanup judgment only for installed plugin skills.
```

**Most-used skills section**: sort by `count desc`, top N.

**Unused skills section**: the union of the following two groups (against the full skill list).
- `count == 0` (never invoked) — `∞`
- `count > 0` but `unused_for >= 30 days`

`∞` at the very top, then sort by `unused_for desc`.

This "full skill list" includes only the SKILL.md files that `list-all-skills.py` discovered on disk (see the "Scope limit" note in the output block above). Built-in / connector skills have no SKILL.md, so they never surface as `count == 0` candidates; therefore **always include the scope-limit note above verbatim in the output table** so the user does not overtrust "unused skill = cleanup target".

The join between the aggregation and the list is based on **skill-name string equality**. Plugin skills match on both sides via the `<plugin>:<skill>` namespace, but for user/project skills, if the namespace notation in the log (the `skill` field) and in the `list-all-skills.py` output disagree, the same skill can be bucketed separately into both sections.

## Output tone

- Markdown tables only. No charts / comments / emoji.
- Keep the column order above exactly (so the user can grep / script it).
- If argument parsing fails, print only the exact one-line usage.
