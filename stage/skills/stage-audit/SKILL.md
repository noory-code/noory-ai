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

`TEMPLATE004` means a project guidance document differs from the current template selected for
the project's `settings.json` `language`. Preview safe default refreshes with:

```bash
python3 stage/scripts/refresh_guidance.py --project-root <project-root> --dry-run
```

Run the same command without `--dry-run` to apply the plan. The command derives ownership from
each template's empty-container shape:

- A document with one empty table is replaced except that the project's table data rows are
  preserved.
- A document with one empty list item is replaced except that the project's bullet items and
  their indented continuation lines are preserved.
- A document without an empty container is replaced only when it has no unexplained project
  lines. A populated list does not declare a container and remains in this branch.
- A document whose template has a populated table is skipped by default. Name its path relative to
  `.stage` to authorize full replacement, for example:

```bash
python3 stage/scripts/refresh_guidance.py --project-root <project-root> index.md
```

A project document missing the container declared by its template is skipped by default; naming
the path explicitly authorizes full replacement. A template with two or more empty containers is
refused because the project-owned data boundary is ambiguous, including table/list combinations.
An empty table beside a populated table is refused for the same reason. An empty list beside a
populated list is not, because guidance prose routinely uses bullets above its own container.
Declare an intentionally project-owned document in `settings.json` `guidance_overrides` to
suppress its drift warning and exclude it from the default refresh. Naming an override path
explicitly still authorizes replacement.

Do not use `stage-init --force` as a refresh path. It replaces project-owned indexes and state as
well as guidance and can destroy project data.

## Judgment criteria

- Any `error` means not complete.
- A `warning` is not a failure by default; use `--strict` for release or pre-commit style verification.
- Never silently bypass an audit failure. Fix each finding at its SSOT location.

## Main checks

- Missing required Stage artifacts against the template.
- Stale guidance against the current localized template, excluding declared `guidance_overrides`
  and preserving project items in template-empty table or list containers.
- Work item frontmatter enum violations.
- Completed work with open verification, retrospective, or promotion decision.
- Mismatches between `active.md`, `review.md`, and `items/`.
- Work item hierarchy: invalid epic/story/action placement, cycles, and open records placed under
  finalized hierarchy locations. Placement findings name the missing/invalid location rather
  than suggesting that operators repair a `parent` field.
- Retrospective links (`retrospective_ref` ↔ `work_item`) resolved by item location.
- Decision record links (`decision_refs` ↔ `work_item`) and decision status enums.
- Planned hierarchy status and folder-derived placement references.
- Archived work item location violations.
- Schema-v4 roadmap references, theme/milestone index parity, status ownership, and decision
  chains.

## Roadmap and chain finding codes

These checks run only when `active_topology(.stage) == ACTIVE_TOPOLOGY_V4`.

| Code | Meaning |
|---|---|
| `CHAIN001` | A roadmap `decision_refs`, `predecessor`, or `supersedes` reference is dangling. |
| `CHAIN002` | Predecessor/supersession edges form a cycle. |
| `CHAIN003` | Two or more non-superseded decisions share one predecessor. |
| `CHAIN004` | A roadmap decision chain has multiple effective heads. |
| `CHAIN005` | A transition decision targets a different roadmap record. |
| `CHAIN006` | A transition decision declares an unknown transition token. |
| `ROADMAP001/002` | A milestone record/index row lacks its matching counterpart. |
| `ROADMAP003/004` | A theme record/index row lacks its matching counterpart. |
| `ROADMAP005` | A work card names a missing milestone after roadmap adoption. |
| `ROADMAP006` | A milestone names a missing theme. |
| `ROADMAP007/008` | A milestone/theme index row disagrees with its record fields. |
| `ROADMAP009` | A roadmap record authors status instead of deriving it from decisions. |
