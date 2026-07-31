# Stage Hooks

This directory owns the hooks that apply Stage principles at execution time.

## Hooks

- `SessionStart`: injects the `.stage/` state and completion gates into the session context — current state, active work, review candidates, an inventory of host-project instructions (`CLAUDE.md`, `AGENTS.md`, `.claude/rules|skills`, …) with a use-and-challenge directive, the newest 3 open questions (`state/questions/`), planned records with `status: selected`, and the most recent session handoff — and prunes stale question-ack markers.
- `PreToolUse`: blocks `.stage` deletion, governed-file modification when no work is active, and official artifact modification without a promotion intent. It appends the selected active hierarchy's one-sentence purposes after every tool decision, with the leaf scope and any scope boundary crossed by the call. Matches every tool (`*`): names outside the built-in and settings-registered write sets remain ungated, but still receive purpose context.
- `PostToolUse`: completes two-phase intent reservations after the tool actually ran (never blocks).
- `Stop`: writes `.stage/.runtime/sessions/<session_id>.md`.

## Blocking criteria

- Deleting `.stage` entirely is forbidden — recursive `rm`/`rmdir`/`Remove-Item` and `find .stage -delete`/`-exec rm` are all blocked, including behind find's pre-path traversal options (`find -L .stage -delete`) and the `--` end-of-options separator. A recursive delete rooted at an ancestor of `.stage` (`rm -rf .`, `find . -delete`) is denied even when a find filter is present — the hook does not evaluate find expressions, so scope destructive sweeps below `.stage`'s branch (e.g. `find src -name '*.pyc' -delete`). Write targets are resolved through existing symlinks and `..` first, so an aliased path cannot dodge classification.
- `.stage/official/` modification is allowed only when a pending intent in `.stage/.runtime/intents/<work-item>.json` points at the target paths and a completed work item, and the target paths are declared in that item's `promotes` (or, for archive intents, match the item's own ID and `retrospective_ref`).
- Governed-file modification is denied only when no open work item exists in `work/current/`. A target outside the selected leaf's scope passes and is reported in the purpose context; scope is a signal, not an authorization boundary. Governance is broad by default — nearly all workspace files except `.stage/`, `.git/`, and `.discuss/` — and is adjusted per project via `.stage/settings.json` exclusions.
- Work item hierarchy is enforced at write time: unknown parents, self-parents, and opening a child under a finalized parent are denied.
- The question tool (`AskUserQuestion` on Claude, `request_user_input` on Codex) gets a once-per-question reminder to derive the answer from the work purpose and canon principles first; re-asking passes.
- Every tool call gets non-blocking purpose context when active work exists. Scope and boundary-crossing lines come first; then the live theme, milestone, epic, story, and action purpose first sentences follow in hierarchy order, leaving the current action purpose last. A denied call keeps its original reason and appends the same purpose context.
- Intermediate commits are allowed. For staged files, same-command `git add` targets, `git commit
  -a` changes, and commit pathspecs, the commit gate requires at least one open work item and still
  blocks a target owned by a completed item whose verification, retrospective, or promotion is
  unfinished. An open item's scope is not commit authorization: an outside-scope target passes and
  is reported in the purpose context.
- OS-specific executable scripts are not allowed inside `.stage`.

## Runtime concurrency

`.stage/.runtime/` is multi-session by construction — several Claude/Codex sessions can share one `.stage` without clobbering each other:

