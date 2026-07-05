---
name: meta-agent-procedure
description: |
  Subagent (teammate) creation/improvement procedure. A project-agnostic team-operation procedure — runs on top of Agent Teams.
  7-kind work-type classification + team-structure concept + 5-Phase common skeleton + operating principles + candidate-judgment signals + the persona 7-field frame.
  Owns "how to create and deploy a teammate" — "who does what" (concrete teammate definitions) is defined by the project (in .claude/agents/).
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# meta-agent-procedure

> **Meaning of this skill**: the **Subagent (teammate) creation/improvement skill**. It bodies-out a **team-operation procedure** not tied to any project — teammate candidate judgment, the persona-definition frame, the invocation interface, area boundaries, the 5-Phase common skeleton.
>
> **MECE boundary (key)**:
> - **This skill = "how to create and deploy a teammate"** — 7-kind work-type classification, team-structure concept, 5-Phase skeleton, operating principles, the 4 candidate-judgment signals, the persona 7-field frame, the model·effort matrix concept (project-agnostic, general-purpose).
> - **Project (.claude/agents/) = "who does what"** — the concrete teammate definitions themselves (each teammate's name/responsibility/model/effort concrete values, per-role Layer binding, project-skill binding) are **defined by the project (in .claude/agents/)**. This skill does not deal with those teammates' names or responsibility mappings.

## Agent Teams mapping (term SSOT)

This skill runs on top of Agent Teams. The mapping between flow concepts and Agent Teams components has `flow/SKILL.md` "Agent Teams mapping model" as its SSOT. Core terms used in this skill:

| This skill's concept | Agent Teams mapping |
|---|---|
| Main (orchestrator) | single team lead (fixed) |
| Expert | teammate |
| Return to main on area intrusion | mailbox handoff |
| Team deployment (after Epic Planning Finalize) | after passing the plan-approval gate |
| teammate assignment | teammate spawn (**main-only** — a teammate cannot spawn another teammate) |

**Team-structure constraint (key)**: the main is the single team lead. A teammate cannot **spawn** another teammate ("No nested teams" — a platform hard constraint: nested teams cause token explosion and coordination complexity). So **assigning (spawning) a new teammate is main-only** — if an expert needs a new expert, it requests the main via mailbox and the main spawns it. **But collaboration between already-active team members (information sharing / review requests) is peer-to-peer direct mailbox** — the lead is not a central hub (the essence of Agent Teams). What must go through the lead is **only spawn/assignment/plan approval**. The layers in "Team structure" below are a **conceptual responsibility hierarchy**; only the actual spawn authority is fixed to the main (collaboration messages are direct). (The above applies only when Claude Code AT is on — Copilot falls back to AT off with a sequential main.)

## 1. 3-tier classification (teammate area / utility / skill)

```
Work types (teammate area) — 7 kinds
Utilities (tools — not teammates) — simple imperative automation (codegen / clean / setup, etc., per project)
Skills (user-invoked directly) — user-triggered procedures (like security-review — per project)
```

## 2. Work types — 7 kinds (handled by teammates)

| # | Work type | Core process flow |
|:-:|----------|-----------------|
| 1 | **Feature development** (9 steps) | requirements → design → TDD → implementation → run tests → review → apply → output verification → wrap-up |
| 2 | **Bug fix** (7 steps) | bug analysis → reproduce (ideally) → identify the issue → fix (+ logging) → rerun tests → review → wrap-up |
| 3 | **Simple feature improvement/change** (8 steps) | almost identical to Feature — small scope + existing context |
| 4 | **Documentation** (5 steps, 5 sub) | output extraction/update/planning + package docs + Wiki — no code change |
| 5 | **Refactoring** (8 steps) | user-stated + scope/level discussion → extract verification criteria → apply patterns → criteria-based verification |
| 6 | **AI system improvement** (5-Phase guide) | not a procedure but a value — start/hypothesis/principle/experiment/learning |
| 7 | **Material research / Research** (6 steps) | dual mode: standalone / another teammate's sub-tool |

> The 1:1 mapping of the 7 kinds ↔ concrete expert teammates — each teammate's name/responsibility/owned Layer/model/effort concrete values — is **defined by the project (in .claude/agents/)**. This section specifies only the **classification frame** of work types.

### 2.5 Process teammates (universal — plugin-provided interface)

If a specialist handles "what to build (project domain)," a **process teammate handles "how to work (universal)."** Project-independent, so the plugin provides the interface and the project customizes only the variable elements via settings (no fixed `.md` shipped).

| Process teammate | Responsibility (universal) | Variable (settings/project) | Persona |
|---|---|---|---|
| **planning** | Action breakdown · AC definition · MECE | domain analysis is the project specialist's job | Manager |
| **finishing** | retrospective · archive · PR · Squash merge | — | Manager |
| **research** | investigation · source organization | **"where (source)" = settings customization** | Analyst |

The universal procedures already exist in the plugin `skills/` (flow-planning-* / flow-retrospective·archive / flow-pr) — a process teammate is a universal member that runs those skills. **research source customization**: declare sources in `.flow/settings.json`:

```json
{ "research": { "sources": ["rag", "web", "wiki:<path>"] } }
```

Source tools are optional (e.g. use the `rag` plugin if installed — no hard dependency). If `research.sources` is empty, the research teammate asks the user to configure sources.

## 3. AI system improvement 5-Phase skeleton (reference)

```
1. Starting point (accumulated retrospectives / user decision / discovery)
2. Hypothesis derivation (data analysis + user dialogue)
3. Principle application (token vs improvement / complexity / accuracy tradeoff)
4. Experiment application (hypothesis → apply → measure)
5. Effect evaluation + learning (retrospective — input to the next hypothesis)
```

This skill itself is a model case of this pattern (start=discovery / hypothesis=interview / principle=accuracy-first / experiment=rule/skill update / learning=retrospective).

## 4. Team structure — conceptual responsibility hierarchy

```
┌───────────────────────────────────────────────────┐
│  Main (user interface + orchestration owner)      │
│  - Determine work type → select playbook          │
│  - Epic Planning (confirm Story outline) + finalize Story Action decomposition │
│  - Run the playbook procedure + assign (spawn) expert teammates + verify/commit/retrospective │
└───────────────────┬───────────────────────────────┘
                    │ Main assigns experts per the playbook procedure
                    ▼
┌───────────────────────────────────────────────────┐
│  Shared expert teammate pool (per role — defined by the project) │
│  - Depth work in own area (analysis / implementation / testing / review / wrap-up, etc.) │
│  - Peer collaboration = peer-to-peer direct mailbox (no lead relay) │
│  - Request the main only when a new teammate is needed (spawn is main-only — "No nested teams") │
└───────────────────┬───────────────────────────────┘
                    │ operates on top of the below
                    ▼
┌───────────────────────────────────────────────────┐
│  Flow (infrastructure — shared by all teammates) │
│  - Epic/Story/Action SSOT                         │
│  - Planning procedure / Verify-Commit / retrospective / PR / merge │
└───────────────────────────────────────────────────┘
```

> **No orchestration middle layer (Lead)**: procedures are playbooks (per work type); orchestration is done directly by the always-running main (Initiative Φ1). The expert-teammate composition (count + each name/responsibility/model/effort) is **defined by the project (in .claude/agents/)**. This section specifies only the **responsibility-hierarchy concept** of main → expert → flow and the spawn-authority constraint.

> **Recommended placement of Research**: Research = standalone mode + sub-tool mode compatible → recommended placement in the expert pool (the main uses it as a sub-tool). Concrete placement is the project's decision.

### 4.1 LLM matrix — Tier × complexity → (model, effort)

A **matrix concept** for deciding a teammate frontmatter's `model` + `effort` (concrete value mapping is the project's decision):
- An Agent Teams teammate frontmatter controls inference strength via `model` (opus/sonnet/haiku, etc.) + `effort` (low/medium/high/xhigh/max, etc.).
- Multiple teammate invocations each carry their own context, so tokens grow greatly — accurate model·effort selection is the key to cost control.
- **Application timing (Claude Code ground-truth inspection — claude-code-guide)**: `model` **can be set both in the agent definition (frontmatter) and as a spawn-time override** → **actively select** a model that fits the task's nature **at spawn time**. `effort` **can only be fixed in the frontmatter — a per-task dynamic setting at spawn time is currently unimplemented** (GitHub #25591, session effort inheritance). So bake effort into the agent definition to fit the task's nature (update this procedure once dynamic support arrives). (Applies only when Claude Code AT is on — Copilot does not use teammates.)

