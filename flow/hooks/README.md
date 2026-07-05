# hooks/

Quality-gate hooks for the flow plugin. They guarantee the same quality gate (the PreToolUse 12 rules) across two layers: **Claude Code plugin hooks** (`hooks.json`) +
**Agent Teams hooks**. The plugin hooks alone cover the 4 events
(PreToolUse / PostToolUse / SessionStart / Stop).

Premise: every flow work item (Initiative/Epic/Story/Action) lives under the standard `.flow/workspace/`
path, and runtime byproducts (audit logs / session summaries) accumulate under `.flow/.runtime/` (gitignored).

---

## 1. Configuration files

| File | Event | Role |
|------|--------|------|
| `hook_pre_tool_validate.py` | PreToolUse | 12-rule validation right before tool execution (deny/ask/allow) |
| `post_tool_validate.py` | PostToolUse | Audit logging after tool execution (`.flow/.runtime/hook_audit.jsonl`) |
| `inject_flow_context.py` | SessionStart | At session start, re-inject active Initiative/Epic/Story/Action state + the top-level one-line `**ultimate purpose**` (purpose-anchoring) + consolidate the previous session summary + on rule drift, provide preflight guidance before running `/flow-upgrade` |
| `session_relay.py` | Stop | Record a summary at session end (`.flow/.runtime/_session_summary.md`) → the next SessionStart picks it up |
| `rule_sync_cli.py` | (CLI — `/flow-upgrade`) | Sync the plugin `rules/` canonical source → the project `.claude/rules/` copies (detect/apply drift; also removes sync-registered historical `.claude/rule-details/` copies as orphans — unregistered files are treated as hand-authored and protected) |
| `quality_gate_cli.py` | (CLI — invoked at the verification stage) | **Quality-gate adapter** (TS-003): runs the declared checks in `.flow/settings.json`'s `commands` (test/lint/analyze/required_checks) via `subprocess` (shell=False) → records checks into `hook_audit.jsonl` (audit_report aggregation) → on required failure, performs a **minimal failure action** (non-zero exit, not a hook deny). No-op if undeclared. Invocation points = `flow-verify-commit` Step 1 / `flow-procedure-story` §7-1 verification |
| `audit_report.py` | (CLI — retrospective/measurement) | Aggregates `hook_audit.jsonl` (denied/asked rules · skills · retries · tools · verification checks) — evidence-based retrospective at the work-item level. `--pr N` posts the (optionally `--unit`-filtered) markdown report as a PR comment via `gh`; `--pr` + `--json` is rejected |
| `../scripts/append-log.py` | PreToolUse (`Skill` matcher) | Skill-usage telemetry: appends each Skill invocation to the active agent home's `skill-usage.jsonl` — `~/.claude` by default, `~/.codex` for Codex payloads (discriminated by the `turn_id` payload field). Best-effort — never blocks the tool call; opt-out via `skill_usage.enabled=false` in `.flow/settings.json` |
| `../scripts/report-usage.py` | PostToolUse (`Bash` matcher) | On `git push`/`gh pr create`, folds the personal skill-usage logs (`~/.claude` + `~/.codex`) into the monthly (`YYYYMM`) aggregation ticket comment via `gh`, then clears the logs on success (best-effort — a push is never blocked) |
| `_flow_state.py` | (shared module) | 4-tier traversal + `resolve_workspace_root` + rule sync (detect/apply) + `read_quality_commands` — shared SSOT across multiple hooks/CLIs |
| `hooks.json` | (registration) | Registers the above PreToolUse/PostToolUse/SessionStart/Stop hooks with the Claude Code plugin (CLIs are invoked by commands/procedures) |

---

## 2. PreToolUse 12 rules (quality gate)

`hook_pre_tool_validate.py` validates right before every tool execution. Path checks are
performed relative to `resolve_workspace_root` (`CLAUDE_PROJECT_DIR` first, else `cwd`),
so even if the repo clone location contains `/apps/` etc. it does not false-positive (shared SSOT across the 4 hooks).

### Tool name compatibility (Claude Code + VS Code Copilot)

VS Code Copilot sends different tool names than Claude Code. So the hook does not rely on the matcher and handles aliases directly in the body.

