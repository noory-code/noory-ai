---
name: plugin-dev
description: Plugin self-development work type — rule/skill/hook/command changes + regression obligation + propagation obligation (rule sync + version bump) + dogfood. A single meta-work flow (no methodology variant).
---

# plugin-dev (plugin self-development)

The meta work type for changing this plugin's own — or a sibling plugin's — assets (rules / skills / hooks / commands / playbooks / docs). By the nature of meta work, its essence is a **regression safety net + a propagation mechanism**, and it differs from an ordinary code work type (feature/bug/refactor, etc.) in two ways:

1. **Full-regression obligation** — when adding a new hook rule, enforce the *entire* regression suite (all hook tests), not just the new case. This blocks the accident of existing regressions going stale via prevention rather than recovery (epic-wf-fanout-enforce TS-002 retrospective, High Try).
2. **Propagation obligation** — the work is complete only when the changed asset actually propagates to every installed location. A text change alone does not finish it (rule sync + plugin version bump).

## Scope

- Changes to the plugin's own rules (`rules/*.md`) / skills (`skills/*/SKILL.md`) / hooks (`hooks/*.py`) / commands (`commands/*.md`) / playbooks (`playbooks/*.md`) / docs (`docs/*.md`)
- Changes to the same assets in a sibling plugin (e.g. rag, flutter-cask, etc.)
- Out of scope: a single-project code change (→ `feature` / `bug` / `refactor`) / evaluating an external library (→ `research`)

## Procedure

Plugin self-work is a **single flow — no methodology variant** (by the nature of meta work, flow branching is meaningless). 5 stages + a Hard Gate at each stage.

1. **Design** — classify the changed assets (rules / hooks / skills / docs / commands / playbooks) + impact scope + expected regression impact. Output: a changed-asset table (asset type + file + propagation path)
2. **Change** — implement and add via the Edit / Write tools. Output: the changed assets
3. **🚨 Regression (Hard Gate)** — **when adding a new hook rule, enforce the entire regression suite, not just the new case** (epic-wf-fanout-enforce TS-002 retrospective, High Try). Output: `cd <plugin>/hooks && python3 -m unittest discover -s tests` passes in full (both the pre-Epic baseline and the new case). If it does not pass, go back to the Change stage (no commit)
4. **🚨 Propagation (Hard Gate)** — trigger the appropriate propagation path so the changed asset reaches every installed location:
   - **rule change** (`rules/*.md`) → run `/flow-upgrade` (or `uv run --no-project python <plugin>/hooks/rule_sync_cli.py apply`) → sync to `.claude/rules/`
   - **hook / skill / command / docs / playbook change** → plugin version bump (update the 5 standard locations from the CLAUDE.md "Versioning & Release" table simultaneously — `plugin.json` + `marketplace.json` + `CHANGELOG.md` + (if present) `server/pyproject.toml` + `__init__.py` + (if a skill frontmatter has `plugin_version`) update only the modified skills)
   - Output: drift detect → 0 stale + a grep match on the 3+ files whose plugin version was updated
5. **dogfood** — for a rule change, confirm after sync that the SessionStart hook notice disappears (that drift is 0). Output: detect JSON matches `stale: []`

> Meta work is a single flow — the methodology variants of feature/refactor (BDD / prototype / spec-first, etc.) are meaningless here. Change → Regression → Propagation → dogfood is the essence of meta work.

## AC format

Specify each change's **behavior preservation (regression)** + **propagation completion** in 5 fields.

- **Given** — the pre-change state (current number of hook rules N / current plugin version / current rule-sync state)
- **When** — the change (adding a rule / modifying an asset, etc.)
- **Then** — after the change: (1) the existing regression of N + the new case passes (2) the propagation path is triggered (rule sync or version bump)
- **Verification method** — a measurable command: `unittest discover` / `rule_sync_cli.py detect` / `grep "<version>"`, etc.
- **Pass/fail criteria** — regression 100% pass + a propagation-trigger trace (drift 0 or version match) → PASS / any single failure / residual drift → FAIL

> No unmeasurable AC of the "works fine / looks okay" kind (consistent with ssot-vocabulary).

## Hard Gate (pre-/post-change verification obligation)

This playbook has stronger gates than an ordinary work type — a meta asset affects every installed location if it breaks:

| Gate | When | Pass condition | On violation |
|--------|------|----------|--------|
| **Full-regression obligation** | when adding a hook rule (or changing hook code) | `unittest discover` passes in full (new + existing) | No commit. If even one existing regression is found stale, fix it immediately + record it as a retrospective Problem |
| **Rule-sync obligation** | when modifying `rules/*.md` | `rule_sync_cli.py detect` → 0 stale | No PR. If the rule change is not reflected in `.claude/rules/`, it does not propagate to any installed location |
| **Version-bump obligation** | when changing a plugin asset (hook/skill/cmd/docs/playbook) | `plugin.json` + `marketplace.json` + `CHANGELOG.md` versions consistent | No PR. Without a version bump, the user's plugin-upgrade trigger does not fire = no propagation |

## Feedback-loop locations

- **Right after 3, regression passes** — record the pass result (test count + new/existing ratio) in this Action's body
- **Right after 4, propagation triggered** — record the drift-0 + version-consistency result in this Action's body
- **Right after 5, dogfood** — confirm that the rule-change path's SessionStart notice disappears in the next session (manual, or automatically in the next session)

## Review & evaluation (the essence of meta work)

The review dimensions differ from ordinary work — for a meta asset, inspect these essential defects:

| Inspection item | Meaning |
|-----------|------|
| **Contract violation** | Is the rule's/skill's specification (deny message · gate-trigger condition) consistent? |
| **Layer trespass** | Does the hook body avoid changing external assets (verify only) / does the SKILL body avoid bypassing hook enforcement? |
| **Missing boundary** | Does it avoid dropping an edge-case branch (env off / external environment / fallback)? |
| **Regression safety net** | Do the existing regressions avoid going stale (full-regression obligation)? |
| **OS compatibility** | Works on both macOS + Windows (pathlib + os.environ / 0 POSIX-only dependencies) |

## Non-goals (excluded)

- A single-project code change (→ `feature` / `bug` / `refactor`)
- Evaluating an external library (→ `research`)
- Analyzing user data (→ `research`)

## origin

This playbook was newly created by integrating the meta-work experience of Initiative `epic-wf-fanout-enforce` (2026-06-09 ~ 2026-06-10) + the TS-002 / TS-003 retrospective Tries:
- TS-002 retrospective High Try: "enforce the entire regression suite when adding a new hook rule" → §3 Hard Gate
- TS-003 retrospective Mid Try: "AC markers for external assets" → AC format (measurable command) + explicit non-goals
