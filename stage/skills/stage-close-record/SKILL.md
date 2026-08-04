---
name: stage-close-record
description: >-
  Close or reopen Stage observations, questions, and proposals while moving the record, its Status
  evidence, and both indexes together. Use when a settled P, O, or Q record should leave or return
  to the live drawer.
---

# Stage Close Record

Use the command instead of moving or editing records by hand. It keeps the record body, location,
live index, and archive index in one recoverable transaction.

## Close a record

Give one non-empty, one-line reason. Proposals also require exactly one outcome: `accepted`,
`rejected`, or `partial`.

```bash
python3 stage/scripts/close_record.py --project-root <project-root> close O-00000001 --reason "The fix shipped."
python3 stage/scripts/close_record.py --project-root <project-root> close Q-00000001 --reason "The question was answered."
python3 stage/scripts/close_record.py --project-root <project-root> close P-00000001 --reason "The chosen part shipped." --outcome partial
```

The command records the reason in `## Status`, moves the record to its family archive, removes the
live-index entry, and appends the archive-index entry. It preserves the exact live-index entry in
machine metadata so reopening does not have to infer project-owned wording.

## Reopen a record

```bash
python3 stage/scripts/close_record.py --project-root <project-root> reopen O-00000001
```

Reopening removes the command-owned close block, returns the record to its live drawer, restores
the exact prior live-index entry, and removes the archive-index entry.

## Safety boundary

The command is the sanctioned fast path and validates all owned surfaces before writing. It stages
every new file first and restores the starting bytes if a write fails. Direct edits under any
`official/*/archive/` path still require an archive intent, and that intent cannot authorize an
official path outside the declared archive records and indexes.

After either direction, verify the project:

```bash
python3 stage/scripts/audit_stage.py --project-root <project-root>
```
