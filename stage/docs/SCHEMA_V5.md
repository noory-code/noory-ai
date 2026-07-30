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
