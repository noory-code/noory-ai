# Evonest

**MCP-native autonomous code evolution engine for Claude Code.**
Evonest connects directly to Claude Code's tool ecosystem — not as a standalone CLI, but as a first-class participant that shares context, tools, and conversation continuity with your existing Claude session.

## Why Evonest?

Most AI coding tools give you a single perspective. Evonest rotates through 20 specialist personas — picking one per cycle, weighted by past success, so perspectives that actually improve your project run more often over time.

| | Aider / Cursor | GitHub Copilot Workspace | **Evonest** |
|--|--|--|--|
| Integration | Standalone CLI / editor | Web UI | **MCP-native — lives inside Claude Code** |
| Perspectives | Single AI | Predefined workflow | **20 rotating personas, weighted by success** |
| Context Continuity | Session-local | Isolated web session | **Shares Claude Code conversation + tools** |
| Safety | Manual recovery | Manual recovery | **Auto-revert on failed build/test** |
| Learning | None | None | **Adaptive weights — successful personas run more often** |
| Output | Local commits | PR (web) | **Commit or PR — your choice** |

Each cycle, Evonest picks **one specialist persona**, runs it as a fully independent Claude process with no shared context from prior cycles, and lets natural selection determine which perspectives deserve more weight. Aider launches a single AI per conversation; Evonest launches a fresh process per cycle.

## Proven on Evonest itself

Evonest evolves its own codebase through the same cycle. Real findings from 164 executed proposals:

| Finding | Persona | Outcome |
|---------|---------|---------|
| `subprocess.run(shell=True)` with user config values — shell injection | security-auditor | Fixed: `shlex.split()` + `shell=False` |
| `TimeoutExpired` handler missing `process.kill()` — zombie processes | chaos-engineer | Fixed: `process.kill()` + `process.wait()` in timeout handler |
| Bare `except Exception: pass` in 19 locations — silent failures | observability-advocate | Fixed: module-level logger with `exc_info=True` throughout |
| Path slugification allows `../../../etc/passwd` traversal | security-auditor | Fixed: validate resolved path stays within `.evonest/` |

0 regressions — auto-revert caught everything.

## Install

### Claude Code Plugin

```
/plugin marketplace add noory-code/noory-ai
/plugin install evonest@noory-code/noory-ai
```

Slash commands (`/evonest:analyze`, `/evonest:improve`, `/evonest:evolve`) become available immediately.

### Manual

```bash
pip install evonest   # or: uvx evonest
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
   → creates .evonest/ (identity.md, config.json, proposals/, history/, ...)
   → edit identity.md: mission, values, boundaries

2. evonest_analyze(project="...")
   → scans codebase, saves all improvements as proposals — no code changes

3. evonest_proposals(project="...")
   → review pending proposals, then:
   evonest_improve(project="...", proposal_id="<filename>")
   → execute one proposal → verify → commit/PR
```

**First time? Start with `analyze`.** No code is changed — you review proposals before anything executes.

### .evonest/ layout

```
.evonest/
├── identity.md        ← describe your project (edit this!)
├── config.json        ← verify commands, model, turn limits
├── progress.json      ← persona weights and area touch counts
├── backlog.json       ← tracked improvements across cycles
├── proposals/         ← pending improvement proposals
├── history/           ← cycle logs
├── stimuli/           ← injected external context
├── decisions/         ← human decisions for next cycle
└── (generated)        ← observe.txt, plan.txt, advice.json per cycle
```

## Safety

- **Git stash before execute** — working tree stashed before any change
- **Verify phase** — runs `verify.build` and `verify.test` after every change
- **Auto-revert on failure** — if verification fails, changes are discarded
- **Lock file** — prevents concurrent runs from colliding
- **Turn limits** — every Claude subprocess has a hard cap on API calls
- **Cautious mode** — `--cautious` shows the plan and waits for approval before executing

Configure verify commands in `.evonest/config.json`:

