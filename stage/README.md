# Stage

**A stage the heroes can run wild on — but it has to have a purpose.**

Stage is an execution harness that helps an LLM perform consistently across long-running projects.

Stage adds no model capability. Instead it controls the conditions the LLM acts under: artifact status, context ownership, decision gates, verification, and retrospectives — for every kind of work, not only code.

Execution stays free; purpose stays strict. Stage never tells the executor how to work, and it never lets work float free of what it is for. [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) owns why the harness is shaped this way.

## Generated artifacts

Stage creates a `.stage/` directory inside the project and connects three axes.

- Lifecycle axis (semantic): `planned`, `current`, `official` — every artifact is always in
  exactly one, enforced by the gates rather than by any folder tense.
- Per-work axis: `before`, `during`, `after`, `retrospective`
- Responsibility space axis: `official` (canon, model, promoted decisions, archived work),
  `work`, `decisions`, `state`, `proposals`, `roadmap`, `operations`

## Core rules

- `official/` is the promoted, settled project truth (canon, model, promoted decisions, archived work).
- `state/` holds in-progress observations, questions, assumptions, and risks; `work/current/` holds work being executed.
- `proposals/` and planned work cards (`work/planned/`) are plans, not truth.
- At decision points, use principles (`official/canon/principles.md`) together with context; decision records cite their governing principles.
- Work is not complete until verification and the retrospective are done. What `passed` means is declared per work `kind`.
- Nearly all workspace files are governed by default — planning documents, designs, and configuration included — with exclusions managed in `.stage/settings.json`.
- A work card is one `W-*` artifact across its whole life, moving `work/planned` (planned) →
  `work/current` (started via `scripts/start_work.py`) → `official/work/archive` (closed) like a
  kanban card. Cards form epic/story/action hierarchies through their folder paths and may
  attribute to a roadmap milestone
  (`milestone`), and carry a work `kind`, so every kind of work stays classifiable.
- The roadmap (`roadmap/themes`, `roadmap/milestones`) groups work toward goals and directions;
  a milestone's status is computed from its decision chain, and its closure freezes an immutable
  basis of terminal work cards.
- The core stays Markdown, plain files, and relative paths so it works on Codex, Claude, Windows, Linux, and macOS.
- A single document only holds an index or policy. Every durable individual artifact has its own file.
- Common operational rules are plugin-owned (`operations/` in this plugin) and are not copied into
  projects. `.stage/operations/` holds only project policy: the `kind -> passed` verification
  criteria plus any overrides declared in `settings.json` `operations_overrides`.
- A project can declare a `kind -> venue` role policy (`settings.json` `venue_routing`, e.g.
  design work to a Claude window, implementation to a Codex window). Registration derives each
  item's venue from it, exceptions require a linked decision record, and the audit reports
  missing, unknown, and policy-contradicting venues. No policy declared → venue stays a purely
  advisory per-item field.
- Human-readable `.stage/` documents follow the project's declared language (`settings.json`
  `language`, default `en`; `ko` templates are bundled, other tags fall back to English while
  still governing generated records). Machine-readable tokens — IDs, paths, frontmatter keys,
  enum values, record section headings — stay language-neutral, so hooks and the audit parse
  every language identically. The Stage setting owns `.stage/` document language; host
  instructions own everything outside `.stage/`.

## Hooks

Stage ships one hook set in `hooks/` that both Claude Code and Codex execute (Codex auto-discovers the same `hooks/hooks.json` from the installed plugin).

- `SessionStart`: injects the current Stage context, core principles, and the artifact map.
- `PreToolUse`: blocks `.stage` destruction, unregistered governed-file modification, hierarchy violations, and `official/` modification without a promotion intent; reminds once per question to derive answers from purpose and principles first.
- `PostToolUse`: completes two-phase intent reservations after the tool actually ran (never blocks).
- `Stop`: writes a session summary the next run picks up.

On Codex, hooks run only after a one-time trust approval in the interactive TUI (`/hooks`) — until then they are discovered but silently excluded, including in `codex exec`. Host contract details: `hooks/README.md`.

## Skills

Entry skills: `stage-init`, `stage-work`, `stage-audit`, `stage-decision`, `stage-retrospective`,
`stage-close-record`, `stage-archive`, `stage-handoff`, `stage-roadmap`, `stage-migrate`, and
`stage-discuss`. Descriptions: `skills/README.md`.

## CLI helpers

The plugin ships cross-platform Python helpers.

```bash
python3 stage/scripts/init_stage.py --project-root .
```

The helper copies only missing template files. Use `--force` only to intentionally replace existing `.stage/` files.

Audit the Stage structure and work status:

```bash
python3 stage/scripts/audit_stage.py --project-root .
```

Migrate a `.stage/` from an older schema. The `stage-migrate` skill first performs the
schema-v3-to-v4 responsibility relocation when needed, then moves every v4 flat work card into
the schema-v5 epic/story/action hierarchy. The fail-closed transaction snapshots the durable
Stage tree, installs a maintenance marker, rewrites indexes from actual record paths, stamps
`schema_version: 5`, and runs strict audit. It never commits, and its journal supports an exact
pre-commit abort:

```bash
python3 stage/scripts/migrate_stage.py --project-root .
```

Create a promotion intent after declaring the target paths in the work item's `promotes`:

```bash
python3 stage/scripts/promote_intent.py --project-root . --work-item W-00000001 --path .stage/official/canon/principles.md
```

Create an archive intent to store work records (the retrospective moves in the same intent):

```bash
python3 stage/scripts/promote_intent.py --project-root . --type archive --work-item W-00000001 \
  --path .stage/official/work/archive/items/W-00000001.md \
  --path .stage/official/work/archive/retrospectives/R-00000001.md
```

## Design

[docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) owns what Stage is for; every other design document owns
how it is built.
[docs/BLUEPRINT.md](docs/BLUEPRINT.md) is the responsibility-topology blueprint introduced with schema v4.
[docs/SCHEMA_V5.md](docs/SCHEMA_V5.md) is the current work-hierarchy contract.
[docs/SCHEMA_V4.md](docs/SCHEMA_V4.md) is the historical schema-v4 topology design.
[docs/DISCUSSION.md](docs/DISCUSSION.md) and [docs/IMPLEMENTATION_AUDIT.md](docs/IMPLEMENTATION_AUDIT.md) are historical v3 design records, kept as history.
(The three docs above are user-facing and written in Korean by owner decision; all executable assets are English.)
