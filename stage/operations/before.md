# Before

This document owns the work-start gate.

## Gate

Before starting work:

1. Confirm the purpose.
2. Read the relevant `official/` truth.
3. Read the host project's own instructions (for example `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, project skills) and treat them as binding norms for the plan; if one contradicts observed reality or `official/` truth, register the conflict as an open question with a proposed correction instead of silently obeying it.
4. Check the relevant `state/` uncertainty.
5. Treat `proposals/` and planned work cards (`work/planned/`) only as plans.
6. Define the success criteria.
7. Judge whether a user decision is needed.

## Work cards are for product changes only

Board upkeep — registering, starting, moving, indexing, closing, and archiving cards, and
maintaining `.stage/` records — is performed directly through the Stage skills, scripts, and
hooks. It never gets its own work card: the board must not generate its own workload.

Register a work card only for a change to the product (source, plugin code, docs, released
behavior) that traces to an observed incident, a user request, or a decided design. When a
harness-improvement idea has no such trace, it is not work — at most it is a proposal in
`proposals/`.

## Follow-up candidates

A follow-up candidate is work that a session, a review, or a closing card names as "next" and
that the user did not ask for. It becomes a card only when it carries one of two kinds of
evidence (DE-00000102):

```yaml
a_follow_up_candidate_becomes_a_card:
  - if: it is broken now, and the candidate carries the command that reproduces it and what that
      command prints. Broken means a command fails, a result is wrong, or following a document
      as written stops. A path nobody has run is not broken.
    then: register the card; its success criterion is that the reproducing command passes
  - if: the candidate quotes one line of an open milestone's `## Completion criteria`, with
      the milestone id, as the line it moves. Touching the milestone's purpose sentence is not
      enough.
    then: register the card; its purpose is the quoted line
  - if: it carries neither
    then: discard it and record it nowhere, not on the card, not as an observation, and not
      in `proposals/`. A real problem appears again.
who_attaches_the_evidence: whoever names the candidate
who_judges: the session that registers cards. It checks that the evidence is there; it does not
  ask the user for a purpose, because the evidence carries one.
at_close: the card's `## Progress` gets one line
  `Follow-up candidates: registered <n>, discarded <m>`, also when both are 0
```

A user request still makes a card by itself. When the fix for a broken thing is a `.stage/`
record, fix the record directly; it is board upkeep and gets no card.