| Purpose | Claude Code | VS Code Copilot / Copilot Chat |
|---|---|---|
| File create/edit | `Write`, `Edit`, `MultiEdit`, `NotebookEdit` | `create_file`, `replace_string_in_file`, `multi_replace_string_in_file`, `edit_notebook_file`, `editFiles`, `edit_files`, `apply_patch` |
| Shell execution | `Bash` | `run_in_terminal` |

For `apply_patch`, the file path is not in `tool_input.filePath` but inside the patch string, so it parses the `*** Add/Update/Delete File:` blocks. When creating workspace nodes (`_epic.md`, `_story.md`, `A-NNN.md`) via `Add File`, it also enforces the `**ultimate purpose**` field.

| # | Rule | Check | Decision |
|:-:|----|------|------|
| 1 | `no-action-without-doc` | When an active Epic exists, editing `apps/`·`packages/`·`plugins/` requires an in-progress A-NNN.md to exist | deny |
| 2 | `no-commit-without-retro` | On `git commit`, whether the in-progress Action's retrospective section has substantive content (blocks placeholder / too-short retrospective / `--no-verify`) | deny |
| 3 | `no-push-workspace` | On `git push`, request confirmation of whether `.flow/workspace/` files are included | ask (Codex payloads: deny — Codex does not support `ask`, detected via its `turn_id` field) |
| 5 | `no-shared-branch-merge` | On merge/push to `develop`·`main`·`master`·`release/*`, verify the user's explicit keywords (`USER_MERGE_KEYWORDS`) in the transcript (shared-branch protection rule — CRITICAL) | deny |
| 6 | `no-story-without-action-doc` | When an active Story has 0 A-*.md, block edits to non-SSOT files (`skills`/`rules`/`apps`/`packages`/`plugins`/`lib`/`src`) | deny |
| 7 | `no-merge-without-review` | On Story-finish (all Actions ✅), enforce recording a deliverable review/evaluation in `_story.md` (the concrete review is delegated to project skills/agents) | deny |
| 8 | `no-work-without-playbook` | When editing code/SSOT in the execution stage (Action doc exists), enforce a `**playbook**` (work type) field in the active Epic's `_epic.md` (Φ4). The Planning window (0 Action docs) is exempt | deny |
| 9 | `no-node-without-purpose` | On new creation (Write/full replace) of a workspace node SSOT (`_initiative`/`_epic`/`_story`/`A-NNN.md`), enforce restating `**ultimate purpose**` — propagating the purpose-anchoring chain (a prerequisite for runtime derivation of purpose-anchoring). Epic-independent (including `_epic`/`_initiative` creation). Excludes Edit (partial edit) | deny |
| 10 | `no-shell-node-write` | Block creating/editing workspace nodes (`_initiative`/`_epic`/`_story`/`A-NNN.md`) via shell redirection (`>`/`>>`/`tee`) — prevents bypassing the node gate (best-effort, epic-independent) | deny |
| 11 | `no-finish-without-archive` | Right before PR creation (`gh pr create`)·shared-branch merge/push, block if a completed (✅) work item has not been migrated to `.flow/archives/retro-<name>.md` (epic-independent, global). Exempt at rigor=none level | deny |
| 12 | `no-action-without-depends-on` | On new creation of `A-NNN.md` (Write/full replace + apply_patch Add), block a missing `**depends_on**` field — a prerequisite for the D3 dependency graph (always, AT-independent). Excludes Edit | deny |
| 13 | `fan-out-attempt-mandatory` | With AT env on, when making the first code edit to an in-progress parallelizable Story (`A-NNN.md` ≥2 + `depends_on: []` ≥2), block if there is no spawn (Flow/Agent/Task) trace in the transcript. Passes for AT off / silent fallback / serial Story | deny |

> There is no rule number 4 (historically a gap). The actual 12 rules = 1·2·3·5·6·7·8·9·10·11·12·13.

Retrospective quality judgment: KPT (Keep/Problem/Try) markers + content of 5+ characters, or general text of
`MIN_RETRO_CHARS` (30) or more, excluding placeholders.

### AskUserQuestion question gate (conditional — separate from the 12 rules)

Where the 12 rules above are enforcement that denies content, the question gate is a **"pause once + 4-way reminder"**
mechanism. When an active Epic exists, right before an `AskUserQuestion` call:

