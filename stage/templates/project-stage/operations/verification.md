# Verification kinds

This document owns this project's `kind -> passed` verification criteria.

Common verification rules are plugin-owned; see `operations/verification.md` in the installed
Stage plugin. `verification: passed` on a work item is valid only against the criterion declared
for its `kind` below. Extend this table with the project's own kinds; the audit warns when a work
item uses a kind that has no row here.

| Kind | `passed` means |
|---|---|
| planning | The user (or decision owner) confirmed the plan; open questions routed to `present/state/questions/`. |
| design | The design was reviewed and approved by its owner; decisions recorded in `present/work/decisions/`. |
| development | Tests or equivalent executable verification pass; a declared linter/formatter passes (skipped only when the project declares none). |
| qa | The test scenarios were executed and their results are recorded in the work item. |
| ops | The change was applied and observed working in its target environment. |
