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
- Retired work list files (`work/active.md`, `work/review.md`, `work/planned/index.md`) left by an
  earlier Stage version (INDEX007, a warning): the views are derived from card status, so delete them.
- Work item hierarchy: invalid epic/story/action placement, cycles, and open records placed under
  finalized hierarchy locations. Placement findings name the missing/invalid location rather
  than suggesting that operators repair a `parent` field.
- Retrospective links (`retrospective_ref` ↔ `work_item`) resolved by item location.
- Decision record links (`decision_refs` ↔ `work_item`) and decision status enums.
- Planned hierarchy status and folder-derived placement references.
- Archived work item location violations.
- Schema-v4 roadmap references, theme/milestone index parity, status ownership, and decision
  chains.
- Evidence a close leaves, and index titles: see "After a Stage plugin update" below.

## After a Stage plugin update

A project made by an earlier Stage keeps records and settings in that version's shape. These
findings name each place; none of them is fixed by editing a record by hand.

| Code | Level | Meaning | What to do |
|---|---|---|---|
| `DECISION005` | error | The official decision index has no title column, or a title differs from its record's heading. | Run `python3 stage/scripts/refresh_index_titles.py --project-root .` |
| `ARCHIVE005` | warning | The work archive index has rows without a title that their archived card can fill. One finding names the index and the row count. | The same command. It never replaces a title a row already has. |
| `REVIEW003` | warning | A command under `review.reviewers` or `review.strengths` in `settings.json` does not contain the words `method`, `ran`, `read`, and `unable`, so it does not tell the reviewer to name how it judged each criterion. `close_work.py` rejects a verdict without `method`, so a close review through that command fails. | Add the `method` sentences from the `review` comment of `templates/v4/project-stage/settings.jsonc` to the command (`operations/review.md`, "How the reviewer judges"). |
| `WORK030` | warning | A card has a `- Checks at close` line and no `- Load at close` line, and it closed on a later day than the project's first card that carries a load line. | Do not write the line by hand. Confirm which Stage version the closing session ran; a stale plugin cache is the usual cause. |

```yaml
work030_cut_off:
  judged: cards whose last `- Checks at close` day is later than the earliest `- Load at close`
    day among the project's own cards
  not_judged:
    - cards closed on or before that day, because the project's Stage did not write the line yet
      or the day alone cannot say which close came first
    - cards with no `- Checks at close` line, because nothing dates their close
    - every card of a project that has no `- Load at close` line at all
  why_not_a_fixed_date_or_card_id: another project updates its plugin on another day and numbers
    its cards by itself
```

`refresh_index_titles.py` is the one command to run after an update. It renders the
pending-decision index, fills the official decision index's titles, and fills the work archive
index's titles; a second run changes nothing.

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

## Model tier finding codes

These checks run only when `.stage/settings.json` declares `model_tiers` or a card names a `tier:`
(`docs/SCHEMA_V5.md` → `Model and effort tiers`). They compare cards in the current work zone only.

| Code | Meaning |
|---|---|
| `TIER001` | `model_tiers` or `tier_routing` is invalid (error). |
| `TIER002` | A current card names a tier the settings do not declare (error). |
| `TIER003` | The latest driver round for a current card ran on other model or effort values than the card's tier gives now, or its command does not read `$STAGE_MODEL` / `$STAGE_EFFORT` (warning). |
| `TIER004` | A subagent that ran for current cards used another model or effort than their tier gives; a stated over-tier reason is quoted (warning). |
| `TIER005` | A model-usage record line could not be read and was skipped (warning). |
| `TIER006` | `model_fallbacks` or `usage_limit_patterns` is invalid (error). Checked even without `model_tiers` (`docs/SCHEMA_V5.md` → `Model fallbacks on usage limits`). |
| `TIER007` | `model_fallbacks` names a venue, and `executors.<venue>` or `review.reviewers.<venue>` does not contain `STAGE_MODEL`, so that command cannot switch model (warning). Checked even without `model_tiers`. |
