# Evonest Architecture

## Module Map

```
src/evonest/
├── __init__.py           # Version, entry point router (MCP server vs CLI)
├── __main__.py           # python -m evonest
├── server.py             # FastMCP server (stdio transport)
├── cli.py                # argparse CLI (init, run, status, config, ...)
│
├── tools/                # MCP tool definitions (thin wrappers)
│   ├── run.py            # evonest_run → core.orchestrator.run_cycles
│   ├── init.py           # evonest_init → core.initializer.init_project
│   ├── status.py         # evonest_status → core.state.ProjectState.summary
│   ├── history.py        # evonest_history → core.history.get_recent_history
│   ├── config.py         # evonest_config → core.config.EvonestConfig
│   ├── identity.py       # evonest_identity → core.state read/write identity
│   ├── progress.py       # evonest_progress → core.progress.get_progress_report
│   ├── backlog.py        # evonest_backlog → core.backlog.manage_backlog
│   ├── stimuli.py        # evonest_stimuli → core.state.add_stimulus
│   ├── decide.py         # evonest_decide → core.state.add_decision
│   └── scout.py          # evonest_scout → core.scout
│
├── core/                 # Engine logic (MCP-agnostic)
│   ├── state.py          # ProjectState — all .evonest/ paths + file I/O
│   ├── config.py         # EvonestConfig — 3-tier resolution dataclass
│   ├── lock.py           # EvonestLock — context manager lock file
│   ├── initializer.py    # init_project — create .evonest/ + templates
│   ├── orchestrator.py   # run_cycles — main cycle loop
│   ├── phases.py         # run_observe, run_plan, run_execute, run_verify
│   ├── claude_runner.py  # claude -p subprocess wrapper
│   ├── mutations.py      # load + merge + weighted select
│   ├── progress.py       # update_progress, recalculate_weights
│   ├── backlog.py        # save_observations, update_status, prune
│   ├── meta_observe.py   # build_meta_prompt, apply_meta_results, expire
│   ├── scout.py          # build_scout_prompt, apply_scout_results, should_run_scout
│   └── history.py        # build_history_summary, get_recent_history
│
├── prompts/              # Phase prompt templates (markdown)
│   ├── observe.md
│   ├── plan.md
│   ├── execute.md
│   ├── verify.md
│   ├── meta_observe.md
│   └── scout.md
│
└── templates/            # Copied to .evonest/ on init
    ├── config.json
    ├── identity.md
    ├── progress.json
    ├── backlog.json
    └── scout.json
```

## Orchestrator Flow

