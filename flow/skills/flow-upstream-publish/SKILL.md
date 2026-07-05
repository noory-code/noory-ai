---
name: flow-upstream-publish
description: "Publishes plugin-core/upstream improvement items from the retrospective backlog to a project-designated board as detailed tickets. Called from retro-processing backlog routing. Board coordinates are read only from settings.json upstream_board — zero board-name hardcoding. On missing settings/permission, holds publishing + guides."
user-invocable: false
metadata:
  type: procedure
  version: v1.0.0
---

# Upstream Publish

Among items classified as **backlog** in a retrospective, this publishes **plugin-core/upstream improvements** (which the installing user cannot fix directly — `retro-evolution` M5) to a project-designated board as **detailed tickets**. It is the executing behavior of `retro-processing` backlog routing.

> **Essence**: if the procedure only has the convention "register it on the board" but no actual publishing behavior, the improvement item evaporates. This skill performs that publishing. The board coordinates are read **only from the project settings (`upstream_board`)** — the internal default board is seeded into the settings by `flow-config`/`flow-upgrade` (`config-defaults.json`), so this skill does not hold a board name directly.

## When it's called

- When a backlog item is classified as **plugin-core/upstream** in the `retro-processing` procedure (M5 ownership routing).
- A project-local backlog (that project's own playbook/memory item) is not a target of this skill — it is not sent to the board.

## Procedure

### Step 0: Publishing-eligibility check (project-local block — Hard Gate, measurable)

Before publishing, confirm whether the candidate's **target asset path** is a plugin asset — enforcing "don't send project-local" (from "When it's called") as a check, not just words:

- ✅ **Eligible to publish**: the target is under `flow/` (rules / skills / hooks / commands / playbooks / docs / manifest).
- ❌ **Publish rejected**: an app/project source path (`apps/` · `lib/` · a project package), that project's own playbook/memory, an app task tied to an external issue tracker (e.g. a Jira key), "the execution decision belongs to the project" kind. → That project handles it in its own board/tracker (`retro-evolution` M5).
- ⚠️ **Undecidable (ambiguous target)**: hold publishing + confirm with the user. Declaring "plugin-core/upstream" is **only when the target path is a plugin asset**.

> Without this check, an upstream (retro-processing) classification error leaks straight to the board, and project-local tickets pollute the shared board (ground-truth: 35 items flowed in). This gate is the last line of defense for publishing.

### Step 1: Read the board coordinates (SSOT — no hardcoding)

**Explicitly Read** `.flow/settings.json` → check `upstream_board`.

- **Absent**: **hold** publishing + guide the user — "The retrospective upstream board is not configured. Set `upstream_board` in `.flow/settings.json` to enable publishing (see `flow-config`)." Do not publish to a guessed board.
- **Present**: interpret the coordinates per `type`. `github-project` → `owner` + `number`. (Other `type`s follow that type's publishing path.)

### Step 2: Check permission (before publishing)

For `github-project`, the `gh` token needs the `project` scope. Confirm accessibility first with a lookup:

```bash
gh project view <number> --owner <owner> --format json
```

- On failure (permission / does not exist): **hold** publishing + guide — "No access permission to the board. Run `gh auth refresh -h github.com -s project`, then try again." Do not attempt a publish that will fail.

### Step 3: Check for duplicates and validity (already handled = don't publish)

Before publishing, confirm two things — if either applies, do not create a new ticket (to prevent stale-ticket accumulation):

- **Board duplicate**: whether a ticket for the same source retrospective / target asset already exists on the board (matching by title · body source). If so, add a supplementary comment to the existing ticket or skip it — and report to the user.
- **Validity (staleness)**: whether the signal is **already reflected in the current plugin**, checked directly against the target asset (`Grep`/`Read` — the Step 4 ③ target-asset path). If already reflected, hold publishing + report "already reflected" (separate from the Step 0 project-local block — here it's a *genuine plugin asset but already fixed* item).

```bash
gh project item-list <number> --owner <owner> --format json
```

### Step 4: Compose the detailed ticket body (5 elements mandatory — no stubs)

A ticket must **be understandable and immediately actionable from itself alone**. Move over every bit of material already in the retrospective. No one-line stubs.

| element | content |
|------|------|
| **Title** | `[plugin][<target asset>] <one-line improvement gist>` — what/where at a glance |
| **① Problem (background)** | which behavior/omission was the problem. Reproduction · symptom |
| **② Recurrence source** | in which retrospectives, how many times the pattern appeared (source retrospective identifier + occurrence count) |
| **③ Target asset** | the plugin asset to fix (a file among rule/skill/hook/command/playbook/docs) |
| **④ Proposed change** | a concrete proposal for how to fix it |
| **⑤ Completion criteria** | measurable verification (grep/ls/test). No "works fine" |

### Step 5: Publish

```bash
gh project item-create <number> --owner <owner> --title "<title>" --body "<5-element body>"
```

- (If field mapping is needed, add fields matching the board — the board schema is defined by the project.)

### Step 6: Record the publish result

Leave the published ticket (title + URL) in the `retro-processing` processing log (which retrospective pattern → which ticket). Published = that backlog item is tracked as processed out of the queue.

## Ticket example (5 elements)

```markdown
Title: [plugin][purpose-anchoring rule] Strengthen the ultimate-purpose-confirmation gate after pre-confirming an external source

① Problem: A recurring case of starting implementation on an external request (issue/messenger) with the purpose unconfirmed.
② Recurrence source: retro-epic-wf-dogfood-hardening (2x), retro-story-config-retro-ux (1x) — 3 total.
③ Target asset: rules/purpose-anchoring.md (a plugin-core rule).
④ Proposed change: explicitly add an "external-source pre-confirmation" step to the 3-stage gate before escalation.
⑤ Completion criteria: grep "external-source pre-confirmation" rules/purpose-anchoring.md → hit, 0 recurrence in retrospectives.
```

## Verification

- Trace of an explicit Read of `.flow/settings.json` (the board coordinates are read from settings — not hardcoded)
- Zero board-name hardcoding: this skill's body contains no specific board coordinates (owner/number/URL) — the board is read only from settings' `upstream_board` (the coordinate-literal SSOT = the single place `config-defaults.json`)
- A missing-settings/permission hold branch exists (Steps 1·2)
- The ticket body's 5-element form + 1 example exist
- The publish result is recorded in the processing log (Step 6)

## OS compatibility

- Direct `gh` CLI invocation (arg array — not `shell=True`). Identical on macOS·Windows.
- No POSIX-only paths/modules used.
