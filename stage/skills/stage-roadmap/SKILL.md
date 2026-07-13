---
name: stage-roadmap
description: Create, pursue, close, reopen, and inspect schema-v4 Stage themes and milestones through explicit decision chains and immutable closure evidence. Use when the user asks to create a roadmap theme or milestone, begin or close milestone pursuit, reopen a closed milestone, list roadmap state, or inspect roadmap lifecycle.
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

Close a milestone after every attributed W card is terminal:

```text
python3 stage/skills/stage-roadmap/manage_roadmap.py --project-root <root> \
  close-milestone M-NNNNNNNN \
  --attestation "Exact completion-criteria evidence and conclusion"
```

If closure refuses, resolve every listed card before retrying:

- Archive accepted work; the v4 archiver stamps `terminal_disposition: accepted`.
- Explicitly reject work with `terminal_disposition: rejected`, or archive the rejected card.
- Re-link work that does not belong to this milestone.
- Never edit the generated closure basis or its attestation after creation.

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
- `close-milestone` refuses unless the milestone has one active pursuit head and every linked W
  card is terminal. It creates a decided `transition: closure` record whose `predecessor:` is
  that head, freezes the exact sorted W ids and card-owned `terminal_disposition` values, embeds
  the exact `--attestation` text, and appends the decision to `decision_refs`.
- Promoting a closure into `official/decisions/records/` re-reads all W locations through the
  registry. Promotion fails closed with an id-by-id diff when a disposition changed, a frozen
  card is missing or re-attributed, or a newly linked card is absent from the basis.
- A decided closure is effective immediately. A W id in its frozen basis cannot change its
  `milestone:` field. The same projected file-write change set may do so only when it also adds
  a decided chain member for the same milestone, declares `transition: reopen`, names the
  closure in both `predecessor:` and `supersedes:`, and appends that decision id to the
  milestone's `decision_refs`.
- Reopen only by supersession. Once the decided/promoted reopen record supersedes the closure,
  computed milestone status returns to `active`; never delete or edit the closure record and
  never author a status field on the milestone.

After mutations, run `python3 stage/scripts/audit_stage.py --project-root <root>` and resolve
every error at its owning record or index.