```
evonest run
  │
  ├─ Load EvonestConfig (3-tier: defaults < .evonest/config.json < runtime args)
  ├─ Create ProjectState (validates .evonest/ exists)
  ├─ Acquire EvonestLock (prevents concurrent runs)
  │
  └─ For each cycle (1..N):
      │
      ├─ Meta-observe check (every N cycles, if not --no-meta)
      │   ├─ Build prompt (history + stats + personas + backlog + identity)
      │   ├─ Run claude -p with meta_observe.md
      │   ├─ Expire old dynamic mutations (TTL check)
      │   ├─ Apply results (new personas, adversarials, auto-stimuli)
      │   └─ Save strategic advice → .evonest/advice.json
      │
      ├─ Scout check (every scout_cycle_interval cycles, if scout_enabled and not --no-scout)
      │   ├─ Extract keywords from identity.md
      │   ├─ Run claude -p with scout.md (tools: Read, WebFetch, Bash)
      │   ├─ Score findings 1–10 against project identity/values
      │   ├─ Inject findings ≥ scout_min_relevance_score as stimuli
      │   └─ Cache all findings → .evonest/scout.json (dedup)
      │
      ├─ Select mutation (weighted random)
      │   ├─ Pick persona (built-in + dynamic, weighted by success rate)
      │   ├─ Maybe pick adversarial (20% chance, weighted)
      │   ├─ Consume stimuli (.evonest/stimuli/*.md → .processed/)
      │   └─ Consume decisions (.evonest/decisions/*.md → delete)
      │
      ├─ Phase 1: OBSERVE
      │   ├─ Assemble prompt (observe.md + identity + history + convergence
      │   │   + advisor guidance + environment cache
      │   │   + persona + adversarial + stimuli + decisions)
      │   ├─ Run claude -p (tools: Read, Glob, Grep, Bash)
      │   ├─ Save output to .evonest/observe.txt
      │   ├─ Extract improvements → .evonest/backlog.json
      │   └─ Cache ecosystem items → .evonest/environment.json
      │
      ├─ Phase 2: PLAN
      │   ├─ Assemble prompt (plan.md + identity + observe.txt + backlog context)
      │   ├─ Run claude -p (tools: Read, Glob, Grep, Bash)
      │   ├─ Save output to .evonest/plan.txt
      │   └─ Check for "no improvements" → stop loop
      │
      ├─ [dry-run: skip phases 3-4, count as success]
      │
      ├─ Phase 3: EXECUTE
      │   ├─ Git stash checkpoint
      │   ├─ Assemble prompt (execute.md + identity + plan.txt + decisions)
      │   ├─ Run claude -p (tools: Read, Glob, Grep, Edit, Write, Bash)
      │   ├─ Proposal items → .evonest/proposals/proposal-{cycle}-{ts}.md (no commit)
      │   └─ Code items → .evonest/execute.txt
      │
      ├─ Phase 4: VERIFY
      │   ├─ Run build command (if configured)
      │   ├─ Run test command (if configured)
      │   ├─ Check git diff for changes
      │   └─ Decision:
      │       ├─ PASS + changes + code_output=="commit" → git commit → success
      │       ├─ PASS + changes + code_output=="pr"     → branch + PR → success
      │       ├─ PASS + no changes → drop stash → skip
      │       └─ FAIL → revert + stash pop → failure
      │
      └─ Post-cycle:
          ├─ update_progress (persona stats, area touches, convergence)
          ├─ recalculate_weights (all personas + adversarials)
          ├─ prune backlog (remove old completed/stale)
          └─ save cycle history (.evonest/history/cycle-NNNN.json)
```

## Key Design Decisions

### ProjectState as single access point
All `.evonest/` file I/O goes through `core/state.py:ProjectState`. No other module constructs `.evonest/` paths. This makes testing easy (mock the state) and prevents path bugs.

### Static/Dynamic mutation separation
Built-in mutations live in the `mutations/` package directory (read-only). Dynamic mutations from meta-observe go to `.evonest/dynamic-{personas,adversarials}.json`. They merge at runtime via `load_personas()` / `load_adversarials()`.

### Tool/Core separation
`tools/` modules are thin wrappers that import `core/` functions. All business logic lives in `core/`. This means CLI and MCP server share the same logic.

### 3-tier config resolution
1. Engine defaults (EvonestConfig dataclass field defaults)
2. Project config (`.evonest/config.json`)
3. Runtime parameters (MCP tool args / CLI flags)

Each tier overrides the previous. Supports dot-notation for nested keys (`verify.build`, `max_turns.observe`).

### Weight formula
```
weight = 1.0 + (success_rate * 0.5) - (failure_rate * 0.3) + recency_bonus
```
- `success_rate` = successes / uses
- `failure_rate` = failures / uses
- `recency_bonus` = 0.3 if unused for 3+ cycles (encourages exploration)
- Clamped to [0.2, 3.0]

### Backlog lifecycle
```
pending → in_progress → completed
                      → pending (attempt++)
                      → stale (after 3 failed attempts)
completed/stale → pruned (after 20 cycles)
```

## Phase Summary

| Phase | Claude? | Tools | Max Turns | Output |
|-------|---------|-------|-----------|--------|
| Meta-Observe | Yes | Read, Glob, Grep, Bash | 10 | Dynamic mutations + auto-stimuli + advice |
| Scout | Yes | Read, WebFetch, Bash | 15 | `.evonest/scout.txt` (raw output) + `.evonest/scout.json` (dedup cache) + stimuli |
| Observe | Yes | Read, Glob, Grep, Bash | 25 | `.evonest/observe.txt` + backlog |
| Plan | Yes | Read, Glob, Grep, Bash | 15 | `.evonest/plan.txt` |
| Execute | Yes | Read, Glob, Grep, Edit, Write, Bash | 25 | `.evonest/execute.txt` + proposals |
| Verify | No | subprocess (build/test), git | — | commit / PR / revert |
