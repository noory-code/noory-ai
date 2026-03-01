# Evonest

**MCP-native autonomous code evolution engine for Claude Code.**
Evonest connects directly to Claude Code's tool ecosystem — not as a standalone CLI, but as a first-class participant that shares context, tools, and conversation continuity with your existing Claude session.

## Why Evonest?

Most AI coding tools give you a single perspective. Evonest rotates through 19 specialist personas — security auditor, chaos engineer, performance analyst, domain modeler, and more — picking one per cycle, weighted by past success, so the perspectives that actually improve your project run more often over time.

### Why 19 personas?

A single AI can only offer one perspective at a time. Real projects require security, performance, maintainability, and product strategy — often in conflict with each other.

Each cycle, Evonest picks **one specialist persona**, runs it as a fully independent Claude process, and lets natural selection determine which perspectives deserve more weight.

**Adaptive learning:**
Successful personas gain weight. If security improvements keep passing, security-auditor runs more often. Personas that propose unnecessary refactoring are automatically deprioritized.

**Diversity prevents tunnel vision:**
Aider/Cursor operate as a single AI and try only one approach. GitHub Copilot Workspace is locked into a predefined workflow. Evonest rotates through 19 independent perspectives, and natural selection finds the optimal combination for your specific project.

| | Aider / Cursor | GitHub Copilot Workspace | **Evonest** |
|--|--|--|--|
| Integration | Standalone CLI / editor | Web UI | **MCP-native — lives inside Claude Code** |
| Perspectives | Single AI | Predefined workflow | **19 rotating personas, weighted by success** |
| Context Continuity | Session-local | Isolated web session | **Shares Claude Code conversation + tools** |
| Safety | Manual recovery | Manual recovery | **Auto-revert on failed build/test** |
| Learning | None | None | **Adaptive weights — successful personas run more often** |
| Output | Local commits | PR (web) | **Commit or PR — your choice** |

### Advantages of being MCP-native

**Context continuity:**
Evonest runs inside your Claude Code session, so it shares conversation history, opened files, and executed commands. Aider operates as a separate process with no knowledge of your prior work. Copilot Workspace is isolated in a web UI.

**Native tool sharing:**
Running `/evonest:analyze` uses Claude Code's Read, Glob, Grep, Edit, and Write tools directly — no separate file access permissions or redundant codebase parsing.

**Single environment:**
Project settings, git state, environment variables, and dependencies are identical to Claude Code's environment. Aider is a separate CLI prone to environment mismatches. Copilot Workspace runs in a cloud environment that cannot reflect local configuration.

## What competitors cannot do

### Aider / Cursor cannot switch personas

Aider and Cursor operate as a single AI instance. You can ask "analyze from a security perspective," but it's the same model interpreting a different prompt — no independence between perspectives, and prior conversation context introduces bias.

Evonest launches a **new Claude process** for each cycle. security-auditor and performance-analyst run as completely independent sessions with no knowledge of each other's suggestions.

### GitHub Copilot Workspace cannot learn autonomously

Copilot Workspace locks you into an "Issue → Plan → Code → PR" workflow. It does not learn which approaches are effective, and there is no per-project optimization.

Evonest recalculates persona weights after every cycle. If security improvements keep succeeding, security-auditor frequency increases. Personas that propose unnecessary refactoring are automatically deprioritized. After 50 cycles, a persona distribution tailored to your project emerges.

## Proven on Evonest itself

Evonest evolves its own codebase through the same cycle. Here are real findings from self-evolution:

| Finding | Persona | Outcome |
|---------|---------|---------|
| `subprocess.run(shell=True)` with user config values — shell injection | security-auditor | Fixed: `shlex.split()` + `shell=False` |
| `TimeoutExpired` handler missing `process.kill()` — zombie processes | chaos-engineer | Fixed: `process.kill()` + `process.wait()` in timeout handler |
| Bare `except Exception: pass` in 19 locations — silent failures | spec-reviewer | Fixed: module-level logger with `exc_info=True` throughout |
| Path slugification allows `../../../etc/passwd` traversal | security-auditor | Fixed: validate resolved path is within `.evonest/` |

