# Cairn

**An append-only decision log.**

A cairn is a stack of stones left to mark a path for those who come after. Cairn
does the same for decisions: each significant choice — a tech stack, an
architecture, a convention — is recorded once and **never edited**. To change a
decision you record a new one that **supersedes** the old; the history stays, so
anyone (or any agent) arriving later can see not just *what* was decided but
*why*, and what it replaced.

Cairn is a **shared substrate**. It is the home for the decisions that govern a
project's work. Tools like [Plot](https://github.com/noory-code/noory-ai/tree/main/plot)
and [Solera](https://github.com/noory-code/noory-ai/tree/main/solera) do not own
it and do not import it — they point at decisions by stable **id, by value**.
Cairn runs **standalone** over plain files under `.noory/cairn/`.

## A decision

Each decision is a Markdown file: YAML frontmatter holds the machine fields
(title, status, what it supersedes); the body holds the prose — context, the
decision, alternatives considered, consequences.

```
---
title: Use Postgres for the primary store
status: accepted
supersedes: null
---
## Context
We need a relational store with strong consistency...

## Decision
We will use Postgres.

## Alternatives
- SQLite — rejected: ...

## Consequences
- All services depend on a running Postgres...
```

- **status** — `proposed` (an option was drafted, e.g. by an agent) or
  `accepted` (a human chose it).
- **supersedes** — the id of a decision this one replaces, or nothing.
- A decision is **in force** when it is `accepted` and no accepted decision
  supersedes it. That is *derived*, never stored — the log is append-only.

## CLI

```bash
cairn --root "$PWD" record "Use Postgres" --status accepted --about auth-stack  # -> CAIRN-001
cairn --root "$PWD" list                                      # all decisions
cairn --root "$PWD" in-force [--about auth-stack]             # the ones still standing
cairn --root "$PWD" show CAIRN-001                            # one decision
cairn --root "$PWD" check --about auth-stack                  # gate: exit 0 if decided, else 1
```

`--root` is the project directory; `.noory/cairn/` lives under it.

The **`about`** tag links a decision to what it governs — a Solera decision-type
work-item names a topic (e.g. `auth-stack`) and gates on
`cairn check --about auth-stack`; a human's `cairn record … --about auth-stack`
makes that gate pass.

MIT licensed.
