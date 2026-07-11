# Hooks

This document owns the Stage hook rules.

## Rules

- `SessionStart` injects the Stage context and completion gates.
- `PreToolUse` blocks executions that are likely rule violations before they run.
- `PostToolUse` completes two-phase intent reservations after the tool actually ran (never blocks).
- `Stop` leaves a summary the next session can pick up.
- Hooks assist the Stage core principles; they do not replace artifact promotion itself.

## Blocked actions

- Deleting `.stage` entirely.
- Modifying `.stage/past/` without a pending intent in `.stage/.runtime/intents/`.
- Modifying source files not registered in `present/work/items/`.
- Deleting a registered source file (`rm`/`del`/`erase`/`Remove-Item`/`ri`) without the same registration a write would need.
- OS-specific executable scripts inside `.stage`.

## Registration gate scope

The registration gate covers nearly all workspace files by default — code, documents, configuration, and design artifacts alike. `.stage/`, `.git/`, and `.discuss/` are excluded. Projects adjust the scope in `.stage/settings.json` (`governance.exclude_paths`/`exclude_extensions`); every narrowing is reported by the audit. When `settings.json` exists but is unreadable, writes outside `.stage/` are denied until it is repaired (fail-closed).

## Hierarchy gate

Writing a work item whose `parent` does not exist, points at itself, or opens a child under a finalized parent (completed/archived/rejected) is denied at write time. The audit re-checks the full hierarchy (unknown parents, cycles, open children under finalized parents) as a safety net.

## Question gate

Before `AskUserQuestion` reaches the user, the hook reminds once per question: derive the answer from the work item's Purpose and `past/canon/principles.md` first; ask only when the decision genuinely belongs to the user. Re-asking after the reminder passes.

Shell write detection is best-effort. The default detection targets are redirects, `cp`, `mv`, `tee`, and `sed -i`, plus delete operands of `rm`/`del`/`erase`/`Remove-Item`/`ri`. File writes inside inline interpreters are outside the detection range.

## Promotion intent

Official artifact modification uses no body markers. Each pending intent lives in `.stage/.runtime/intents/<work-item>--<basename>-<digest>.json` — one file per (work item, path), created with `scripts/promote_intent.py` (never hand-write the filename), so concurrent sessions do not clobber each other and consumption is an atomic reservation.

```json
{
  "type": "promotion",
  "work_item": "W-00000001",
  "paths": [".stage/past/canon/principles.md"]
}
```

A regular promotion may only modify paths declared in the linked work item's `promotes`.

Archiving is not promotion. Use an archive intent when moving into `past/work/archive/`.

```json
{
  "type": "archive",
  "work_item": "W-00000001",
  "paths": [
    ".stage/past/work/archive/items/W-00000001.md",
    ".stage/past/work/archive/retrospectives/R-00000001.md"
  ]
}
```

An archive intent is valid only when each `items/` target filename matches the `work_item` ID, and each `retrospectives/` target filename matches the work item's `retrospective_ref`.
