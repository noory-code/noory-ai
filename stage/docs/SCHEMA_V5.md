# Schema v5 — Work Hierarchy

Schema v5 makes the filesystem path the single source of truth for work scale and parentage.
Runtime scanners accept one shape only: epic, story, or action records below a lifecycle root.

## Record shapes

The same shape applies under `work/planned/`, `work/current/`, and
`official/work/archive/items/`.

```text
W-EPIC/
  _epic.md
  W-STORY/
    _story.md
    W-ACTION.md

W-INDEPENDENT-STORY/
  _story.md
  W-ACTION.md
```

- An epic is `<root>/<id>/_epic.md`.
- A top-level independent story is `<root>/<id>/_story.md`.
- A story below an epic is `<root>/<epic-id>/<story-id>/_story.md`.
- An action is a named Markdown file next to its story record.
- Actions cannot have children.
- Work records do not carry `parent` frontmatter. Their directory placement owns parentage.

Lifecycle moves operate on the top-level directory. A hierarchy is therefore started, closed,
and archived as one move unit while each record keeps its own lifecycle fields and retrospective.

## Work record questions

Every planned and current work record asks for `Purpose`, `User value`, `Scope`, `Risks`,
`Success criteria`, and `Next action`. `Purpose` is exactly one sentence at each scale, with no
character limit. A child states only its own contribution instead of repeating an ancestor's
purpose.

Scale determines the remaining planning questions:

| Scale | Questions |
|---|---|
| Epic | `Stories` lists the stories that combine into the epic. |
| Story | `Actions` lists the actions that combine into the story. |
| Action | `Source` names what produced the indivisible step, and `Dependencies` names what it waits for. |

A current record keeps the same questions as its planned counterpart. It additionally carries
`Related truth`, `Progress`, `Verification`, `Retrospective`, and `Promotion decision`, which are
filled as execution advances. Record-section headings are machine tokens and remain English for
every project language.

## Rejected planned work

`rejected` is a terminal status in both `work/planned/` and `work/current/`, but the two locations
record different histories.

- A hierarchy rejected in `work/planned/` never entered the current lifecycle. Every record in the
  move unit must be `rejected`; its card body owns the rejection reason, and archiving requires no
  retrospective.
- A hierarchy rejected in `work/current/` was started. Every record still requires a completed
  retrospective and its `retrospective_ref` before archiving.
- An archive intent may name a rejected planned card. A promotion intent may not use a planned
  card as its work item.
- Starting a rejected planned card remains invalid. Its next lifecycle transition is direct
  archival, not start.

## Model and effort tiers

A project may name model and effort tiers in `.stage/settings.json`. Without `model_tiers` no
card records a tier, no tool exports or fills a model, and every behavior below is off.

```json
"model_tiers": {
  "scout":    {"claude": {"model": "haiku",  "effort": "low"},    "codex": {"model": "<model>", "effort": "low"}},
  "standard": {"claude": {"model": "sonnet", "effort": "medium"}, "codex": {"model": "<model>", "effort": "medium"}},
  "strong":   {"claude": {"model": "opus",   "effort": "high"}},
  "lead":     {"claude": {"model": "fable",  "effort": "high"}}
},
"tier_routing": {"*": "standard", "chore": "scout", "development": {"action": "standard", "*": "standard"}}
```

- `model_tiers` is a non-empty object of tier names. Declaration order is cost order: the first
  tier is the cheapest, and every reader compares cost only by that order.
- Each tier maps venue names to an object holding `model`, `effort`, or both, as non-empty
  strings written in that venue's own vocabulary. Stage never translates a value between venues.
  An omitted key is neither exported nor filled; a tier without a venue gives that venue nothing.
- `tier_routing` maps a work kind to a tier name, or to an object from scale (`epic`, `story`,
  `action`) to tier name with `"*"` as that kind's fallback. The top-level `"*"` covers every
  other kind. When nothing matches, the card records no tier.
- A routing entry that names an undeclared tier, a malformed table, or `tier_routing` without
  `model_tiers` is invalid: registration and start refuse, and runtime readers act as if no tiers
  were declared.
- `stage/hooks/stage_model_tiers.py` is the only reader of both settings.

A card records its tier in frontmatter `tier:`, after `venue:` (after `environment:` when present).
`register_work.py` writes the routed tier, or the declared tier passed with `--tier`, for current
and planned records alike; it refuses `--tier` naming an undeclared tier or used without
`model_tiers`. `start_work.py` fills a missing `tier:` on every record of the started unit and
keeps one already set. A person may edit `tier:` at any time; readers take the card's value at the
moment they run.

The driver exports the card tier's values as `STAGE_MODEL` and `STAGE_EFFORT`: the executor
receives its own venue's values, and the independent reviewer (and the close review in
`close_work.py`) receives the reviewer venue's values. A command applies the tier only by reading
the variables, for example `--model "$STAGE_MODEL" --effort "$STAGE_EFFORT"`; a command with a
literal `--model` keeps working and keeps its literal model. Each round's `### Driver commands`
entry in the work log adds one line when the card has a tier:

