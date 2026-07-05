---
name: flow-scale-judgment
description: "Judging batch work vs work-item management. Confirm the ultimate purpose (if self-evident, state and confirm) + 7-step scale judgment + Initiative/Epic/Story/standalone decision table + upper-container plurality guard (a single child forbids the upper). The AI judges the scale — it does not ask the user for the scale."
user-invocable: false
metadata:
  type: reference
  version: v1.2.0
---

# Work scale judgment (Scale Judgment)

The common scale-judgment logic used in the Discovery stage of the Planning Phase.
Referenced by `flow-planning-epic` and `flow-planning-story`.

The scale-decision result determines the shared task list structure.

| Decision result | shared task list structure |
|----------|----------------------|
| Batch work | single task (no hierarchy, commits only) |
| Story standalone mode | single task list (Action items) |
| Epic | Epic hierarchy (multiple Stories → Actions) |
| Initiative | Initiative hierarchy (multiple Epics → Stories → Actions) — a common value proposition |

## Confirm the ultimate purpose (precedes scale judgment — if self-evident, state and confirm; ask only when unclear)

Ahead of the 7-step scale judgment, anchor **this work item's ultimate purpose**. The purpose plays two roles:
1. **First signal of scale** — the breadth of the purpose separates Initiative/Epic/Story (a value that bundles multiple areas → Epic/Initiative; a single focused purpose → Story). ⚠️ But even if the purpose looks large, **if the child unit is 1 do not make it an upper container** (see §upper-container necessary condition below).
2. **The root of the purpose chain** — the anchored purpose becomes the `**ultimate purpose**` field of the entry-scale top node (`_initiative`/`_epic`/`_story`). Inherited down to the child (Action).

**Default = the lightweight path (`purpose-anchoring`/`decision-criteria-first` parity)**: if the purpose is self-evident from the request, do not ask. The AI **states the purpose in 1 line, confirms**, and proceeds. (Not removing the purpose but removing the unnecessary question.)

**When to ask (only when the purpose is fundamentally unclear)**: "What is this work's ultimate purpose? (why / which higher value it serves)". If ambiguous, narrow once more: "If this fails, what gets blocked?".

> ⚠️ What you ask is the **purpose (what and why)**, not the **scale (which of Story/Epic/Initiative)**. Once the purpose is captured, the AI derives the scale via the 7 steps (§Scale decision).

**Handling**:
- The answer received (or stated and confirmed) = the value of the `**ultimate purpose**` field of the entry-scale top node. Lower levels inherit and restate it (do not invent an absent upper level).
- If the entry scale is Story, the Story goal is the ultimate purpose; if Epic, the Epic goal; if Initiative, the value proposition — **the entry scale is the top**.
- If the purpose spans multiple areas → weight it as an Epic/Initiative signal in the 7 steps.

---

## Scale judgment 7 steps

When the user requested only "start work", analyze the work scale by the 7-step criteria below.
(The §ultimate-purpose interview above is required before the 7 steps.)

### 1. Expected work duration

| Duration | Decision |
|------|------|
| 1-3 days | Story standalone mode |
| 5+ days | Epic |
| 4 days | Borderline → judge by sub-task count |

### 2. Sub-task count

| Count | Decision |
|------|------|
| 5 or fewer Actions | Story standalone mode |
| 3 or more Stories | Epic |
| 2 Stories | Borderline → judge by area scope |

### 3. Area scope

| Scope | Decision |
|------|------|
| Single area (e.g. a single feature/topic) | Story standalone mode |
| Multiple areas (e.g. auth + profile + settings) | Epic |

### 4. Dependencies

| Dependency | Decision |
|--------|------|
| Can run independently | Story standalone mode |
| Needs coordination across multiple teams/systems | Epic |

### 5. Deliverable impact scope

| Scope | Decision |
|------|------|
| 5 or fewer deliverables changed | Story standalone mode |
| 10 or more deliverables changed | Epic |
| New area/structure added | Epic |

### 6. Uncertainty

| Uncertainty | Decision |
|---------|------|
| Clear requirements, verification method fixed | Story standalone mode |
| Needs research/PoC, requirements unclear | Epic (includes a Discovery Story) |

### 7. External conditions

| Condition | Decision |
|------|------|
| Only internal team involved | Story standalone mode |
| Needs external approval/review | Epic |
| Milestone-linked | Epic |

---

## Judgment-criteria summary

**Story standalone mode recommended**:
- 1-3 days, 5 or fewer sub-tasks
- Single area, can run independently
- 5 or fewer deliverables, clear requirements

**Epic recommended**:
- 5+ days, 3 or more Stories
- Multiple areas, complex dependencies
- 10 or more deliverables, high uncertainty

**Initiative recommended**:
- 2 or more Epics, bundled by a common value proposition
- A large flow that does not finish with a single Epic (`flow-procedure-initiative`)

**Borderline (4 days, 2 Stories, 5-10 deliverables)**:
- The AI decides by default: **start small** (Story standalone) — do not ask the user for the scale.
- Promote later if needed (start small → promotion is cheaper than over-structuring). **Immediately upon the promotion decision, update the original Story/TS placeholder to '➡️ promoted to Epic' + a link to the promoted Epic (do not leave it ⬜).**

---

## Upper-container necessary condition — plural children (a single child forbids the upper)

Create an upper level only when the **child units are 2 or more**. If there is 1 child, that child level is the entry scale — the same even if the purpose looks large.

- **Initiative = 2 or more Epics** (1 Epic forbids an Initiative)
- **Epic = 2 or more Stories** (1 Story forbids an Epic)
- ❌ **No empty-shell containers**: things like "Initiative — 1 Epic", "Epic — 1 Story + 1 Action". Over-structuring that only adds orchestration/directory cost.
- ✅ A single child = enter at that level (1 Epic → Epic directly / 1 Story → Story standalone / an Action bundle → inside that Story).
- Even if you started upper, **if decomposition converges to 1 child, demote to that level**.

> **Why this guard is needed**: if the plurality conditions (Epic 2+, Story 2+) exist only as "recommendation criteria" without a necessary-condition guard, then when the purpose looks large or because of the hook directory pattern (`epic-*`/`initiative-*`), an upper container is created even with a single child (empty shell). The guard blocks this.

---

## Scale decision — proceed after the AI judges (do not ask the user for the scale)

The scale is **judged by the AI** with the 7-step indicators — duration, task count, area, dependencies, deliverables, uncertainty, and external conditions are all objective signals derivable from the work content. Scale is a **reversible way-of-working judgment** (`decision-criteria-first` (0)), not a user value judgment.

- ❌ **Do not ask "shall we do it as a Story, or as an Epic?"** — forbidden to offload the scale onto the user as an option. **Do not ask even in a borderline case.**
- ✅ **Report the judgment result in 1 line, then proceed**: e.g. "By the 7 steps I judge Story standalone (rationale: 1 day · 3 Actions · single area). Starting small."
- On borderline/ambiguity, default = **start small** (Story standalone / batch). Starting small and promoting if needed is cheaper than over-structuring.
- The user-intervention point is not the "scale" but the **approval of the whole formulated plan** (plan approval) — the AI sets the scale + structure and presents it as a plan, and the user reviews and approves/edits it (`no-auto-proceed` checkpoint). The "pick the scale" question and "plan approval" are different.

> Even in exceptions, do not ask the scale: if the purpose is fundamentally unclear, ask the **purpose** via §Confirm the ultimate purpose (not the scale); once the purpose is captured, the AI derives the scale via the 7 steps.

---

## References

- `flow-planning-epic`: references this file in the Discovery section
- `flow-planning-story`: references this file in the Discovery section
