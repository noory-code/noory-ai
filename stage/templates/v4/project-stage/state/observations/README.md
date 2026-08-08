# Observations

This directory owns the SSOT of current observations.

## Rules

- One observation has one file.
- `opened:` carries the date the observation was first written, as `YYYY-MM-DD`. The session-start
  view reads it to state how long each observation has been open; filesystem timestamps cannot
  stand in, because a fresh clone or a git worktree checkout stamps every record with today.
- A verified observation can be promoted to `official/`.
- A stale observation changes status; it is not deleted.
- A closed observation states directly under its heading what closed it. Since the record stays,
  anyone opening the file has to see whether it is still live; marking it only in the index leaves
  the file asserting something untrue.

