# Backlog Operation

This document owns the backlog operation rules.

The backlog is the planned column of the work-card board (DE-00000007): every entry is a `W-*`
work card that has not started. One card keeps one identity from capture to archive.

## Lifecycle

```text
captured -> triaged -> ready -> selected -> start_work.py moves the card to present/work/items (active)
captured -> triaged -> deferred
captured -> triaged -> rejected
```

Starting work is a physical MOVE performed by `scripts/start_work.py`: it relocates the card
file to `present/work/items/`, sets `status: active`, requires the `scope` declaration, adds the
`present/work/active.md` row, removes the backlog index row, and enforces the venue/split
contract (derive `venue` from `settings.json` `venue_routing`; a `split` kind or a
policy-contradicting venue needs a validated exception decision).

## Gate

1. A planned card has a purpose, source, user value, scope, and success criteria.
2. Grant `ready` only when executable inputs and completion criteria exist.
3. Grant `selected` only when current capacity and priority are confirmed.
4. `rejected` records the reason for not doing it.
5. `index.md` and `views/` never duplicate card bodies.
6. Work fields (`verification`, `retrospective`, `promotion`) and the registration gate apply
   only after the card reaches `present/work/items/`.
