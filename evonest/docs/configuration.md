# Evonest Configuration Reference

Config lives at `.evonest/config.json` in your project. All fields are optional — defaults are listed below.

The file supports **JSONC** syntax: you can add `//` line comments anywhere.

## 3-Tier Resolution

1. **Engine defaults** — Built into `EvonestConfig` dataclass
2. **Project config** — `.evonest/config.json`
3. **Runtime parameters** — CLI flags (`--level`, `--cycles`, etc.) or MCP tool args

Each tier overrides the previous. Runtime parameters always win.

---

## Core Fields

### `active_level`
**Default:** `"standard"`

Analysis depth preset. Each level sets `model`, `observe_mode`, and `max_turns`.

| Level | Model | Observe mode | Use when |
|-------|-------|--------------|----------|
| `quick` | haiku | quick | Fast feedback, large codebases |
| `standard` | sonnet | auto | Everyday use (default) |
| `deep` | opus | deep | Thorough analysis, before releases |

Select at init: `evonest init .` (interactive prompt)
Override per-run: `evonest analyze . --level deep`

---

### `language`
**Default:** `"english"`

Language for generated files: proposals, identity, advice.

Examples: `"english"`, `"korean"`, `"japanese"`

---

### `code_output`
**Default:** `"commit"`

How evolved changes are delivered:
- `"commit"` — commit directly to current branch
- `"pr"` — create a new branch and open a pull request

---

### `verify`
**Default:** `{ "build": null, "test": null }`

Shell commands to run after each Execute phase. `null` = skip.

```json
"verify": {
  "build": "npm run build",
  "test": "uv run pytest -q"
}
```

---

### `max_cycles_per_run`
**Default:** `5`

Maximum evolution cycles per `evonest evolve` call.

---

## Level Presets

### `levels`

Customize per-level defaults. Only the fields you specify are overridden.

```jsonc
"levels": {
  "quick":    { "model": "haiku",  "observe_mode": "quick" },
  "standard": { "model": "sonnet", "observe_mode": "auto"  },
  "deep":     { "model": "opus",   "observe_mode": "deep"  }
}
```

Each level also supports `max_turns` overrides:

```jsonc
"levels": {
  "deep": {
    "model": "opus",
    "observe_mode": "deep",
    "max_turns": { "observe": 60, "plan": 25, "execute": 40 }
  }
}
```

---

## Scout & Adversarial

| Field | Default | Description |
|-------|---------|-------------|
| `scout_enabled` | `true` | Enable external ecosystem search (npm, PyPI, GitHub trends) |
| `scout_cycle_interval` | `10` | Run scout every N cycles |
| `scout_min_relevance_score` | `6` | Min relevance score (1–10) to accept scout results |
| `adversarial_probability` | `0.2` | Probability (0.0–1.0) of adversarial challenge per cycle |

---

## Max Turns (Advanced)

Controls LLM tool calls per phase. Set via top-level `max_turns` or inside level presets.

```jsonc
"max_turns": {
  "observe":      25,   // Quick observe pass
  "observe_deep": 100,  // Deep observe pass
  "plan":         15,
  "execute":      25,
  "meta":         10,
  "scout":        15
}
```

> **Note:** Top-level `max_turns` are overridden by the active level's preset. To customize per level, set `max_turns` inside the level entry.

---

## Observe Depth Scaling (Advanced)

Dynamically scales `max_turns.observe` based on project file count.

| Field | Default | Description |
|-------|---------|-------------|
| `observe_turns_quick_ratio` | `0.10` | quick turns = max(min_quick, files × ratio) |
| `observe_turns_deep_ratio` | `0.50` | deep turns = max(min_deep, files × ratio) |
| `observe_turns_min_quick` | `50` | Minimum turns for quick observe |
| `observe_turns_min_deep` | `100` | Minimum turns for deep observe |
| `deep_cycle_interval` | `10` | Run deep observe every N cycles (auto mode) |

---

## Mutation Evolution (Advanced)

| Field | Default | Description |
|-------|---------|-------------|
| `max_dynamic_personas` | `5` | Max auto-generated personas |
| `max_dynamic_adversarials` | `3` | Max auto-generated adversarials |
| `dynamic_mutation_ttl_cycles` | `15` | Cycles before dynamic mutations expire |
| `meta_cycle_interval` | `5` | Run meta-observe every N cycles |

---

## Persona Community (v0.4.0+)

### Importing Community Personas

Via MCP tool:
```python
evonest_import(
    source="noory-code/evonest-personas/security/owasp-expert.json",
    target_type="persona"
)
```

Via CLI (planned):
```bash
evonest import persona noory-code/evonest-personas/security/owasp-expert.json
```

Imported personas are stored in `.evonest/dynamic-personas.json` and automatically loaded on next run.

### Community Repository Structure

```
noory-code/evonest-personas
├── startup/        # Lean startup, growth hacking, PMF
├── security/       # OWASP, threat modeling, pentesting
├── data-science/   # ML ops, model optimization, data pipelines
└── community/      # Community contributions
```

### Contributing Personas

See [noory-code/evonest-personas](https://github.com/noory-code/evonest-personas) for:
- Persona JSON template
- Schema validation rules
- Contribution guidelines
- Quality standards

---

## Viewing & Updating Config

```bash
# View current config
evonest config .

# Set a value (dot notation supported)
evonest config . --set active_level deep
evonest config . --set verify.test "uv run pytest -q"
evonest config . --set max_turns.observe 40
evonest config . --set code_output pr
```

Via MCP:
```
evonest_config(project=".", settings={"active_level": "deep", "max_cycles_per_run": 10})
```

---

## Full Example

```jsonc
{
  // Output language: "english" | "korean" | etc.
  "language": "english",
  // Delivery: "commit" | "pr"
  "code_output": "pr",
  // Analysis depth
  "active_level": "standard",
  // Verify commands (null = skip)
  "verify": {
    "build": null,
    "test": "uv run pytest -q"
  },
  // Level presets
  "levels": {
    "quick":    { "model": "haiku",  "observe_mode": "quick" },
    "standard": { "model": "sonnet", "observe_mode": "auto"  },
    "deep":     { "model": "opus",   "observe_mode": "deep"  }
  },
  "scout_enabled": true,
  "adversarial_probability": 0.2,
  "max_cycles_per_run": 3
}
```
