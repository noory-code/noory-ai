---
name: stage-roadmap
description: Create and inspect schema-v4 Stage themes and milestones, and open a milestone pursuit through an explicit decision chain. Use when the user asks to create a roadmap theme or milestone, begin milestone pursuit, list roadmap state, or inspect roadmap lifecycle.
---

# Stage Roadmap

This skill is schema-v4-only. Before doing roadmap work, confirm that the project-local
`.stage/settings.json` contains the exact integer `schema_version: 4`. The CLI performs the same
check and exits without writing on every v3 project.

## Flow

Run commands from the plugin repository or substitute the installed plugin root for `stage/`.
Place `--project-root` before the subcommand.

Create a theme first:

```text
python3 stage/skills/stage-roadmap/manage_roadmap.py --project-root <root> \
  create-theme --title "Theme title" --intent "Outcome"
```

Create a milestone under that theme:

```text
python3 stage/skills/stage-roadmap/manage_roadmap.py --project-root <root> \
  create-milestone --theme TH-NNNNNNNN --title "Milestone title" \
  --purpose "Purpose" --period "Period" --completion-criteria "Criterion"
```

Open the milestone's initial pursuit:

```text
python3 stage/skills/stage-roadmap/manage_roadmap.py --project-root <root> \
  open-pursuit M-NNNNNNNN
```

List themes, milestones, and their computed status:

```text
python3 stage/skills/stage-roadmap/manage_roadmap.py --project-root <root> list
```

## Contracts

- Theme and milestone IDs use the registry's shared roadmap-family counter. A newly created
  `TH-` and the next `M-` therefore receive different numeric identities.
- Records are copied from the bundled schema-v4 templates and their owning theme or milestone
  index is updated in the same command.
- Theme records contain `id` and `decision_refs`; milestone records contain `id`, `theme`, and
  `decision_refs`. Never add `status` to either record or to its index row.
- Computed status is `planned` when no decided transition exists, `active` when the effective
  head opens pursuit, `closed` when the effective head closes it, and `invalid` when chain
  integrity cannot establish one truthful head.
- `open-pursuit` creates a decided `DE-` record in `decisions/pending/`, sets
  `roadmap_item: M-*` and `transition: pursuit`, cites SSOT and Honesty, and appends the decision
  to the milestone's `decision_refs`.
- Every later transition declares `predecessor:`; a replacement also declares `supersedes:`.
  The audit rejects dangling references, cycles, unresolved forks, and multiple effective
  heads. Chain structure, never an ID number or timestamp, determines the effective state.
- Closure, closure snapshots, promotion-time revalidation, and closed-snapshot attribution
  gates are not part of this command. They belong to the later roadmap-closure implementation.

After mutations, run `python3 stage/scripts/audit_stage.py --project-root <root>` and resolve
every error at its owning record or index.
