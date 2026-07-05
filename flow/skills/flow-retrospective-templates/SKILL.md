---
name: flow-retrospective-templates
description: "Retrospective templates. Reference for per-level Action/Story/Epic + code/meta work variants + metric tables + action-item form + no-empty-field (placeholder blocking)."
user-invocable: false
metadata:
  type: reference
  version: v1.0.1
---

# Retrospective templates

Retrospective forms for each Action, Story, and Epic level. Branches into **code work / meta work variants**.

## Scope (gray zones stated)

| Gray-zone case | Primary | Secondary |
|---------------|---------|-----------|
| Retrospective form (the template structure itself) | **flow-retrospective-templates** | `flow-retrospective` (procedure flow) |
| Retrospective procedure (collection/reflection/archive) | `flow-retrospective` | **flow-retrospective-templates** (form check) |

**Anti-patterns**:
- Omitting some sections of the form (placeholder-blocking violation)
- Leaving blank without stating "N/A"
- Applying code-work metrics directly to meta work
- Action-item table column mismatch (priority/item/target/content)
- Encroaching on procedure responsibility (duplicating `flow-retrospective`'s collection flow into this skill)

**Decision Heuristics**:
- Action retrospective → write in the `## Retrospective` section inside A-NNN.md
- Story retrospective → the `## Story retrospective` section inside _story.md
- Epic retrospective → the retrospective section of _epic.md (→ integrated directly into the Epic retrospective document on archive; no separate RETRO directory)
- Work type code → work-deliverable metrics (e.g. deliverable verification result / impact scope / change size)
- Work type meta → meta-asset metrics (e.g. number of changed assets / reference consistency / consistency)
- Metric unsuitable → state "N/A"

**Output Quality Bar**:
- Keep/Problem/Try all have ≥1 substantive item
- Metric table (matched to the area)
- Action-item table columns: priority (High/Mid/Low) / item / target (file/asset) / content
- Zero empty fields (placeholder blocking)

**Sanity Self-Questions**:
- "Are all sections of the form filled in — not an empty-field violation?"
- "Was the code-work/meta-work variant applied correctly?"
- "When a metric is unsuitable, did I state 'N/A' rather than just leaving it blank?"
- "Did I avoid duplicating procedure responsibility into this skill?"

> ⚠️ Work-type branch: for detailed criteria see `flow-retrospective`'s work-type branch.
> Stating "metric N/A" is allowed. But Keep/Problem/Try etc. cannot be left blank (placeholder blocking).

> 📊 **Measurement citation (evidence-based retrospective)**: metrics/Problems should, where possible, use **measured numbers** rather than impressions — pull the aggregate for the work unit via `uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/audit_report.py" --unit <work-unit-id>` and cite retries, tools, fired rules, and skills used. (If there is no measurement data, state "no measurement." Projects without flow measurement capture installed are N/A.)

---

## Level 1: Action retrospective

Write in the `## Retrospective` section of the relevant A-NNN.md after completing the Action. However, if `.flow/settings.json` `retrospective.levels.action.rigor=none`, the Action retrospective is not a required item, and you may leave only the rationale for omission via a `## Settings note` etc.

### Code-work form (concise)

```markdown
## Retrospective

**Keep**: [one line — a good AI behavior/pattern]
**Problem**: [one line — inefficiency/mistake; "none" if none]
```

> Add only when an action item is needed: `**Try**: [improvement]`

### Meta-work form (detailed)

```markdown
## Retrospective

### Metrics (meta-work variant)
- Changed assets: [N] ([target category])
- Reference consistency: [N] (Before [N] / After [N])
- Consistency metric: [standard-application rate X%, or a summary of change-pattern consistency]
- Regression impact: [whether AI behavior regressed; provisional marking allowed before ground-truth inspection]
- Measurement citation (audit_report): retries [N] / main tools [tool=N …] / fired rules [rule=N …] / skills used [skill …] — `audit_report.py --unit <work-unit-id>` (if no measurement, "no measurement")

### Keep
- [a good AI behavior/pattern]

### Problem
- [inefficiency/mistake/mis-called decision]

### Try
- [improvement to apply in a follow-up Action/Story]

### What was needed
- [material/pre-verification/tool that was absent at the time]

### Action items
| Priority | Item | Target | Content |
|---------|------|------|------|
| High/Med/Low | [short title] | [file/asset/Epic] | [what to do] |
```

---

## Level 2: Story retrospective

Write in the `## Retrospective` section of `_story.md` when wrapping up the Story.

> **Meta-work variant**: use the form below as-is, but add **meta-work metrics** below the "Overall Summary" table (total changed assets, cumulative reference consistency, whole-Story consistency metric, AI-behavior regression impact). For per-Action metrics see each A-NNN.md retrospective (Level 1 meta form).

```markdown
## Retrospective

### Overall Summary
| Item | Value |
|------|-----|
| Planned Actions | [N] |
| Actual Actions | [N] |
| Added Actions | [title if any] |
| Removed Actions | [title if any] |
| Total commits | [N] |

### Meta-work metrics (meta Story only)
| Item | Value |
|------|-----|
| Total changed assets | [N] (sum across Actions) |
| Reference consistency (Before / After) | [N] / [N] |
| Consistency metric | [overall standard-application rate X% or change-pattern summary] |
| Regression impact (AI behavior) | [none / present + detail] |

### AI efficiency analysis
| Item | Content |
|------|------|
| Most efficient Action | [A-NNN: title] - [reason] |
| Least efficient Action | [A-NNN: title] - [reason] |
| Repeated pattern | [problem repeated ≥2 times] |

### Cause analysis
| Inefficiency | Cause | Category |
|--------|------|----------|
| [content] | [cause] | skill-gap/procedure-gap/context-gap |

### Keep / Problem / Try
(same format as the Action retrospective)

### What was needed
(same format as the Action retrospective)

### Action items
(same format as the Action retrospective)

### Per-Action retrospective summary
| Action | Key Keep | Key Problem |
|--------|----------|-------------|
| A-001 | [summary] | [summary] |
| A-002 | [summary] | [summary] |
```

---

## Level 3: Epic retrospective

Write in the `## Retrospective` section of `_epic.md` when wrapping up the Epic.

> **Meta-work variant**: add **meta-Epic metrics** below the "Overall metrics" table (summed across all Stories — total changed assets, total change in reference consistency, overall consistency, overall regression impact).

```markdown
## Retrospective

### Overall metrics
| Item | Planned | Actual | Variance |
|------|------|------|------|
| Stories | [N] | [N] | [+/-N] |
| Actions | [N] | [N] | [+/-N] |
| Duration | [N days] | [N days] | [+/-N days] |

### Meta-work metrics (meta Epic only)
| Item | Value |
|------|-----|
| Total changed assets | [N] (sum across all meta-asset types) |
| Reference consistency (Before → After) | [N] → 0 (goal) |
| Overall consistency | [standard-application rate X% across all assets] |
| Regression impact (AI behavior) | [final verification result] |
| Orphan assets (Before → After) | [N] → 0 (goal) |

### AI efficiency analysis
| Item | Content |
|------|------|
| Most efficient Story | [US-NNN: title] - [reason] |
| Least efficient Story | [US-NNN: title] - [reason] |
| Overall pattern | [recurring problem] |

### Keep / Problem / Try
(same format as the Action retrospective)

### What was needed
(same format as the Action retrospective)

### Action items
(same format as the Action retrospective)

### Per-Story retrospective summary
| Story | Key Keep | Key Problem | Actions |
|-------|----------|-------------|----------|
| US-001 | [summary] | [summary] | [N] |
| US-002 | [summary] | [summary] | [N] |
```

---

## Level 4: Initiative retrospective

Write in the `## Initiative retrospective` section of `_initiative.md` when wrapping up the Initiative. **Not an Epic-retrospective summary but a value-proposition (Φ) alignment evaluation** (procedure: `flow-procedure-initiative`).

```markdown
## Initiative retrospective

### Value-proposition (Φ) alignment evaluation
| Φ | Philosophy | Achieved | Basis (deliverable) |
|---|------|:--------:|-------------|
| Φ1 | [philosophy] | achieved/partial/unmet | [deliverable + verification] |
| ... | ... | ... | ... |

### Initiative metrics
| Item | Value |
|------|-----|
| Total Epics / Stories / Actions | [N] / [N] / [N] |
| RETRO items | [N] |
| Updated assets (rule/skill/playbook/memory) | [N] |
| Evolution metrics (trend) | Try→asset reflection rate [%] / same-mistake repeat frequency [trend] / essence alignment [verdict] |

### Per-Epic retrospective summary
| Epic | Key Keep | Key Problem | Stories |
|------|----------|-------------|----------|
| Epic 1 | [summary] | [summary] | [N] |

### Next evolution direction
- [follow-up evolution direction after the Initiative completes]
```

> **Evolution metric trend**: the Initiative retrospective measures a **cumulative trend**, not a single point (a drop in same-mistake repeat frequency = proof of evolution). Metric definitions: `flow-retrospective` Part 3-5.

---

> **Per-label example retrospectives**: see `flow-retrospective` Part 4 §4-6 (responsibility boundary — the form/example SSOT is this templates skill; label definitions/examples are procedure-dependent, so they live in retrospective Part 4).

## Authoring rules

1. **Keep**: describe concrete behavior/pattern (e.g. "loaded the procedure doc then implemented immediately → efficient")
2. **Problem**: based on objective facts (e.g. "edited the same file 3 times → insufficient upfront analysis")
3. **Try**: an actionable improvement (e.g. "grasp the whole structure before editing a file")
4. **Banned**: self-evaluation like "did well," "done" → describe concrete facts only
5. **Action items**: always state the target file and priority
