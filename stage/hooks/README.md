# Stage Hooks

This directory owns the hooks that apply Stage principles at execution time.

## Hooks

- `SessionStart`: injects the `.stage/` state and completion gates into the session context.
- `PreToolUse`: blocks `.stage` deletion, unregistered governed-file modification, and official artifact modification without a promotion intent.
- `Stop`: writes `.stage/.runtime/session-summary.md`.

## Blocking criteria

- Deleting `.stage` entirely is forbidden.
- `.stage/past/` modification is allowed only when `.stage/.runtime/promote-intent.json` points at the target paths and a completed work item, and the target paths are declared in that item's `promotes` (or, for archive intents, match the item's own ID and `retrospective_ref`).
- Governed-file modification is allowed only when an active work item in `present/work/items/` has a matching scope. Governance is broad by default — nearly all workspace files except `.stage/`, `.git/`, and `.discuss/` — and is adjusted per project via `.stage/settings.json` exclusions.
- Work item hierarchy is enforced at write time: unknown parents, self-parents, and opening a child under a finalized parent are denied.
- The question tool (`AskUserQuestion` on Claude, `request_user_input` on Codex) gets a once-per-question reminder to derive the answer from the work purpose and canon principles first; re-asking passes.
- Intermediate commits are allowed. The commit gate checks that staged files, same-command `git add` targets, and `git commit -a` targets are registered to work items.
- OS-specific executable scripts are not allowed inside `.stage`.

## Limits

Shell write detection is best-effort. The default detection targets are redirects, `cp`, `mv`, `tee`, and `sed -i`. File writes inside inline interpreters are outside the detection range.

Write-target extraction reads `path`/`file`-keyed input fields plus `apply_patch` file headers. A hypothetical host alias that carries its write target under a different key (e.g. `target`, `uri`) would pass the gates unexamined — no documented Claude/Codex tool does this (Codex round-10 review, Low).

Governance settings are fail-closed: when `.stage/settings.json` exists but is unreadable or malformed, writes outside `.stage/` are denied until the file is repaired (repairing `.stage/settings.json` itself stays allowed).

`apply_patch` payloads are parsed for `*** Add/Update/Delete File:` and `*** Move to:` targets, so patch-body paths pass through the registration and promotion gates like any other write.

## Host contract

Both hosts consume the same `hooks/hooks.json` (Claude hook schema) and send Claude-compatible JSON on stdin (`tool_name`, `tool_input`, `cwd`, `hook_event_name`). Host differences the hook absorbs:

| Concern | Claude | Codex |
|---|---|---|
| File edits | `Write`/`Edit`/`MultiEdit` with `file_path` | `apply_patch` with `tool_input.command` = patch body |
| Shell | `Bash` with `command` | `Bash` (canonical name) with `command` |
| Question tool | `AskUserQuestion` | `request_user_input` |
| Workspace root | `CLAUDE_PROJECT_DIR` env | no env var — hook cwd and payload `cwd` are the workspace |
| Allow output | exit 0, empty stdout = no opinion — the call falls through to the host's normal permission flow (an explicit `allow` would bypass permission prompts entirely) | same (an explicit `permissionDecision: "allow"` is additionally rejected as unsupported output) |
| Deny output | `hookSpecificOutput.permissionDecision: "deny"` + reason | same |
| Stop output | `systemMessage` only | same (`decision` is accepted only as the literal `"block"`) |

### Codex hook trust

Codex executes plugin hooks only after they are trusted once in the interactive TUI (`/hooks`); trust persists as `[hooks.state.*] trusted_hash` entries in `~/.codex/config.toml`. Until then hooks are discovered but silently excluded — including in `codex exec` — so Stage enforcement on Codex requires the one-time trust approval after `codex plugin add stage`.

## Portability

The hook body uses only the Python standard library. `hooks.json` runs `python3` directly, so the hook and its tests must run on whatever `python3` the host machine provides — annotations stay lazy via `from __future__ import annotations` (verified on system Python 3.9.6). Windows environments without a `python3` command need the Python launcher or a host adapter.