```text
Model tier (JSON): {"tier": "standard", "executor": {"venue": "codex", "model": "...", "effort": "...", "command_uses_model_env": true, "command_uses_effort_env": true}, "reviewer": {"venue": "claude", ...}}
```

`command_uses_*_env` records whether the command text names the variable; false means the round
ran without the tier's value.

## Finished record locations

A record's directory owns whether it is still live. Live drawers hold only records that still
apply; a finished record moves to its family's archive zone under `official/`. No record type
carries a status field for this — the location is the single owner (DE-00000057).

| Live zone | Archive zone | Mover |
|---|---|---|
| `decisions/pending` | `official/decisions/archive` | `archive_work.py`, with the card that consumed the pass |
| `proposals` | `official/proposals/archive` | the close command |
| `state/observations`, `state/questions` | `official/state/archive` | the close command |

`official/decisions/records` is unchanged: it holds decisions that still bind future work.

- A one-shot venue pass (`authorizes: venue_exception`) is never promoted into
  `official/decisions/records`. It moves to the decision archive when its work item archives.
- A proposal records its outcome as `accepted`, `rejected`, or `partial`. Location states that it
  is finished; the outcome field states which of the three.
- An observation or question keeps its closure reason in its body. Reopening is the same
  command in reverse.
- No lifecycle path moves these records by hand, and no path deletes one.

## Runtime boundary

`stage_record_paths.record_paths()` is the recursive filesystem boundary. Runtime work consumers
validate every returned work record with `work_record_scale()` and reject flat root-level
`W-*.md` files. There is no schema-v4 fallback in hooks, audit, close, archive, escalation,
drivers, or context rendering.

Indexes never assemble a flat work filename. They resolve the real record first and write a
relative link to that path.

## Migration

`stage-migrate` accepts schema v3 or v4 and finishes on schema v5.

- A v3 project first performs the historical responsibility relocation to schema v4.
- Every flat v4 card without a parent becomes an independent story.
- A card with an existing parent is placed below that parent's folder. A three-level chain maps
  to epic, story, and action; deeper chains fail before mutation.
- `parent` frontmatter is removed from every migrated card.
- If an archived child belongs to a live parent, the hierarchy is rejoined under the parent's
  lifecycle root. Its terminal disposition becomes `completed` or `rejected`, and its
  retrospective moves back to the live retrospective root.
- Active, review, planned, and archive indexes are rebuilt with actual relative record paths.
- The pending-decision index is refreshed after migrated work cards reach their final paths.
- Work guidance and templates are refreshed before schema activation.
- Audit findings present before migration form a baseline. The migration lists carried findings
  and fails only on findings introduced by the migration.

The direct `glob("B-*.md")` in `migrate_stage.py` remains solely as v3 migration input. B cards
are not work records in schema v5 and no runtime scanner recognizes them.

## Guidance refresh safety

The default guidance refresh derives each file's project-owned container from its current
localized template. One empty table or one empty list item declares that container. An empty
table carries the project's table data rows into the current template. An empty list carries each
project bullet item together with its indented continuation lines. Both merges preserve all
template text outside the container span byte for byte.

A template without an empty container is refreshed only when every non-empty, non-separator
project line also exists in the template. Otherwise the command skips the file, reports the
unexplained line count, and requires the operator to name the path explicitly for full
replacement. A populated list does not declare a container and stays in this branch. A template
with populated tables is skipped by default.

If the project document does not contain the container declared by the template, the default
refresh skips it instead of failing the command. Naming that path authorizes full replacement.
Two or more empty containers are refused as ambiguous, whether they are tables, lists, or one of
each.

An empty table standing beside a populated table is refused for the same reason: a template that
carries reference rows of its own leaves no way to tell which rows the project owns. An empty list
standing beside a populated list is not refused, because guidance prose routinely uses bullets and
refusing that shape would forbid a template from explaining itself above its own container. The
merge then aligns the project's lists with the template's by position.

## Failure and rollback

Before changing durable Stage files, the v4-to-v5 pass records the original `HEAD` and a
byte-for-byte snapshot of the durable `.stage/` tree, excluding `.stage/.runtime/`. It then
installs a maintenance marker. An interruption or verification failure leaves the marker and
journal in place so governed writes in that project fail closed. Excluded project paths and
paths outside that project remain writable. A successful migration removes its completed
journal.

After an interrupted or failed migration and before commit:

```bash
python3 stage/scripts/migrate_stage.py --project-root . --abort
```

The abort restores the exact snapshot and preserves unrelated runtime state. A chained v3
migration then restores its matching original git transaction as well. Journals from unrelated
older transactions are reported and ignored. A successful migration removes its journals and is
not abortable; review its working-tree changes before committing. After commit, rollback uses
`git revert`.

The migration is a topology relocation of existing Stage truth, not a promotion of new official
truth. Like the schema-v3-to-v4 transaction, it runs under the maintenance marker and refuses
concurrent pending promotion machinery rather than creating one archive intent per historical
card.
