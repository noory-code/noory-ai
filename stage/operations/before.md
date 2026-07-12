# Before

This document owns the work-start gate.

## Gate

Before starting work:

1. Confirm the purpose.
2. Read the relevant `past/` truth.
3. Read the host project's own instructions (for example `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, project skills) and treat them as binding norms for the plan; if one contradicts observed reality or `past/` truth, register the conflict as an open question with a proposed correction instead of silently obeying it.
4. Check the relevant `present/` uncertainty.
5. Treat `future/` only as plans or proposals.
6. Define the success criteria.
7. Judge whether a user decision is needed.

## Work cards are for product changes only

Board upkeep — registering, starting, moving, indexing, closing, and archiving cards, and
maintaining `.stage/` records — is performed directly through the Stage skills, scripts, and
hooks. It never gets its own work card: the board must not generate its own workload.

Register a work card only for a change to the product (source, plugin code, docs, released
behavior) that traces to an observed incident, a user request, or a decided design. When a
harness-improvement idea has no such trace, it is not work — at most it is a proposal in
`future/proposals/`.
