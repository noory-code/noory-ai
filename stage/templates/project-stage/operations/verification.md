# Verification

This document owns the verification rules.

## Rules

- Both external-perspective and internal-perspective completion are required.
- Tests or equivalent verification must match the change.
- If the project declares a linter or formatter (a config file or a documented command exists), it must pass; if none is declared, this criterion is skipped.
- New behavior needs a verification path.
- `verification: passed` records evidence produced in the session that sets it — the stated checks actually run, with their output observed, not the checks that were merely supposed to run.
- Work without a retrospective is not complete.

## What `passed` means per kind

`verification: passed` on a work item is valid only against the criterion declared for its `kind`. Projects extend this table; the audit warns when a work item uses a kind that has no row here.

| Kind | `passed` means |
|---|---|
| planning | The user (or decision owner) confirmed the plan; open questions routed to `present/state/questions/`. |
| design | The design was reviewed and approved by its owner; decisions recorded in `present/work/decisions/`. |
| development | Tests or equivalent executable verification pass; a declared linter/formatter passes (skipped only when the project declares none). |
| qa | The test scenarios were executed and their results are recorded in the work item. |
| ops | The change was applied and observed working in its target environment. |
