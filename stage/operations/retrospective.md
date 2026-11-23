# Retrospective

This document owns the mandatory post-work retrospective.

## Gate

After each task, record three sections, the only ones a later reader went back to:

1. `## Decision points`: the choices made and why, including options rejected.
2. `## Context that was missing`: what was missing or stale and cost time.
3. `## Rule candidate`: how work should be done from now on, or empty when nothing durable was
   learned (`stage-retrospective/rule-promotion.md`).

The retrospective does not repeat what other records own:

- What changed: the card's `## Purpose` and the executor report.
- Promotion: the card's `promotion:` field and `## Promotion decision`.
- Principles cited for a decision: the decision record's `## Principles applied`.
- Next work: a planned card, or a record under `state/` (observation, question, risk).

Retrospectives archived before this contract keep their older sections and stay valid
(DE-00000093).

## Rule candidates across retrospectives

```yaml
who_gathers_candidates: a consolidation session the orchestrator starts, never the closing session
when:
  - before a milestone is closed
  - when 20 or more retrospectives are newer than the list's `through:` id
writes: `.stage/state/rule-candidates.md` only
never_edits: retrospectives, decision records, rule files
promotion: the session proposes; a person chooses; a card amends the rule file
```

`stage-retrospective/rule-promotion.md` ("Consolidating candidates") owns the list's format, and
the `stage-orchestrate` skill ("Start a consolidation session") owns starting the session
(DE-00000100).
