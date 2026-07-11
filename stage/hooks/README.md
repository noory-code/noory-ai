# Stage Hooks

This directory owns the hooks that apply Stage principles at execution time.

## Hooks

- `SessionStart`: injects the `.stage/` state and completion gates into the session context — current state, active work, review candidates, an inventory of host-project instructions (`CLAUDE.md`, `AGENTS.md`, `.claude/rules|skills`, …) with a use-and-challenge directive, the newest 3 open questions (`present/state/questions/`), backlog records with `status: selected`, and the most recent session handoff — and prunes stale question-ack markers.
- `PreToolUse`: blocks `.stage` deletion, unregistered governed-file modification, and official artifact modification without a promotion intent.
- `Stop`: writes `.stage/.runtime/sessions/<session_id>.md`.

## Blocking criteria

- Deleting `.stage` entirely is forbidden — recursive `rm`/`rmdir`/`Remove-Item` and `find .stage -delete`/`-exec rm` are all blocked, including behind find's pre-path traversal options (`find -L .stage -delete`) and the `--` end-of-options separator. A recursive delete rooted at an ancestor of `.stage` (`rm -rf .`, `find . -delete`) is denied even when a find filter is present — the hook does not evaluate find expressions, so scope destructive sweeps below `.stage`'s branch (e.g. `find src -name '*.pyc' -delete`). Write targets are resolved through existing symlinks and `..` first, so an aliased path cannot dodge classification.
- `.stage/past/` modification is allowed only when a pending intent in `.stage/.runtime/intents/<work-item>.json` points at the target paths and a completed work item, and the target paths are declared in that item's `promotes` (or, for archive intents, match the item's own ID and `retrospective_ref`).
- Governed-file modification is allowed only when an active work item in `present/work/items/` has a matching scope. Governance is broad by default — nearly all workspace files except `.stage/`, `.git/`, and `.discuss/` — and is adjusted per project via `.stage/settings.json` exclusions.
- Work item hierarchy is enforced at write time: unknown parents, self-parents, and opening a child under a finalized parent are denied.
- The question tool (`AskUserQuestion` on Claude, `request_user_input` on Codex) gets a once-per-question reminder to derive the answer from the work purpose and canon principles first; re-asking passes.
- Intermediate commits are allowed. The commit gate checks that staged files, same-command `git add` targets, and `git commit -a` targets are registered to work items.
- OS-specific executable scripts are not allowed inside `.stage`.

## Runtime concurrency

`.stage/.runtime/` is multi-session by construction — several Claude/Codex sessions can share one `.stage` without clobbering each other:

