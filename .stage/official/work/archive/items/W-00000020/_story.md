---
id: W-00000020
title: Cross-venue delegation and review contract
kind: documentation
venue: claude
priority: high
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000020
promotion: not_applicable
scope: stage/skills/stage-handoff/,stage/operations/,stage/templates/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000020 Cross-venue delegation and review contract

## Purpose

Formalize dual-agent operation: a bridge-equipped window may execute another venue's cards by delegation (claude window delegates codex-venue cards via the codex plugin), and work is cross-reviewed — codex-venue output reviewed by claude before close, claude-venue output reviewed by codex via the close_work review gate. Update stage-handoff doctrine, operations docs, and the review-gate wiring guidance.

## Source

Owner direction 2026-07-13: automate the venue rotation (claude designs, codex implements,
each reviews the other) from the claude window, which carries the codex bridge; the codex
window has no claude bridge, so delegation is one-directional by nature.

## User value

The human stops switching windows for routine execution and touches the loop only at decision
points (questions, promotions). Review quality rises because no card is reviewed by the model
that produced it.

## Scope

### Included

- `stage/skills/stage-handoff/SKILL.md`: Delegated execution doctrine (venue = executing
  surface, not hosting window; host monitors, reviews, never self-reviews; decisions and
  promotions never delegate).
- `stage/operations/review.md`: Cross-venue review section (executor ≠ reviewer; delegated
  output reviewed by host at close; self-closed cards bind the counter-venue via the existing
  `review: pending` + settings strength gate).
- CHANGELOG + plugin version bump.

### Excluded

- No hook or script changes — the contract rides existing mechanisms (review gate, venue
  field, audit checks).
- No template changes: venue meaning stays project-canon; plugin templates fix no venue names
  (AHA — revisit if a second project needs the same canon text).

## Dependencies

- W-00000019 (C2) commit must land first: it holds staged CHANGELOG/plugin.json changes in
  the shared tree; this card's version bump and commit follow it.

## Risks

- Two agents share one working tree; commits must stay scoped to each card's files.

## Success criteria

- Both docs state the contract without banned vagueness (explicit executor/reviewer rules,
  explicit gate wiring), consistent with `operations/review.md`'s existing rebuttal sequence.
- Version bumped, CHANGELOG entry added, committed and pushed after C2 lands.

## Next action

Wait for the W-00000019 commit, then bump version + CHANGELOG and commit this card's files.

## Progress

- 2026-07-13: Both doc edits written (SKILL.md Delegated execution; review.md Cross-venue
  review); committed as 0.24.1 (b069a98e) after the C2 commit landed.
- Cardless board-upkeep doctrine added to operations/before.md as 0.24.2 (e4b407f5) on owner
  direction: the rule lives in Stage, not in agent memory.
- Cross-venue review executed (codex, companion review, HEAD~1 diff): zero findings on this
  card's contract docs. Three adjacent board findings processed per the review gate: P1
  invalid review strengths in settings.json — fixed and gate wired (7e1da0f9); P3 backlog
  index rows outside the table — fixed, root cause captured as W-00000027; P2 language ko —
  REBUTTED: the owner's explicit locale choice through Stage's ko feature; the repository
  English rule governs product artifacts, and this card keeps all plugin docs in English.
- Review-gate wiring measured and hardened: raw companion review exits 0 even with P1
  findings, so the bound command wraps it to emit BLOCK and exit non-zero on any P1.
  Limitations recorded: review target is the HEAD~1 diff (single-commit cards fully covered),
  and the command pins the plugin cache path (re-pin on plugin update).

## Verification

Executed this session:

```
$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 281 tests in 0.494s

OK
```

## Retrospective

## Promotion decision
