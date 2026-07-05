# Directory standard + distinction of the 2 rule kinds

The directory standard the flow plugin uses once installed in a project, plus the scope distinction of the 2 rule kinds.

## `.flow/` directory standard

The project root `.flow/` is the single location for flow assets:

| Path | Purpose |
|------|---------|
| `settings.json` | Project flow settings (active playbooks / team composition). The orchestrator Reads it. |
| `workspace/` | **In-progress** work items (`epic-*/{US,TS}-NNN-*/A-*.md` SSOT — Story dirs use both `US-NNN-*` and `TS-NNN-*`, per `ssot-vocabulary`). Status (⬜/🔄/✅) source is only `_epic.md`/`_story.md`/`A-NNN.md` here (`ssot-write-only`). Hooks (quality gates) scan it and enforce Action-doc/retrospective existence. |
| `archives/` | **Per-completed-unit retrospectives** — one flat `retro-{unit-name}.md` per entry scale (unit = top level that started the work: Initiative/Epic/Story), no folders, **git-tracked**. `## Retrospective` extracted + source meta; work content stays in the repo/PR (`flow-archive`). Unreflected-retrospective queue: after `retro-processing` reflects it into main, delete the file. |
| `playbooks/` | Project-custom playbooks overriding the plugin built-ins (optional — falls back to built-in if absent). |

Core: **`workspace` (in progress) / `archives` (completed)**. Claude Code does not auto-inject `.flow/` — the orchestrator does an explicit Read (especially the `playbooks/` override).

> Teammate (specialist) definitions live in the standard `.claude/agents/`, not under `.flow/` — the tool discovers them natively; there is no settings index for them.

### git track/ignore (SSOT)

| Path | git | Reason |
|------|-----|--------|
| `.flow/settings.json` | tracked | team-shared settings |
| `.flow/archives/` | tracked | unreflected-retrospective queue (shared) |
| `.flow/playbooks/` | tracked | shared custom playbooks |
| `.flow/workspace/` | ignored | in-progress — volatile, per-clone local |
| `.flow/.runtime/` | ignored | audit log (`hook_audit.jsonl`) · session summaries · rule-sync state |
| flow propagation rules in `.claude/rules/` | ignored (generated) | DO-NOT-EDIT copies of the plugin canonical. Sync (`/flow-upgrade`) registers them in `.gitignore` **per file** (never whole-folder — protects hand-authored rules), overrides them with the canonical (even if hand-edited), deletes them when gone from the canonical. |
| consumer hand-authored rules there | tracked | outside `.gitignore`; sync never touches them |

- `flow-config` writes the static ignore paths (`workspace/`·`.runtime/`) into `.gitignore` (skip + guide if not a git repo); per-file registration of propagation rules is done by sync at propagation time. Declared-but-unregistered ignore = ground-truth bug (volatile files committed / propagation rules tracked).
- Propagation rules are git-ignored, so they are absent right after clone — activate with `/flow-upgrade` in the first session (rule-missing detection guides this).

## Distinction of the 2 rule kinds (scope — conflicts when confused)

| Kind | Applies | Location |
|------|---------|----------|
| **Flow rule** (no-action-without-doc / gate-enforcement-default-on, etc.) | **Always** (common to all work) | `.claude/rules/` (auto-loaded) + hooks |
| **playbook** (feature / bug / refactor, etc. work types) | **One selected per work item** | Applies only to that work item once selected |

Core: **flow rule = always loaded / playbook = one selected per work item — registering a playbook as a rule is forbidden** (rules are always loaded; two playbooks-as-rules apply two ways of working at once and conflict). Flow rules are always-on procedural guardrails; a playbook is the rulebook for one work item.

### Playbook selection flow (Plan Mode)

1. Read `.flow/settings.json` → active `playbooks[]`.
2. Pick 1 by the work item's nature — no fixed default; if nothing fits, fall back to `general`.
3. Use the project override `.flow/playbooks/{playbook}.md` if present, else the plugin built-in.
4. Load it into context — applies only to that work item's Action flow.
5. Record the choice in `_epic.md` `**playbook**` (an Epic is temporary, so not in settings).

## Related rules

- `ssot-write-only` — work-item status source (`.flow/workspace/` SSOT)
- `gate-enforcement-default-on` — flow-rule default enforcement
