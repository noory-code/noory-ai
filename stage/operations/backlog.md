# Backlog Operation

This document owns the backlog operation rules.

## Lifecycle

```text
captured -> triaged -> ready -> selected -> present/work/active.md
captured -> triaged -> deferred
captured -> triaged -> rejected
```

## Gate

1. A backlog item has a purpose, source, user value, scope, and verification criteria.
2. Grant `ready` only when executable inputs and completion criteria exist.
3. Grant `selected` only when current capacity and priority are confirmed.
4. `rejected` records the reason for not doing it.
5. `index.md` and `views/` never duplicate item bodies.