#### Dimension definitions

- **Tier (row)**: responsibility hierarchy — main / Planning / expert / utility
- **Complexity (column)**: task inference load — high (broad reasoning, composite decisions, meta) / medium (structure application, standard patterns) / low (simple lookup, clear procedure)
- **Cell**: `(model, effort)` pair

#### Matrix (4 Tier × 3 complexity — conceptual example)

| Tier \\ complexity | high (broad / meta) | medium (structure / standard pattern) | low (simple lookup / procedure) |
|----------------|:------------------:|:--------------------:|:---------------------:|
| **Main** (user interface + Planning + orchestration) | (top, max effort) | (top, high effort) | (mid, high effort) |
| **Planning** (analysis + decomposition) | (top, max effort) | (top, high effort) | (mid, high effort) |
| **Expert** (depth in own area) | (mid, high effort) | (mid, medium effort) | (low, medium effort) |
| **Utility** (simple collection / wrap-up) | (mid, medium effort) | (low, medium effort) | (low, low effort) |

> The cells above are a **relative-strength concept** (top/mid/low model × max/high/medium/low effort). Concrete model names and effort values are **defined by the project to fit its own model lineup**.

#### Complexity definitions (1 line)

- **High (broad / meta)**: cross-area, AI-system meta improvement, essence-attack depth, persona matching, review depth — deep thinking required
- **Medium (structure / standard pattern)**: standard-pattern application, work on top of existing context — moderate reasoning
- **Low (simple lookup / procedure)**: material collection / indexing / archiving / PR creation, etc. with a clear procedure — light thinking

