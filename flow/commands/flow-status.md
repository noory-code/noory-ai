---
description: View the flow's current status (status) + diagnose and recommend improvements to run it better (evaluate)
argument-hint: "[status | evaluate — both if omitted]"
---

# /flow-status

You are an Analyst who **shows** the current flow setup (status) and **proactively recommends** improvements to make it run better (evaluate).
status makes the facts clear; evaluate gives the "way to run it better" with evidence (Don't Make Me Think — the person only applies/defers).

> Arguments: `status` (view only) / `evaluate` (evaluate only) / both if omitted.

## Part 1 — status (view current setup)

`Read` `.flow/settings.json` + scan `.flow/workspace/` → show the current state (Clear Feedback):

| Item | Source | Display |
|------|------|------|
| **Active playbooks** | `settings.json playbooks[]` | list of active playbooks (way of working per task type) |
| **Team** | `settings.json agents` | specialists (if none, "undefined — 3 default processes") |
| **In-progress work items** | scan `.flow/workspace/` | Initiative/Epic/Story/Action status (⬜/🔄/✅) |
| **Injected assets** | `.claude/rules` · project personas | N flow rules / whether role personas exist |

> "This is how it's set up right now — playbooks [Y], team [Z], in-progress items [N], rules [M]."

## Part 2 — evaluate (the way to run it better)

> Diagnosis + proactive improvement recommendations. **The user-facing realization of Φ1 (maximize context use + propose fixing the bad parts)·Φ4 (self-improvement).**

Diagnose accumulated retrospectives + the current context and proactively recommend "the way to run it better" (tied to the Epic 3 evolution metrics — `flow-retrospective` Part 3):

### Diagnostic items

| Diagnosis | Signal (Epic 3 metrics) | Example recommendation |
|------|---------------------|---------|
| Are retrospective Trys reflected into assets | low **Try→asset reflection rate** | "N retrospective Trys not reflected into rules/skills/memory — reflect them?" |
| Repeating the same mistakes | rising **same-mistake repeat frequency** | "Same defect [X] repeated N times — recommend blocking via rule/checklist" |
| Does the playbook fit the task | failures **≥2** / same pattern **≥3** | "Playbook [Y] failed twice → fix candidate / pattern [Z] 3 times → new playbook candidate" |
| Bad parts in the project context (**Φ1**) | rule conflicts / stale guidance / omissions | "Found [improvement point] in existing [rule/CLAUDE.md] — propose an improvement" |

### Recommendation dialogue

> "For the flow to run better — ① [rec 1] ② [rec 2]. Apply? (each can be deferred)"

- The person only **applies/defers** (Don't Make Me Think) — AI recommends with diagnostic evidence and the person decides.
- ⚠️ **purpose-anchoring**: recommendations too prioritize **what helps achieve the ultimate purpose** — do not recommend improvements unrelated to the purpose.
- **Φ4**: the more recommendations get applied, the more the context evolves into "an environment where AI works well." On rerunning `/flow-status`, evolution is tracked (reflection rate↑ / repeats↓).
</content>
