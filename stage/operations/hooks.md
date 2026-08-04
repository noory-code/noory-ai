# Hooks

This document owns the Stage hook rules.

## Rules

- `SessionStart` injects the Stage context and completion gates.
- `PreToolUse` blocks likely rule violations and appends purpose to every tool decision.
- `PostToolUse` completes two-phase intent reservations after the tool actually ran (never blocks).
- `Stop` leaves a summary the next session can pick up.
- Hooks assist the Stage core principles; they do not replace artifact promotion itself.

## What the hooks can see

A hook receives a tool call and decides on it. That is the whole surface: a `Write`, an `Edit`, a
shell command line. What a program does once it is running is not part of that surface, so a script
that opens `.stage/official/` and writes to it passes without an intent, and the `PostToolUse` step
that consumes an intent never fires. The same applies to any editor, git operation, or process
outside this session.

This is a boundary, not a defect to route around. Refusing inline interpreter code (below) closes
the case where the code is invisible on the command line; closing the general case would mean the
guard interpreting arbitrary programs, which it does not attempt.

So an intent is a declaration, not a defence. It records which work item authorized a change to
official truth, and the guard enforces it on the writes it can see. An agent that reaches around
the gate has broken the rule the gate exists for — the record is silently wrong afterwards, and
nothing downstream will say so. When a bulk change needs a program, run it and then verify:
`audit_stage.py` re-derives the tree's consistency independently, and leftover intents show up as
`WORK025`.

## Blocked actions

- Deleting `.stage` entirely.
- Modifying `.stage/official/` without a pending intent in `.stage/.runtime/intents/`.
- Modifying governed files when no work item is open in `work/current/`.
- Deleting a governed source file (`rm`/`del`/`erase`/`Remove-Item`/`ri`) when no work item is open.
- OS-specific executable scripts inside `.stage`.

## Registration gate scope

The registration gate covers nearly all workspace files by default — code, documents, configuration, and design artifacts alike. `.stage/`, `.git/`, and `.discuss/` are excluded. It asks only whether open work exists; a work item's scope is an advisory signal, not write authorization. An outside-scope target passes and the purpose context names the crossing so the executor reports it. Projects adjust governance in `.stage/settings.json` (`governance.exclude_paths`/`exclude_extensions`); every narrowing is reported by the audit. When `settings.json` exists but is unreadable, writes outside `.stage/` are denied until it is repaired (fail-closed).

## Commit gate

The commit gate applies the same registration rule to staged files, same-command `git add`
targets, `git commit -a` changes, and commit pathspecs. At least one work item must be open, but an
outside-scope target passes and the purpose context names the crossing. Independently, a target
owned by a completed work item remains blocked until that item's verification, retrospective, and
promotion decision are final.

## Hierarchy gate

Writing a work item whose `parent` does not exist, points at itself, or opens a child under a finalized parent (completed/archived/rejected) is denied at write time. The audit re-checks the full hierarchy (unknown parents, cycles, open children under finalized parents) as a safety net.

## Question gate

Before `AskUserQuestion` reaches the user, the hook reminds once per question: derive the answer from the work item's Purpose and `official/canon/principles.md` first; ask only when the decision genuinely belongs to the user. Re-asking after the reminder passes.

At `SessionStart`, the open-question view omits a question whose `## Status` section starts with the
machine state token `answered` (Markdown emphasis is allowed). This exception keeps an answered
record in `state/questions/` when durable records still cite it without presenting it as open.

## Purpose context

Every `PreToolUse` result appends live purpose context when active work exists. It never blocks.
The hook selects the driver-provided item when `STAGE_WORK_ITEM_PATH` names an active card;
otherwise it renders every active leaf and its ancestors.

Each branch contributes its leaf scope, an explicit report instruction, and any scope boundary
crossed by a recognized write or commit call. Those signals come first. The live theme, milestone,
epic, story, and action purpose first sentences follow in hierarchy order, one line per level, so
the current action purpose is the final line returned for the tool call. Denied calls retain their
original reason before this context.

## Promotion intent

Official artifact modification uses no body markers. Each pending intent lives in `.stage/.runtime/intents/<work-item>--<basename>-<digest>.json` — one file per (work item, path), created with `scripts/promote_intent.py` (never hand-write the filename), so concurrent sessions do not clobber each other and consumption is an atomic reservation.

```json
{
  "type": "promotion",
  "work_item": "W-00000001",
  "paths": [".stage/official/canon/principles.md"]
}
```

A regular promotion may only modify paths declared in the linked work item's `promotes`.

Archiving is not promotion. Use an archive intent when moving into `official/work/archive/`.

```json
{
  "type": "archive",
  "work_item": "W-00000001",
  "paths": [
    ".stage/official/work/archive/items/W-00000001.md",
    ".stage/official/work/archive/retrospectives/R-00000001.md"
  ]
}
```

An archive intent is valid only when each `items/` target filename matches the `work_item` ID, and each `retrospectives/` target filename matches the work item's `retrospective_ref`.