#### Priority (interpretation order)

- **model**: `CLAUDE_CODE_SUBAGENT_MODEL` env > **spawn-time `model` override** > frontmatter `model` > main session model. → the layer where per-task spawn selection is possible.
- **effort**: env (`CLAUDE_CODE_EFFORT_LEVEL`) > frontmatter `effort` (this matrix applies) > session inheritance > model default. **Per-task dynamic at spawn time is unimplemented** (see §4.1 application timing above — frontmatter-fixed).

Detailed delegation mechanism = `handoff-protocol` (`delegation_mode` compatible — `auto` / `subagent` / `direct`).

## 5. Operating principles

| # | Principle | Meaning |
|:-:|------|------|
| 1 | **Flow = infrastructure** | Not a teammate. Shared by all teammates. The common skeleton of Planning/Verify/retrospective/PR |
| 2 | **Epic Planning Phase = main's responsibility** | Centered on user + AI dialogue. Main handles Epic analysis / Story **outline** decomposition / user confirmation (Epic-level) |
| 3 | **Story Planning (Action decomposition) + orchestration = main's responsibility** | All per-Story Action decomposition/finalization/confirmation is the main. Thereafter the main runs the playbook procedure through the Epic's 1-cycle PR (every Story + every Action — the expert only performs Actions). User confirmation is at key decision points |
| 4 | **Prevent area intrusion** | Operate only within your own work type. On finding another area, return to main + `flow-issue-handling` classification |
| 5 | **2-stage retrospective** | (a) self-retrospective immediately (Action/Story wrap-up) (b) meta improvement later (analyze N accumulated retrospectives) |
| 6 | **Sub-tool mode allowed** | Another teammate can use it like a tool (e.g. the Research teammate) (but no area intrusion) |

## 6. Dimension separation (flow vs teammate)

| Dimension | Responsibility | Persona |
|------|------|---------|
| **Flow** | "How do we **manage/track** this work?" (work-item decomposition / SSOT / status) | manager (Flow Manager) |
| **teammate** | "How do we **perform** this work?" (domain decomposition / implementation / verification) | per-role expert type |