- No preceding pause marker → **deny + 4-way (`FOUR_WAY_BRIEF`) reminder** (pause the question once)
- Re-called after re-review (marker present) → **allow + delete the marker**

Since deleting the marker on pass is the main mechanism, it pauses **once per question** (not once per session). The TTL (120s) is a
safety net so that a marker left neglected after a deny does not wrongly let the next question pass. The marker is
`.flow/.runtime/.askq_gate`. **The hook does not judge whether a question is bad** (it cannot judge meaning) —
it unconditionally pauses once to show the 4-way, and the AI then judges: drop the question if the answer can be derived from
the ultimate purpose, or re-ask (which passes) if it cannot be derived or a value judgment is required. The gate does not fire
during general work (no active Epic); plain-text questions are not tool calls so they are not caught — the SessionStart baseline covers those.

---

## 3. Agent Teams hooks mapping

When Agent Teams is enabled, the following team events act as **additional gates** on top of the PreToolUse 12 rules above.

| Agent Teams event | Mapped quality gate | Meaning |
|--------------------|---------------------|--------|
| `TaskCreated` | Action doc enforcement (`no-action-without-doc` / `no-story-without-action-doc`) | On Task creation, the corresponding A-NNN.md must precede it |
| `TaskCompleted` | Retrospective enforcement (`no-commit-without-retro`) | On Task completion, the retrospective section must have substantive content |
| `TeammateIdle` | Prevent autonomous stall | When a teammate becomes idle, keep autonomous progress to the next Action/Story |

---

## 4. Fallback relationship (core)

**This PreToolUse Python hook is itself the fallback.** Even if Agent Teams is disabled or the beta is
retired, the same 12-rule quality gate keeps working.

- When Agent Teams is **enabled**: `TaskCreated` / `TaskCompleted` / `TeammateIdle` act as additional gates.
- When Agent Teams is **disabled/retired**: this PreToolUse hook's 12 rules alone guarantee the same quality.

That is, regardless of the presence of team events, the flow quality floor does not break.

---

## 5. Installation / registration

`hooks.json` is auto-registered when the plugin loads. Registration structure (simplified — the actual `hooks.json` also sets per-hook `timeout`s and a tool-name `matcher` on the gate hooks):

```json
{
  "hooks": {
    "PreToolUse": [
      { "hooks": [{ "type": "command", "command": "uv run --no-project python \"${CLAUDE_PLUGIN_ROOT}/hooks/hook_pre_tool_validate.py\"" }] },
      { "matcher": "Skill", "hooks": [{ "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/append-log.py\"" }] }
    ],
    "PostToolUse": [
      { "hooks": [{ "type": "command", "command": "uv run --no-project python \"${CLAUDE_PLUGIN_ROOT}/hooks/post_tool_validate.py\"" }] },
      { "matcher": "Bash|run_in_terminal", "hooks": [{ "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/report-usage.py\"" }] }
    ],
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "uv run --no-project python \"${CLAUDE_PLUGIN_ROOT}/hooks/inject_flow_context.py\"" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "uv run --no-project python \"${CLAUDE_PLUGIN_ROOT}/hooks/session_relay.py\"" }] }
    ]
  }
}
```

- `${CLAUDE_PLUGIN_ROOT}` is substituted by Claude Code with the plugin root path.
- **Interpreter: `uv run --no-project python`** — first-class support on both macOS and Windows. Bare `python3` may be
  absent on standard Windows (python.org) (→ if the hook fails to launch, PreToolUse is **fail-open** so the
  tool proceeds as-is = the gate is neutralized), and bare `python` may be absent on some macOS. `uv` resolves
  Python regardless of OS (repo standard — same as `rag`, per the CLAUDE.md "invoke via `uv run`" rule). `--no-project`
  ignores the target project's `pyproject.toml` (the script uses only the standard library — no extra dependencies).
  The two telemetry hooks (`scripts/append-log.py` / `scripts/report-usage.py`) are pure-stdlib **best-effort** scripts and invoke bare `python3` directly — if `python3` is absent, only telemetry is skipped; no quality gate is weakened (unlike the gate hooks above, where fail-to-launch = fail-open).
- Every hook receives JSON input via stdin and outputs a JSON decision via stdout.
- PostToolUse/Stop are non-blocking (post hooks): they output only `{}` / `{"continue": true}` respectively.
