# Stage

Stage is an execution harness that helps an LLM perform consistently across long-running projects.

Stage adds no model capability. Instead it controls the conditions the LLM acts under: artifact status, context ownership, decision gates, verification, and retrospectives — for every kind of work, not only code.

## Generated artifacts

Stage creates a `.stage/` directory inside the project and connects three axes.

- Global time axis: `past`, `present`, `future`
- Per-work time axis: `before`, `during`, `after`, `retrospective`
- Responsibility space axis: `canon`, `model`, `decisions`, `work`, `state`, `operations`

## Core rules

- `past` is the official project truth.
- `present` is in-progress or provisional artifacts.
- `future` is plans or proposals.
- At decision points, use principles (`past/canon/principles.md`) together with context; decision records cite their governing principles.
- Work is not complete until verification and the retrospective are done. What `passed` means is declared per work `kind`.
- Nearly all workspace files are governed by default — planning documents, designs, and configuration included — with exclusions managed in `.stage/settings.json`.
- Work items form hierarchies (`parent`), carry a work `kind`, and trace their lineage to backlog items (`source`/`realized_by`), so every kind of work stays classifiable.
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
- `PreToolUse`: blocks `.stage` destruction, unregistered governed-file modification, hierarchy violations, and `past` modification without a promotion intent; reminds once per question to derive answers from purpose and principles first.
- `PostToolUse`: completes two-phase intent reservations after the tool actually ran (never blocks).
- `Stop`: writes a session summary the next run picks up.

On Codex, hooks run only after a one-time trust approval in the interactive TUI (`/hooks`) — until then they are discovered but silently excluded, including in `codex exec`. Host contract details: `hooks/README.md`.

## Skills

Five entry skills: `stage-init`, `stage-audit`, `stage-decision`, `stage-retrospective`, `stage-discuss`. Descriptions: `skills/README.md`.

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

Migrate a `.stage/` initialized by an older plugin to the plugin-owned operations layout
(idempotent; never deletes content that differs from the plugin copy):

```bash
python3 stage/scripts/migrate_stage.py --project-root .
```

Create a promotion intent after declaring the target paths in the work item's `promotes`:

```bash
python3 stage/scripts/promote_intent.py --project-root . --work-item W-00000001 --path .stage/past/canon/principles.md
```

Create an archive intent to store work records (the retrospective moves in the same intent):

```bash
python3 stage/scripts/promote_intent.py --project-root . --type archive --work-item W-00000001 \
  --path .stage/past/work/archive/items/W-00000001.md \
  --path .stage/past/work/archive/retrospectives/R-00000001.md
```

## Design

[docs/BLUEPRINT.md](docs/BLUEPRINT.md) is the current blueprint.
[docs/DISCUSSION.md](docs/DISCUSSION.md) is the design discussion record.
[docs/IMPLEMENTATION_AUDIT.md](docs/IMPLEMENTATION_AUDIT.md) audits implementation against the blueprint.
(The three docs above are user-facing and written in Korean by owner decision; all executable assets are English.)
