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

The direct `glob("B-*.md")` in `migrate_stage.py` remains solely as v3 migration input. B cards
are not work records in schema v5 and no runtime scanner recognizes them.

## Failure and rollback

Before changing durable Stage files, the v4-to-v5 pass records the original `HEAD` and a
byte-for-byte snapshot of the durable `.stage/` tree, excluding `.stage/.runtime/`. It then
installs a maintenance marker. An interruption or verification failure leaves the marker and
journal in place so other Stage writes fail closed.

Before commit:

```bash
python3 stage/scripts/migrate_stage.py --project-root . --abort
```

The abort restores the exact snapshot and preserves unrelated runtime state. A chained v3
migration then restores its original git transaction as well. After commit, rollback uses
`git revert`.

The migration is a topology relocation of existing Stage truth, not a promotion of new official
truth. Like the schema-v3-to-v4 transaction, it runs under the maintenance marker and refuses
concurrent pending promotion machinery rather than creating one archive intent per historical
card.
