---
name: flow-trigger-classify
description: "Trigger's first action — read an external source (issue-tracker ticket / messenger thread / natural language) and classify it into work type + scale. Structured sources (issue type field) are classified with certainty via a mapping table; unstructured sources (messenger·speech) infer from content and, when ambiguous, confirm with the user. Route the classification result to playbook-selection (work type) + scale-judgment (scale). Reference when an external request is right before flow entry."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Trigger's first action — classify the external source

The classification procedure the flow manager (main) performs first **when a work item comes in from an external source**. It reads the external source, judges the **work type** (which way of working = which playbook is needed) and the **scale** (flow weight), and passes the result to the existing selection procedures.

> **Essence**: for a procedure (playbook) to actually be triggered, the *work type must be judged at entry time*. External sources (issue-tracker ticket / messenger thread / natural language) already carry work-type·scale signals — reading and classifying them is the trigger's first action.
>
> **Boundary (no overlap)**: this skill only does **classification (read + judge)**. It delegates the work type → playbook **confirmation** to `flow-playbook-selection` and the scale **confirmation** to `flow-scale-judgment`. This skill builds and routes the inputs to those two procedures.

## Classification, 4 steps

### 1. Identify·read the source

Identify the source type of the incoming work item and **read the actual content** (no guessing from the title).

| Source type | Signal nature | How to read (environment-dependent) |
|----------|----------|--------------------|
| **Issue-tracker ticket** | Structured (type field = certain signal) | fetch the ticket via the issue-tracker MCP — type / title / description / estimate / parent link |
| **Messenger thread** | Unstructured (natural language = inference) | read the thread via the messenger MCP — grasp the context |
| **Natural language (speech)** | Unstructured (natural language = inference) | the conversation input as-is |

> The concrete MCP tools·field names are **environment-dependent** — supplied by the project. This procedure enforces only the principle that "if there is a structured signal like type, that is the primary signal".

### 2. Classify the work type

**Structured source (issue type field present)** — classify via the mapping table below. Certain if type is clear.

| Issue type (common name) | Work type (playbook) | Certainty |
|----------------------|---------------------|--------|
| Bug / Defect | `bug` | certain |
| Story / Feature / New Feature | `feature` | high |
| Improvement / Refactor / Tech Debt | `refactor` | high |
| Documentation | `docs` | high |
| Task / Sub-task | infer from content (judge among the 4 above from title·description) | medium → if ambiguous, §confirm |
| Spike / Research | `docs` or `general` (by deliverable nature) | medium → if ambiguous, §confirm |
| Epic / Initiative (type) | work type is inferred from sub-content + **scale hint = Epic/Initiative** (step 3) | — |
| (fits none of the above) | `general` (general fallback — no specific playbook forced) | fallback |

**Unstructured source (messenger·speech)** — infer the work type from content. "fix it/doesn't work/error" → bug, "add/build it" → feature, "clean up/structural improvement" → refactor, "docs/explanation" → docs, "process retrospective/gather improvements" → retro-processing. **If the inference is ambiguous, §confirm with the user when ambiguous.**

> Playbook catalog for mapping: feature / bug / refactor / docs / retro-processing / general. The cross-check·confirmation against the project's active list (`settings.json playbooks[]`) is performed by `flow-playbook-selection` in the step-3 routing.

### 3. Extract the scale hint

Pull scale signals from the source (**just a hint — confirmation is scale-judgment**):

- **Estimate** (story points / estimate) → a large estimate = Epic signal
- **Parent link** (epic link, etc.) → part of a parent epic = possibly Story scale
- **The ticket's own type is Epic/Initiative** → Epic/Initiative scale signal
- **Description scope** → single topic·deliverable = Story / multiple areas = Epic / simple repetition·format = batch

### 4. Routing

Pass the classification result to the dedicated procedures and enter Planning.

```
work type  → flow-playbook-selection (cross-check settings active playbooks[] → recommend → confirm → record in _epic)
scale hint → flow-scale-judgment (ultimate-purpose interview + 7 steps → confirm scale)
            → enter flow Planning Phase (epic-planning / story-planning ...)
```

> Order: classify → confirm scale → confirm playbook → Planning. This skill fills only the first cell (classification) and delegates the rest.

## Confirm with the user when ambiguous (unstructured·ambiguous branch)

If any of the following, do **not** assert the classification result and confirm with the user:
- The work-type inference of an unstructured source (messenger·speech) splits into two or more candidates
- Even for a structured source, the type is ambiguous (Task / Spike, etc.) and does not resolve from the description either

Confirmation format (consistent with `decision-criteria-first` — no forced option enumeration, recommendation + rationale + 1 alternative):

> "This request looks like **[work type]** by content — rationale: [signal]. (Alternative: **[Y]** — [when it fits better].) Shall I classify it as this?"

> A structured source (issue type certain) proceeds per the mapping table without confirmation. Only unstructured·ambiguous cases are confirmed — minimize unnecessary questions.

## User-explicit bypass

Bypassing the classification·confirmation procedure is only on the user's explicit expression (skip / move on / bypass / skip it). No AI self-judgment bypass (`gate-enforcement-default-on` consistency).

## Verification

- issue type → work type mapping table exists: `grep -E "Bug|Story|Task|Spike" {this SKILL}` → hit
- ambiguous-confirmation branch exists: `grep -E "ambiguous|confirm with the user" {this SKILL}` → hit
- routing cross-ref: `grep -E "flow-playbook-selection|flow-scale-judgment" {this SKILL}` → 2 procedure hits
- generality (bundle enforcement): 0 framework·tool proper nouns in the body procedure (only issue-tracker / messenger abstractions). Proper nouns are cited only inside code-block examples

## References

- `flow-playbook-selection`: work type → playbook confirmation (the step-4 routing target of this skill)
- `flow-scale-judgment`: scale hint → scale confirmation (the step-4 routing target of this skill)
- `flow` SKILL §Mode Detection: fires this skill on external-source entry (wire up)
