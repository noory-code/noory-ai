# Observations

This directory owns the SSOT of current observations.

## Rules

- One observation has one file.
- `opened:` carries the date the observation was first written, as `YYYY-MM-DD`. The session-start
  view reads it to state how long each observation has been open; filesystem timestamps cannot
  stand in, because a fresh clone or a git worktree checkout stamps every record with today.
- A verified observation can be promoted to `past/`.
- A stale observation changes status; it is not deleted.