164 proposals executed to date. 0 regressions (auto-revert caught everything).

## Install

### Claude Code Plugin

**1. Add marketplace** (points to https://github.com/noory-code/noory-ai)
```
/plugin marketplace add noory-code/noory-ai
```

**2. Install plugin**
```
/plugin install evonest@noory-code/noory-ai
```

Slash commands (`/evonest:analyze`, `/evonest:improve`, `/evonest:evolve`) become available immediately.

### Manual

```bash
uvx evonest
# or: pip install evonest
```

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

## Quick Start

```
1. evonest_init(project="/path/to/project")
   → creates .evonest/ with identity.md, config.json, proposals/, ...
   → edit identity.md: mission, core values, boundaries (DO NOT touch list)

2. /evonest:analyze  (or: evonest_analyze(project="..."))
   → scans codebase, saves all improvements as proposals (no code changes)
   → review with: evonest_proposals(project="...")

3. evonest_improve(project="...", proposal_id="<filename>")
   → execute one proposal → verify → commit/PR
```

**First time? Start with `analyze`.** It only reads your codebase and saves proposals — no code is changed. You stay in control of what gets executed.

### .evonest/ layout

```
.evonest/
├── identity.md       ← describe your project (edit this!)
├── config.json       ← verify commands, model, etc.
├── proposals/        ← pending improvement proposals
│   └── done/         ← executed proposals
├── history/          ← cycle logs
└── ...               ← observe.md, plan.md (generated per cycle)
```

## Safety

Evonest modifies your code autonomously — so it has multiple layers of protection:

- **Git stash before execute**: the working tree is stashed before any change
- **Verify phase**: runs `verify.build` and `verify.test` after every change
- **Auto-revert on failure**: if verification fails, changes are discarded automatically
- **Lock file**: prevents concurrent runs from colliding
- **Turn limits**: every Claude subprocess has a hard cap on API calls
- **Cautious mode**: `--cautious` shows the plan and waits for your approval before executing

Configure verify commands in `.evonest/config.json`:

```json
{
  "verify": {
    "build": "npm run build",
    "test":  "npm test"
  }
}
```

Without verify commands, Evonest still reverts on exceptions but cannot check functional correctness.

## Cost

Evonest runs Claude subprocesses — here's what to expect with `claude-sonnet` (default):

| Phase | Typical turns | Estimated cost |
|-------|--------------|----------------|
| Observe | ~10 turns | ~$0.05 |
| Plan | ~5 turns | ~$0.03 |
| Execute | ~10 turns | ~$0.10 |
| **Per cycle total** | | **~$0.15–0.25** |

With `max_cycles_per_run: 5` (default), one full run costs roughly **$0.75–1.25**.

**To reduce cost:**
- Switch to `haiku`: `evonest_config(project="...", key="model", value="haiku")` — 5–7× cheaper
- Use `observe_mode: "quick"` — shorter observe phase, fewer turns
- Use `--cautious` — pauses before execute; cancel if the plan doesn't look worth it
- Use `analyze` mode first — read-only, cheap, lets you review proposals before spending on execution

> Cost estimates are approximate and depend on codebase size and complexity.

## Modes

| Mode | What it does |
|------|--------------|
| **analyze** | Observe codebase → save ALL improvements as proposals. No code changes. |
| **improve** | Execute one proposal → verify → commit/PR. |
| **evolve** | Full autonomous cycle: Observe → Plan → Execute → Verify → commit/PR. |

```bash
# Plugin slash commands
/evonest:analyze
/evonest:improve
/evonest:evolve

# CLI
evonest analyze . [--all-personas] [--observe-mode quick|deep]
evonest improve . [--proposal <filename>]
evonest evolve  . [--cycles N] [--cautious] [--all-personas]
```

**Cautious mode** (`--cautious`): pauses after planning, shows the plan, waits for approval before executing.

## How Mutations Work

Every cycle, Evonest picks a **persona** — a specialist perspective — and optionally pairs it with an **adversarial challenge**. This is the core mechanism that prevents single-perspective tunnel vision.

### Personas (19 built-in)

Each persona brings a distinct angle to the codebase:

| Group | Example Personas |
|-------|-----------------|
| **tech** | security-auditor, chaos-engineer, performance-analyst, test-coverage-analyst, api-designer, documentation-writer, ecosystem-scanner, code-archaeologist |
| **biz** | product-strategist, competitor-analyst, monetization-analyst, domain-modeler |
| **quality** | spec-reviewer, refactoring-specialist, dependency-auditor, technical-debt-analyst |

**Selection is weighted**: after each cycle, successful personas get higher weights. Over time, the personas that actually improve your project run more often.

**You control which personas run:**

```json
// .evonest/config.json
{
  "active_groups": ["tech"],
  "personas": {
    "chaos-engineer": false,
    "monetization-analyst": false
  },
  "adversarials": {
    "break-interfaces": false
  }
}
```

### Adversarial Challenges (8 built-in)

With 20% probability per cycle, a challenge is layered on top of the persona:

- `break-interfaces` — deliberately stress API boundaries
- `corrupt-state` — look for state corruption opportunities
- `scale-100x` — assume 100x current load; find bottlenecks
- `remove-feature` — identify features that should not exist
- ... and more

Set `adversarial_probability: 0.0` to disable, or force one with `adversarial_id`.

### Dynamic Mutations

Evonest generates new personas and adversarials based on your project — stored in `.evonest/dynamic-personas.json` and `.evonest/dynamic-adversarials.json`. These are pruned automatically based on effectiveness.

## MCP Tools

| Tool | Description |
|------|-------------|
| `evonest_init` | Initialize `.evonest/` in a project |
| `evonest_analyze` | Observe and save all improvements as proposals (no code changes) |
| `evonest_improve` | Execute one proposal → verify → commit/PR |
| `evonest_evolve` | Full cycle: Observe → Plan → Execute → Verify → commit/PR |
| `evonest_proposals` | List pending proposals (sorted by priority) |
| `evonest_status` | Show cycle count, success rate, convergence areas |
| `evonest_history` | View recent cycle history |
| `evonest_config` | View/update project configuration |
| `evonest_identity` | View/update project identity document |
| `evonest_progress` | Detailed stats: per-persona weights, area touch counts |
| `evonest_backlog` | Manage improvement backlog |
| `evonest_stimuli` | Inject external stimulus for the next cycle |
| `evonest_decide` | Drop a human decision for the next cycle |
| `evonest_scout` | Run scout phase — search for external developments |
| `evonest_personas` | List, enable, or disable personas and adversarial challenges |
| `evonest_run` | *(deprecated — use `evonest_evolve`)* |

All tools take `project` (absolute path) as their first argument.

## Adaptive Intelligence

Evonest learns from its own history to avoid spinning in circles and to invest more effort where it succeeds.

### Convergence Detection

If Evonest touches the same codebase area (directory) **3 or more times**, that area is flagged as a convergence zone. The next cycle receives an explicit warning: "This area may be stuck — look elsewhere or try a different approach."

The threshold of 3 is empirical: 1–2 touches are normal iteration; 3+ touches without a clean pass suggests the improvement is blocked or the approach needs to change.

Convergence flags are visible in `evonest_status` and `evonest_progress`.

### Adaptive Persona Weights

Every persona starts with weight `1.0`. After each cycle:

- **Successful cycle** → persona weight increases (capped at 3.0)
- **Failed cycle** → persona weight decreases (floor at 0.2)
- **Recency bonus** → a persona unused for 3+ cycles gets a small boost (encourages exploration)

The floor at 0.2 prevents any persona from being permanently silenced. The cap at 3.0 prevents any single persona from monopolizing all cycles.

Over dozens of cycles, the persona distribution shifts toward what actually works for your project. Run `evonest_progress` to see current weights.

### Meta-Observe

Every 5 cycles (configurable), Evonest runs a meta-observe pass: it reads its own history and generates strategic advice — which areas need attention, which patterns are working, what to try next. This advice is stored in `.evonest/advice.json` and injected into future cycles.

## identity.md

The most important file. Lives at `.evonest/identity.md`.

`evonest_init` creates a template — but the real value comes from filling it in and keeping it updated as your project evolves. The richer this file, the better the proposals.

**Start with the template, then grow it:**

```markdown
## Mission
One sentence describing what this project does.

## Core Values
- "Zero external dependencies"
- "Type safety everywhere"
- "Test coverage before shipping"

## Current Phase
"Pre-launch. Building core features only."

## Quality Standards
- "All tests must pass: npm test"
- "No TypeScript errors: tsc --noEmit"

## Boundaries (DO NOT touch)
- .evonest/
- migrations/
```

**Keep it alive**: update `Current Phase` as you ship features, add new `Core Values` as patterns emerge, tighten `Boundaries` as the codebase matures. Evonest reads this file at the start of every cycle — it shapes every proposal.

## Configuration

Settings in `.evonest/config.json`. Engine defaults < project config < runtime args.

| Field | Default | Description |
|-------|---------|-------------|
| `model` | `"sonnet"` | Claude model (`sonnet`, `opus`, `haiku`) |
| `max_cycles_per_run` | `5` | Cycles per invocation |
| `verify.build` | `null` | Build command (e.g., `npm run build`) |
| `verify.test` | `null` | Test command (e.g., `npm test`) |
| `code_output` | `"commit"` | `"commit"` = direct commit; `"pr"` = open pull request |
| `observe_mode` | `"auto"` | `auto`, `quick`, or `deep` |
| `adversarial_probability` | `0.2` | Chance of adversarial challenge per cycle |
| `active_groups` | `[]` | Persona group filter (`[]` = all groups) |
| `personas` | `{all: true}` | Per-persona enable/disable toggle map |
| `adversarials` | `{all: true}` | Per-adversarial enable/disable toggle map |
| `scout_enabled` | `true` | Enable external ecosystem scout |
| `language` | `"english"` | Output language for proposals and reports |

Full configuration reference: [docs/configuration.md](docs/configuration.md)

### Team Workflow (Pull Request Mode)

Set `code_output: "pr"` to have Evonest create branches and open pull requests instead of direct commits:

```json
{
  "code_output": "pr"
}
```

This is designed for team environments where:

- Multiple developers share the same repository
- Changes go through code review before merging
- Evonest proposals appear as reviewable PRs rather than direct commits

Each PR includes the proposal description, the persona that generated it, and the verify results. Teams can run Evonest in `analyze` mode to generate proposals, then route chosen proposals through the normal PR review process via `improve`.

## Self-Evolution

Evonest runs on itself — this repo has its own `.evonest/` and evolves through the same cycle.

See [docs/self-evolution.md](docs/self-evolution.md) for setup and cautious-mode workflow.

## CLI Reference

```bash
evonest init /path/to/project

evonest analyze .
evonest analyze . --all-personas
evonest analyze . --observe-mode deep

evonest improve .
evonest improve . --proposal <filename>

evonest evolve . --cycles 3
evonest evolve . --cautious
evonest evolve . --all-personas

evonest status   .
evonest history  . -n 5
evonest progress .
evonest config   . --set model opus
evonest identity .
evonest backlog  .
evonest backlog  . add --title "Fix auth tests"
```

## License

MIT
