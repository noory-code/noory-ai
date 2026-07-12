# Verification

This document owns the common verification rules for every Stage project.

Project-specific `kind -> passed` criteria are project policy and live in the consuming
project's `.stage/operations/verification.md`.

## Rules

- Both external-perspective and internal-perspective completion are required.
- Tests or equivalent verification must match the change.
- If the project declares a linter or formatter (a config file or a documented command exists), it must pass; if none is declared, this criterion is skipped.
- New behavior needs a verification path.
- `verification: passed` records evidence produced in the session that sets it — the stated checks actually run, with their output observed, not the checks that were merely supposed to run.
- Work without a retrospective is not complete.

## What `passed` means per kind

`verification: passed` on a work item is valid only against the criterion declared for its
`kind` in the project's `.stage/operations/verification.md` table. The audit warns when a work
item uses a kind that has no row there.