**Example — the actual responsibility split of stages that look overlapping**:
- Flow Planning = "split this work into N Actions and record in the SSOT" (work-item dimension)
- teammate design stage = "how to structure this feature" (domain dimension)
- The two stages are **collaboration** (the teammate provides analysis results to Flow Planning)

## teammate creation procedure

### Step 1: teammate candidate judgment (4 signals — frequency / clear persona / no area intrusion / main dependency)

| # | Signal | teammate candidate? |
|:-:|------|:------------:|
| 1 | High **frequency** + **clear persona** | ✅ teammate |
| 2 | Low frequency or simple command | ❌ skill or utility |
| 3 | Can own its responsibility **without area intrusion** | ✅ teammate |
| 4 | Always needs **main + user dialogue** (main dependency) | ❌ main |

> Signals 1/3 both satisfied + signals 2/4 both not applicable → teammate separation recommended.

### Step 2: Persona definition (7 fields)

Follow the persona 7-field frame in `rules/personas.md` (a teammate definition is a functional persona — unrelated to the skill-top-block prohibition):
- Role / Expertise / Core Beliefs / Anti-patterns / Decision Heuristics / Output Quality Bar / Sanity Self-Questions

### Step 3: Define the invocation interface

- **Input**: the message the expert teammate receives (work unit + context)
- **Output**: the format returned to the main or caller
- **Self-retrospective format**: a format usable as meta-improvement input data

### Step 4: State area boundaries

- Own work type (responsibility)
- Collaborable sub-tools (e.g. the Research teammate — via mailbox)
- Handling on area intrusion (return to main + `flow-issue-handling`)

### Step 5: State flow usage

- Which part of the Planning Phase is used
- Whether Verify-Commit is used
- Retrospective-writing format
- PR-creation timing

### Step 6: Create the teammate definition file

- Write the system prompt (follow the project's agents-directory convention)
- Tool / MCP selection
- Test scenarios

> **The concrete teammate definition (name/responsibility/model/effort)** is **defined by the project (in .claude/agents/)**. This procedure is the **common skeleton** activated when adding a new teammate or improving an existing one.

## teammate improvement procedure

### Meta-improvement trigger (after retrospectives accumulate)

- N Action/Story/Epic retrospectives accumulate → pattern analysis
- Evaluate the teammate's own behavior (Keep / Problem / Try)
- Derive improvement proposals through user + main dialogue

### Activate the AI-system-improvement 5 Phase (see §3 above)

This skill is that procedure document. Improve through the start/hypothesis/principle/experiment/learning cycle.

## Asset Files

| Reference skill | Use |
|---------|------|
| `rules/personas.md` | Persona 7-field frame (used when defining a teammate) |
| `meta-skill-procedure` | Skill creation procedure (distinguish teammate ≠ Skill) |
| `flow-issue-handling` | Classification decision table when area intrusion occurs |
| `handoff-protocol` | teammate assignment mechanism (`delegate_to` / `delegation_mode`) |
| `debate-protocol` | Debate RT (verification when improving a teammate) |

## MUST NOT

- ❌ Trying to activate an undefined teammate (invoking without a prior definition — a new one must pass this procedure)
- ❌ Demoting the flow to a teammate (infrastructure ≠ teammate)
- ❌ Bringing a teammate into the Planning Phase (its essence is main + user dialogue)
- ❌ Area intrusion (handling work outside your own work type yourself)
- ❌ A placeholder retrospective (not qualified as meta-improvement input)
- ❌ Unbounded growth in teammate count (complexity boundary)
- ❌ A change that increases tokens + has zero effect (Core Belief violation)
- ❌ A teammate directly spawning another teammate (main-only — "No nested teams")

## References

- `flow/SKILL.md` — Agent Teams mapping model (term SSOT)
- `handoff-protocol` — meaning of `delegate_to` + teammate assignment mechanism ("how to delegate")
- `flow-issue-handling` — area-intrusion classification + handling path
- Project (.claude/agents/) — the concrete teammate definitions themselves ("who does what")
