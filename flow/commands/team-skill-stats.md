---
description: Team monthly skill-usage totals — aggregates each person's records from that month's rollup ticket and flags unused skill candidates
argument-hint: "[YYYYMM]"
---

# /team-skill-stats

You show the team's monthly skill-usage totals. This is the summed result of each person's comments on the specified month's (defaults to the current month) rollup ticket.

## Execution

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/team-usage-report.py" $ARGUMENTS`

- Argument: `YYYYMM` (e.g. 202607). Defaults to the current month.
- Show the output (a Markdown table + unused candidates) to the user **verbatim**. Do not process or summarize it.
- If "No rollup ticket found" appears, that month's push records have not yet been reflected in a ticket — explain that this month's ticket is auto-created once someone pushes.
- Personal (self) stats are `/skill-stats`; team totals are this command.

## Usage

- **Judge the previous month in the following month**: In August, run `/team-skill-stats 202607` to open July's finalized data and make pruning decisions based on the "unused skills" evidence.
- Trust unused candidates only against **installed plugin skills** (see the limitation note above).