- `intents/<work-item>--<basename>-<digest>.json` — one pending intent per (work item, entry-canonical workspace-relative path), so consuming an authorization is an atomic **rename reservation** (`intent.json` → `intent.json.claim-<id>`): the session that wins the rename proceeds, a concurrent session whose rename fails is denied rather than riding the same one-shot authorization (the claim file is unlinked afterward, and a stale claim from a crashed session is swept after a day). No shared-file rewrite, hence no lost-update race. The filename embeds the target basename plus a 10-hex digest of the full path (bounded length, deterministic replant). The promotion gate requires every targeted path to be covered by exactly one pending intent — zero coverage or more than one candidate per path denies (fail closed on ambiguity) — and validates all involved intents before reserving any. Legacy single-slot and multi-path intent files are split into this layout on first read (originals kept unless every replacement persisted); `session-summary.md` migrates to `sessions/legacy.md` (or a numbered slot if that is taken, never dropping a handoff).
- `sessions/<session_id>.md` — one Stop handoff per session; SessionStart injects the most recent handoff, plus any others sharing its mtime (two sessions can Stop in the same coarse-resolution tick), and Stop prunes to the newest 5. The just-written summary is pinned, and files younger than a day are never pruned (under cross-host clock skew the cap is soft for at most a day rather than losing a live session's handoff).
- `question-ack/<session_id>` — the question-gate reminder marker is per session; SessionStart removes markers older than a day (abandoned sessions).

The session dimension comes from the `session_id` field both hosts send in hook stdin; a payload without it falls back to a shared `default` slot.

## Limits

Shell write detection is best-effort. The default detection targets are redirects, `cp`, `mv`, `tee`, and `sed -i`. File writes inside inline interpreters are outside the detection range.

The delete gate tokenizes the whole command with shell control operators (`;`, `&`, `&&`, `|`, `||`, unquoted newlines) as their own tokens — quoting is honored, line continuations are spliced, heredoc bodies are dropped, and a find `-exec … \;` terminator stays inside its find group. It tracks the effective cwd across `cd`/`pushd`/`popd`/`cd -` (with a directory stack and OLDPWD) as a SET of possible directories — a conditionally executed, backgrounded, or pipeline-fed cd unions its state with the prior one, a failed cd (missing directory, multi-operand error, unknown option) keeps the caller's cwd, and the gate denies if ANY possible cwd would remove the Stage tree (fail closed). This models an honest actor's shell, not an adversary: cwd changes inside `eval`, command substitution, `env -C`, or an explicit subshell `(cd x; …)` are not evaluated, and a governance root the operator deliberately sabotages is out of scope (see the closing paragraph).

Coverage is deliberately scoped to what an honest actor would plausibly type. Detection resolves the common shell forms above; a set of rarely-hand-typed constructs is left as documented best-effort rather than chased into a full shell-parser reimplementation: `cd -P` physical mode (only logical `cd -L` is modelled), indexed directory-stack ops with a non-zero index (`pushd +N`/`popd +N`), and find whose traversal mode or destructive action is spelled through another predicate's operand (`find … -name -P …`, a file literally named `-delete`). These do not arise from an accidental or shortcut `.stage` deletion, which is the harness's protection target. (External-process wrappers that cannot run the `cd` builtin — `nohup`, `nice`, `time` — are not peeled, so their apparent `cd` is a no-op and a following relative delete stays anchored at the caller, which is the correct fail-closed behavior.)

Write-target extraction reads `path`/`file`-keyed input fields plus `apply_patch` file headers. A hypothetical host alias that carries its write target under a different key (e.g. `target`, `uri`) would pass the gates unexamined — no documented Claude/Codex tool does this (Codex round-10 review, Low).

Gating is keyed on tool NAMES: a file-writing tool whose name is outside the built-in allowlist — typically an MCP server tool such as `mcp__filesystem__write_file` — bypasses every gate, silently. Projects that use such tools register the exact names in `.stage/settings.json` `extra_write_tools`; registered names are classified as write tools before the unknown-name early allow, so the registration, promotion, hierarchy, and governance gates apply (targets are matched entry-canonically, like `apply_patch`). Shape-based auto-detection (any payload with path+content) was considered and rejected: it would deny non-file tools that happen to carry those fields. When `settings.json` is unreadable, the registered names cannot be read back — those tools fall back to this ungated default until the file is repaired, while built-in tools stay behind the governance fail-closed deny.

A pending intent is a path-scoped capability: once planted, any session may perform the matching `past` write, and the hook cannot attribute the write to a specific work item (hook stdin carries no work-item context). This is unchanged from the single-slot design; the binding (completed item + declared `promotes`/archive filename) plus the ambiguity deny above are the enforced surface.

Intent consumption happens at PreToolUse time, after every other gate has passed (the promotion gate validates last, so a call denied by the registration, hierarchy, governance, or commit gate never burns the authorization). What remains is the window between the hook's allow and the write actually landing: if the tool call itself fails or the user rejects the permission prompt, the consumed intent is gone. Re-issuing is one command — `scripts/promote_intent.py --work-item <id> --path <path>`. A post-execution restore protocol would need a PostToolUse hook on both hosts; Codex support for that event is unverified, so consumption stays at pre-time.

Write targets are classified by the union of three forms — resolved-canonical (symlink parents + `..`, leaf included), entry-canonical (parents resolved, leaf kept as named), and lexical — so a symlink or `..` cannot re-enter `.stage` unseen, a symlink whose leaf sits in `.stage/past` still hits the promotion gate, and a governed symlink *entry* (`src/link`) whose target is outside stays registration-gated when it is unlinked or replaced. The resolved (leaf-dereferenced) form participates only in fail-closed directions — detection and governance INCLUSION — never in authorization or exemption: exact-entry authorizations (a work item's `promotes`, pending intents, archive filenames) and scope matching compare the entry-canonical form, so a grant or scope for one leaf never covers a sibling symlink aliasing the same target, and configured governance exclusions win on the entry/lexical forms only (structural `.stage`/`.git`/`.discuss` exclusions win on any form). find's `-H`/`-L`/`-follow` modes drop the link-only exemption for symlink roots (the tool traverses the link); a destructive find whose TRAVERSAL escapes through a symlink deeper inside a non-`.stage` root remains undetectable without walking the filesystem — same best-effort boundary as shell write detection. The remaining seam is a workspace that adversarially symlinks its own `.stage` root at a degenerate location (`.stage -> .`); the harness protects an honest actor from accidental/shortcut bypass, not a governance root the operator has deliberately sabotaged.

Governance settings are fail-closed: when `.stage/settings.json` exists but is unreadable or malformed, writes outside `.stage/` are denied until the file is repaired (repairing `.stage/settings.json` itself stays allowed).

`apply_patch` payloads are parsed for `*** Add/Update/Delete File:` and `*** Move to:` targets, so patch-body paths pass through the registration and promotion gates like any other write.

## Host contract

Both hosts consume the same `hooks/hooks.json` (Claude hook schema) and send Claude-compatible JSON on stdin (`tool_name`, `tool_input`, `cwd`, `hook_event_name`). Host differences the hook absorbs:

| Concern | Claude | Codex |
|---|---|---|
| File edits | `Write`/`Edit`/`MultiEdit` with `file_path` | `apply_patch` with `tool_input.command` = patch body |
| Other write tools (MCP, host-specific) | registered per project via `settings.json` `extra_write_tools` (§Limits) | same |
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
