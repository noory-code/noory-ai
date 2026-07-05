# /flow-config detailed procedure

Stage 3 reference for `commands/flow-config.md`. The command file stays as the explicit-invocation entrypoint, and this file is kept as the SSOT for the detailed onboarding procedure.

## Purpose

Configure the flow plugin to fit the project. It is not a form-filling wizard but an onboarding where the AI does ground-truth inspection of the project and, through conversation with a person, finalizes the playbook and settings injections. (`agents[]` is NOT a conversation topic — it is scan-filled silently from `.claude/agents/`; do not ask the user about team composition or agents.)

## Core principles

- Conversation-centric: not forms/auto-scan, but drawn out through conversation after ground-truth inspection.
- AI proactively fills in: the AI builds recommendations so a person does not need to know the terminology.
- Don't Make Me Think: rather than listing candidates, present a single recommendation grounded in ground-truth inspection plus one alternative.
- Clear Feedback: clearly report what was understood and what will be injected.
- Purpose anchoring: before asking the user, first check whether the answer is derivable from the project ground-truth inspection plus the purpose.

## Phase 1: Understand the project in depth

| Inspection target | What it tells us |
|-----------|---------------|
| Existing skills `.claude/skills/` | Ways of working the project already has |
| Rules/guidelines `.claude/rules/`, `CLAUDE.md` | Rules to follow + hints about ways of working |
| Installed plugins/marketplace | Conflict/coexistence targets |
| Code stack/directory structure | Basis for inferring playbooks |

After inspection, map playbooks to the `playbooks.json` catalog or a project override. If unsure, narrow to two candidates and present them, but do not offload the choice of task type onto the user.

## Phase 2: Four project-state quadrants

| State | What to handle |
|------|-----------|
| Empty project | Inject playbook/settings from scratch |
| Has its own skills | Set the flow relationship with existing skills (coexist/leverage/override) |
| Multiple plugins installed | Check command/rule conflicts and coexistence |
| Own skills + plugins | Apply the two above in sequence, then present an integrated cleanup plan |

Every case keeps the AI recommendation → user confirmation flow.

## Phase 3: Finalize playbook and inject settings

- If a bundled playbook fits, activate it in settings.
- If it does not fit, create a `.flow/playbooks/{method}.md` override.
- The override follows the 7 elements of `meta-playbook-procedure` (frontmatter / procedure / AC format / Hard Gate / feedback loop / violation handling / review-and-evaluation points).
- Wire up not only per-layer skills but also cross-cutting skills like structure/location/naming, quality/verification, and refactoring.

## Phase 4: config-only RT gate

Before injecting settings, adversarially review the playbook mapping and override draft.

- Target: playbook mapping, settings draft, override structure
- Strength: architecture/meta — strong
- Iterations: up to 3 rounds, terminate when High issues reach 0
- On non-convergence, report the residual issues and choices to the user.

## Phase 5: Generate settings.json

Example:

```json
{
  "playbooks": ["feature", "bug"],
  "agents": [],
  "commands": {
    "test": ["uv", "run", "pytest"],
    "required_checks": ["test"]
  },
  "upstream_board": {
    "type": "github-project",
    "owner": "<org-or-user>",
    "number": 0,
    "url": "https://github.com/orgs/<org>/projects/<n>"
  },
  "skill_usage": { "enabled": true }
}
```

- `playbooks[]`: list of active playbooks. There is no fixed default.
- `agents`: list of specialist teammates the project supplies. **Definition SSOT = `.claude/agents/`** (one `.md` per teammate); `settings.json` `agents[]` is an index derived from there.
  - **Scan-fill**: Glob `.claude/agents/*.md` → extract each file's frontmatter `name` (or the filename stem if absent) as the teammate name → fill `agents[]`.
  - **Non-destructive / idempotent (union)**: preserve existing `agents[]` entries and team customizations. Merge the scan result with existing values as a union but drop duplicates — do not overwrite existing values. Re-running must produce the same result.
  - If `.claude/agents/` is missing or empty, leave `agents: []`. **Never ask the user** to define or pick teammates here — role templates are optional; a project without them works fully (dynamic teams / parallel subagents need no pre-registered roster). At most, report the scan result in one line.
- `commands`: quality-gate adapter input. No-op if absent.
- `upstream_board`: board binding for publishing/processing the retrospective backlog (plugin-core/upstream items) as tickets. **Default = the internal default board baked into the plugin (`upstream_board` in `config-defaults.json`)** — because this is an internal-only tool (private↔private install), baking board coordinates has no security impact. On config, put this default straight into settings; a project using a different board can just change the value. The publish/process skills read board coordinates **only from this settings field** (`retro-processing` backlog routing SSOT). The per-`type` coordinate fields are defined by the publish skill (e.g., `github-project` uses `owner`+`number`). Publishing/querying a GitHub Project requires the `project` scope on the `gh` token — without it, hold the publish + guide.
  - **config default fill**: if settings has no `upstream_board`, present/inject the value from `${CLAUDE_PLUGIN_ROOT}/config-defaults.json` as the default (user can override). If it already exists, preserve the user value.
- `skill_usage`: turn skill-usage stats collection on/off. **Default = on** (`config-defaults.json`). On config, put this item into settings **explicitly** so the user can see it is "collecting" and turn it off — even without the item the default is on, but then it is invisible in the settings file and the user would not think to turn it off, so we state it explicitly for discoverability. To turn it off, `"enabled": false`. The recording hook reads this value and skips only on `false`. (Same seed path as `upstream_board` — inject the default if absent, preserve the user value if present.)
- Preserve existing values and patch only the changed parts.

## Phase 6: Directory and gitignore

`.flow/` standard:

```text
.flow/settings.json   # tracked
.flow/workspace/      # gitignore
.flow/archives/       # tracked
.flow/playbooks/      # tracked
.flow/.runtime/       # gitignore
```

If it is a git repo, idempotently add the following to `.gitignore`.

```gitignore
.flow/.runtime/
.flow/workspace/
```

## Phase 7: Rule sync and restart guidance

1. Sync plugin rules to `.claude/rules` via `/flow-upgrade` or the same helper.
2. Guide which assets need a session restart.
3. In the FINAL report only, include one optional line: parallel execution is richest with the Agent Teams env on Claude Code (`README.md` §env setup) — do not turn this into a question or a setup conversation.

## Phase 8: Installation verification, 4 axes

| Axis | Verification |
|----|------|
| Active playbook | RT runs + 7 elements confirmed |
| Rule freshness | 0 stale/missing/orphan per `/flow-upgrade detect` |
| settings | Active playbook exists in `.flow/settings.json` |
| Retrospective policy | `retrospective.levels` values are valid and initiative is not `none` |

## Phase 9: Rebalancing

If settings already exist, do not fully rewrite; update only the changed parts. Check the diff of new stack/skills/plugins, and if there is no change, terminate with "nothing to update."
