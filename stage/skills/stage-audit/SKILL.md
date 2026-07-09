---
name: stage-audit
description: "Audit the .stage artifact structure, work status enums, index mismatches, hierarchy, decision and retrospective links, archive locations, and completion gates."
---

# Stage Audit

Use this skill before judging Stage structure or work status as complete.

## Procedure

Confirm the project root, then run the audit helper.

```bash
python3 stage/scripts/audit_stage.py --project-root <project-root>
```

For machine judgment, run with JSON output.

```bash
python3 stage/scripts/audit_stage.py --project-root <project-root> --format json
```

## Judgment criteria

- Any `error` means not complete.
- A `warning` is not a failure by default; use `--strict` for release or pre-commit style verification.
- Never silently bypass an audit failure. Fix each finding at its SSOT location.

## Main checks

- Missing required Stage artifacts against the template.
- Work item frontmatter enum violations.
- Completed work with open verification, retrospective, or promotion decision.
- Mismatches between `active.md`, `review.md`, and `items/`.
- Work item hierarchy: unknown parents, cycles, open children under finalized parents.
- Retrospective links (`retrospective_ref` ↔ `work_item`) resolved by item location.
- Decision record links (`decision_refs` ↔ `work_item`) and decision status enums.
- Backlog frontmatter status and parent references.
- Archived work item location violations.