- `intents/<work-item>--<basename>-<digest>.json` — one pending intent per (work item, entry-canonical workspace-relative path), so consuming an authorization is an atomic **rename reservation** (`intent.json` → `intent.json.claim-<id>`): the session that wins the rename proceeds, a concurrent session whose rename fails is denied rather than riding the same one-shot authorization (the claim is HELD through tool execution: PostToolUse completes it, and a claim whose post never arrives — crash, rejected permission — is restored to a pending intent after ten minutes rather than burning the authorization). No shared-file rewrite, hence no lost-update race. The filename embeds the target basename plus a 10-hex digest of the full path (bounded length, deterministic replant). The promotion gate requires every targeted path to be covered by exactly one pending intent — zero coverage or more than one candidate per path denies (fail closed on ambiguity) — and validates all involved intents before reserving any. Legacy single-slot and multi-path intent files are split into this layout on first read (originals kept unless every replacement persisted); `session-summary.md` migrates to `sessions/legacy.md` (or a numbered slot if that is taken, never dropping a handoff).
- `sessions/<session_id>.md` — one Stop handoff per session; SessionStart injects the most recent handoff, plus any others sharing its mtime (two sessions can Stop in the same coarse-resolution tick), and Stop prunes to the newest 5. The just-written summary is pinned, and files younger than a day are never pruned (under cross-host clock skew the cap is soft for at most a day rather than losing a live session's handoff).
- `question-ack/<session_id>` — the question-gate reminder marker is per session; SessionStart removes markers older than a day (abandoned sessions).

The session dimension comes from the `session_id` field both hosts send in hook stdin; a payload without it falls back to a shared `default` slot.

## Limits

Shell write detection is best-effort. The default detection targets are output redirects, `cp`/`mv` destinations, `tee` targets, and `sed -i` files, plus file-delete operands of `rm`/`del`/`erase`/`Remove-Item`/`ri` — deleting a governed file is a governed modification. Both write and delete operands are anchored at the tracked effective cwd (a preceding `cd` rebases them; any possible anchor may deny, fail closed), redirect targets are extracted from the token stream (a quoted `>` inside a word is data, not a redirect; fd duplications like `2>&1` are not file writes), and `--` ends option parsing. Unexpanded globs and variables pass through as literals, and `rmdir` (empty directories only) is not extracted — best-effort. File writes inside inline interpreters are outside the detection range.

The delete gate tokenizes the whole command with shell control operators (`;`, `&`, `&&`, `|`, `||`, unquoted newlines) as their own tokens — quoting is honored, line continuations are spliced, heredoc bodies are dropped, and a find `-exec … \;` terminator stays inside its find group. It tracks the effective cwd across `cd`/`pushd`/`popd`/`cd -` (with a directory stack and OLDPWD) as a SET of possible directories — a conditionally executed, backgrounded, or pipeline-fed cd unions its state with the prior one, a failed cd (missing directory, multi-operand error, unknown option) keeps the caller's cwd, and the gate denies if ANY possible cwd would remove the Stage tree (fail closed). This models an honest actor's shell, not an adversary: cwd changes inside `eval`, command substitution, `env -C`, or an explicit subshell `(cd x; …)` are not evaluated, and a governance root the operator deliberately sabotages is out of scope (see the closing paragraph).

Coverage is deliberately scoped to what an honest actor would plausibly type. Detection resolves the common shell forms above; a set of rarely-hand-typed constructs is left as documented best-effort rather than chased into a full shell-parser reimplementation: `cd -P` physical mode (only logical `cd -L` is modelled), indexed directory-stack ops with a non-zero index (`pushd +N`/`popd +N`), and find whose traversal mode or destructive action is spelled through another predicate's operand (`find … -name -P …`, a file literally named `-delete`). These do not arise from an accidental or shortcut `.stage` deletion, which is the harness's protection target. (External-process wrappers that cannot run the `cd` builtin — `nohup`, `nice`, `time` — are not peeled, so their apparent `cd` is a no-op and a following relative delete stays anchored at the caller, which is the correct fail-closed behavior.)

Write-target extraction reads `path`/`file`-keyed input fields plus `apply_patch` file headers. A hypothetical host alias that carries its write target under a different key (e.g. `target`, `uri`) would pass the gates unexamined — no documented Claude/Codex tool does this.

Gating is keyed on tool NAMES: a file-writing tool whose name is outside the built-in allowlist — typically an MCP server tool such as `mcp__filesystem__write_file` — bypasses every gate, silently. Projects that use such tools register the exact names in `.stage/settings.json` `extra_write_tools`; registered names are classified as write tools before the unknown-name early allow, so the registration, promotion, hierarchy, and governance gates apply (targets are matched entry-canonically, like `apply_patch`). Shape-based auto-detection (any payload with path+content) was considered and rejected: it would deny non-file tools that happen to carry those fields. When `settings.json` is unreadable, the registered names cannot be read back — those tools fall back to this ungated default until the file is repaired, while built-in tools stay behind the governance fail-closed deny.

A pending intent is a path-scoped capability: once planted, any session may perform the matching `official` write, and the hook cannot attribute the write to a specific work item (hook stdin carries no work-item context). This is unchanged from the single-slot design; the binding (completed item + declared `promotes`/archive filename) plus the ambiguity deny above are the enforced surface.

An archive intent may authorize the shared `official/work/archive/index.md` alongside the item and retrospective moves. Like every intent-authorized official write, the authorization is path-scoped, not content-scoped — a write that damages other rows is not prevented at the gate; the audit detects it afterwards (every archived item without its index row is an ARCHIVE001 error).

Intent consumption is two-phase. The promotion gate validates last (a call denied by the registration, hierarchy, governance, or commit gate never burns the authorization) and reserves by renaming the intent to a claim; the claim is held through tool execution, and PostToolUse — measured as delivered on both hosts, with the tool's response attached — completes it. A claim whose post never arrives (tool crash, rejected permission prompt, a host or an unregistered extra tool that fires no post) is restored to a pending intent after ten minutes by any later hook evaluation, so a failed run recovers on retry without re-planting; re-issuing early is still one command — `scripts/promote_intent.py --work-item <id> --path <path>`. Restore never duplicates an authorization: a re-planted intent under the original name wins and the stale claim is dropped.

Write targets are classified by the union of three forms — resolved-canonical (symlink parents + `..`, leaf included), entry-canonical (parents resolved, leaf kept as named), and lexical — so a symlink or `..` cannot re-enter `.stage` unseen, a symlink whose leaf sits in `.stage/official` still hits the promotion gate, and a governed symlink *entry* (`src/link`) whose target is outside stays registration-gated when it is unlinked or replaced. The resolved (leaf-dereferenced) form participates only in fail-closed directions — detection and governance INCLUSION — never in authorization or exemption: exact-entry authorizations (a work item's `promotes`, pending intents, archive filenames) and scope matching compare the entry-canonical form, so a grant or scope for one leaf never covers a sibling symlink aliasing the same target, and configured governance exclusions win on the entry/lexical forms only (structural `.stage`/`.git`/`.discuss` exclusions win on any form). find's `-H`/`-L`/`-follow` modes drop the link-only exemption for symlink roots (the tool traverses the link); a destructive find whose TRAVERSAL escapes through a symlink deeper inside a non-`.stage` root remains undetectable without walking the filesystem — same best-effort boundary as shell write detection. The remaining seam is a workspace that adversarially symlinks its own `.stage` root at a degenerate location (`.stage -> .`); the harness protects an honest actor from accidental/shortcut bypass, not a governance root the operator has deliberately sabotaged.

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
| PostToolUse | delivered after the tool ran (completes two-phase intent claims) | same — measured on 0.144.0 (`tool_response`, `tool_use_id` included) |
| Workspace root | `CLAUDE_PROJECT_DIR` env | no env var — hook cwd and payload `cwd` are the workspace |
| Allow output | exit 0 with empty stdout or a bare `systemMessage` = no opinion — the call falls through to the host's normal permission flow (an explicit `allow` would bypass permission prompts entirely) | same (an explicit `permissionDecision: "allow"` is additionally rejected as unsupported output) |
| Deny output | `hookSpecificOutput.permissionDecision: "deny"` + reason | same |
| Stop output | `systemMessage` only | same (`decision` is accepted only as the literal `"block"`) |

### Codex hook trust

Codex executes plugin hooks only after they are trusted once in the interactive TUI (`/hooks`); trust persists as `[hooks.state.*] trusted_hash` entries in `~/.codex/config.toml`. Until then hooks are discovered but silently excluded — including in `codex exec` — so Stage enforcement on Codex requires the one-time trust approval after `codex plugin add stage`.

## Portability

The hook body uses only the Python standard library. `hooks.json` runs `python3` directly, so the hook and its tests must run on whatever `python3` the host machine provides — annotations stay lazy via `from __future__ import annotations` (verified on system Python 3.9.6). Windows environments without a `python3` command need the Python launcher or a host adapter.