```json
{
  "verify": {
    "build": "npm run build",
    "test":  "npm test"
  }
}
```

## Cost

Evonest runs Claude subprocesses. Estimated cost per cycle with `claude-sonnet` (default):

| Phase | Max turns | Typical cost |
|-------|-----------|--------------|
| Observe | 25 | ~$0.05–0.15 |
| Plan | 15 | ~$0.03–0.08 |
| Execute | 25 | ~$0.05–0.15 |
| **Per cycle** | | **~$0.15–0.40** |

With `max_cycles_per_run: 5` (default), one run costs roughly **$0.75–2.00**. Actual cost depends on codebase size and complexity; phases typically use 5–15 of the configured maximum turns.

**To reduce cost:**
- Switch to `haiku` — 5–7× cheaper
- Use `observe_mode: "quick"` — shorter observe phase
- Use `--cautious` — cancel if the plan doesn't look worth executing
- Use `analyze` mode first — read-only, lets you review before spending on execution

## Modes

| Mode | What it does |
|------|--------------|
| **analyze** | Observe codebase → save all improvements as proposals. No code changes. |
| **improve** | Execute one proposal → verify → commit/PR. |
| **evolve** | Full cycle: Observe → Plan → Execute → Verify → commit/PR. |

```bash
/evonest:analyze
/evonest:improve
/evonest:evolve

evonest analyze . [--all-personas] [--observe-mode quick|deep]
evonest improve . [--proposal <filename>]
evonest evolve  . [--cycles N] [--cautious]
```

## How Mutations Work

Every cycle, Evonest picks a **persona** and optionally pairs it with an **adversarial challenge**.

### Personas (20 built-in)

| Group | Personas |
|-------|----------|
| **tech** (8) | performance-engineer, new-user, api-designer, architect, future-proofer, contrarian, ecosystem-scanner, domain-modeler |
| **biz** (8) | product-thinker, product-strategist, spec-reviewer, growth-hacker, monetization-analyst, ux-critic, competitor-analyst, cto-reviewer |
| **quality** (4) | security-auditor, chaos-engineer, refactoring-expert, observability-advocate |

Selection is weighted by past success. You can enable/disable any persona or group in `.evonest/config.json`.

### Adversarial Challenges (8 built-in)

With 20% probability per cycle, a challenge layers on top of the persona:
`break-interfaces`, `corrupt-state`, `scale-100x`, `remove-feature`, and more.

Set `adversarial_probability: 0.0` to disable, or force one with `adversarial_id`.

### Dynamic Mutations

Evonest generates project-specific personas and adversarials via meta-observe — stored in `.evonest/dynamic-personas.json` and `.evonest/dynamic-adversarials.json`, pruned automatically by effectiveness.

## Adaptive Intelligence

Persona weights update after every cycle (floor: 0.2, cap: 3.0). Successful personas run more often; underperforming ones are deprioritized but never silenced. A recency bonus encourages exploration of unused perspectives.

If the same directory is touched 3+ times without a clean pass, it's flagged as a convergence zone — the next cycle receives a warning to look elsewhere or try a different approach.

See [docs/architecture.md](docs/architecture.md) for weight formula and convergence details.

## identity.md

The most important file. Lives at `.evonest/identity.md` — created by `evonest_init`.

Describe your project's mission, core values, current phase, quality standards, and boundaries (files Evonest must not touch). Evonest reads this at the start of every cycle — the richer it is, the better the proposals.

See [docs/identity.md](docs/identity.md) for the full guide and template.

## Configuration

Settings in `.evonest/config.json`. Engine defaults < project config < runtime args.

See [docs/configuration.md](docs/configuration.md) for all options.

### Team Workflow (Pull Request Mode)

Set `code_output: "pr"` to have Evonest open pull requests instead of direct commits — designed for teams where changes go through code review.

## Self-Evolution

This repo has its own `.evonest/` and evolves through the same cycle. See [docs/self-evolution.md](docs/self-evolution.md).

## License

MIT
