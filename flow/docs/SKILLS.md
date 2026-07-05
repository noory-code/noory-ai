# flow skill behavior reference

> Documents the **actual behavior** of each of the 32 skills. Each entry is in the order **trigger point / what it does / input-output / core mechanism**. For the full picture see [ARCHITECTURE](ARCHITECTURE.md); for usage see [USAGE](USAGE.md).
>
> Notation: `user-invocable` = the user can call it directly. The rest are internal assets that the orchestrator (`flow`) `Read`s per Phase.

---

## 1. Orchestrators (3)

### flow `user-invocable`
- **Trigger**: "make an epic/story/action", "next/proceed/continue", "retrospective/commit", or when `.flow/workspace/epic-*` exists.
- **What it does**: the team-lead engine. Classifies the trigger into a Mode (Mode Detection table) → determines the current Phase via Auto Mode Logic → `Read`s that Phase's `flow-*` asset → performs the procedure → stops at a user checkpoint.
- **Input-output**: reads = `_epic.md`/`_story.md`/`A-NNN.md` state / writes = updates task SSOT state. Completed (✅) Actions skip loading to save context, only in-progress (🔄) ones are fully loaded.
- **Core**: fixed flow of "judge state → load asset → procedure → completion handling". No guessing — the detailed procedure must be performed after loading the asset. Enforces plan approval (user confirmation) at 9 User Checkpoints.

### flow-pr `user-invocable`
- **Trigger**: "make a PR", "create a pull request", or when a shared-branch merge is needed after work completion.
- **What it does**: create the `pr/{name}` branch → remove excluded targets (workspace SSOT · session files) → analyze the commit history and classify by type → generate a 3-section PR body file (Summary/Changes/Testing) → push → create the PR with a `[TYPE]`-prefixed title and `--body-file` → delete the temporary body file.
- **Input-output**: reads = current branch · commit history · project PR template / writes = `pr-body-*.md` (temporary), git push, PR URL.
- **Core**: no automatic assumption of the base branch (user-specified > task SSOT base > project shared branch). Excluded-file deletion only when the current branch is `pr/` (protect the original).

### flow-verify-commit `user-invocable`
- **Trigger**: right after Action implementation is complete (before commit). The core of the `action-finish` Phase.
- **What it does**: ① static analysis (supplied by the playbook) → ② AC-based test execution (if the "verification method" in the A-NNN.md AC table is test, execution is mandatory = Hard Gate) → ③ **R2 RT independent review default-on** (persona + 4 essence attacks + 2 consecutive passes — **zero runs forbidden**; if an independent agent is impossible, self-review with the same payload is also mandatory) → ④ atomic commit (`[epic][story][action]` format, confirm artifacts staged) → ⑤ state ⬜→✅ + immediately update Step checkboxes → ⑥ retrospective (KPT) + R3 attack (block 5 placeholder patterns).
- **Input-output**: reads = A-NNN.md (AC table · state) · git diff · previous Story retrospective / writes = commit, `_story.md` sync, A-NNN.md checkboxes · retrospective.
- **Core**: AC "test keyword" = Hard Gate (commit blocked if tests are missing). The retrospective is an assessment of AI behavior, not a work summary. Step updates are immediate (not batched) → traceable if lost.

---

## 2. Planning (6) — trigger → scale → playbook → Epic → Story → Action

### flow-trigger-classify
- **Trigger**: the first action when an external source (issue-tracker ticket / messenger thread / natural language) enters the flow.
- **What it does**: identify the source (structured = signal / semi- or unstructured = inference) → classify the work type (structured maps the type field / unstructured infers from keywords, and confirms with the user if ambiguous) → extract scale hints (story point · epic link · issue type) → route to playbook-selection + scale-judgment.
- **Input-output**: reads = external source content / output = work-type hint + scale hint.
- **Core**: structured signal = definitive, unstructured = inference + user-confirmation gate. Non-matches fall back to `general` (no forced specific playbook). It only classifies; the actual confirmation is delegated to the sub-procedures.

### flow-scale-judgment
- **Trigger**: the Discovery stage of Epic/Story planning — judging work scale (batch/Story/Epic/Initiative).
- **What it does**: ① **ultimate-purpose interview (prerequisite)** — before the 7-stage assessment, first ask "why / higher value" to plant the purpose in the top-level node `**ultimate purpose**` → ② 7-stage serial assessment (duration/number of subtasks/domain scope/dependencies/artifact impact/uncertainty/external conditions) → ③ borderline cases (4 days · 2 Stories · 5–10 artifacts) forbid automatic decision, require user confirmation accompanied by a recommendation.
- **Input-output**: reads = purpose statement · expected duration · scope · requirement clarity / output = scale judgment + 7-stage rationale + (when borderline) user confirmation.
- **Core**: the purpose interview precedes the judgment (breadth of purpose = a scale signal). Full 7-stage assessment. Initiative trigger = 2+ Epics + a shared value proposition (not size alone).

### flow-playbook-selection
- **Trigger**: entering Plan Mode (writing Epic/Story) — selecting, among the active playbooks in settings, the one matching the work type.
- **What it does**: explicit Read of `.flow/settings.json` → extract `playbooks[]` → match the work type to the playbook's applicability (non-match = `general` fallback) → confirm with a single recommendation + rationale + 1 alternative → record it in the `_epic.md` `**playbook**` field → when loading the playbook body, the `.flow/playbooks/{name}.md` override takes precedence.
- **Input-output**: reads = settings active playbooks · work type · override path / writes = `_epic.md` `**playbook**` field.
- **Core**: no fixed `default` (selected each time per work type). Explicit settings Read (no auto-loading). A project override takes precedence on a name conflict.

### flow-planning-epic
- **Trigger**: entering the Epic planning Phase.
- **What it does**: 7-stage cycle — Discovery (analyze workspace · code structure · domain boundaries + built-in scale-judgment + AC pre-fulfillment grep) → Assumption Gate (3–5 bullet user confirmation) → Alignment (5 required questions + 3 situational) → Draft (`epic-[name]/` folder + `_epic.md`·`_story.md` with `[DRAFT]` marker) → R1 (AI self-review before the user sees it: persona + 4-minute attack) → Refinement (up to 3 times) → Structure Validation (Hard Gate, block flat-file contamination) → Finalize (remove DRAFT after approval + commit).
- **Input-output**: reads = codebase · existing DRAFT · playbook · persona / writes = `_epic.md`+`_story.md` (DRAFT), commit after approval.
- **Core**: Discovery is done by the main alone, with no teammate assignment. R1 is a quality gate before user exposure. The DRAFT marker is removed only on user approval.

### flow-planning-story
- **Trigger**: entering the Story planning Phase (within Plan Mode).
- **What it does**: Pre-flight 4 axes (directory/persona/branch/Asset) → Discovery (Step 0 auto-load the immediately-preceding Story retrospective → classify·apply Try / Step 0.5 measure the Epic AC baseline = Hard Gate / Steps 1–9 code·structure exploration) → Assumption Gate → Alignment (3 required questions + 2) → Draft (Action decomposition table + delegate_to column + delegation strategy, applying Action decomposition rules · TDD pairing) → R1 → Refinement (up to 2 times) → Finalize (story-setup: branch + Action file creation).
- **Input-output**: reads = previous Story retrospective · Epic AC baseline · codebase · teammate guide / writes = `_story.md` (DRAFT) + Action files.
- **Core**: Step 0 auto-loads the retrospective (block recurring defects). Step 0.5 measures the baseline (catch scope mismatch before decomposition). Emphasis on the persona axis (contamination undermines downstream reviews).

### flow-planning-action
- **Trigger**: confirming the Action approach within Story Plan Mode (a lightweight cycle after decomposition).
- **What it does**: Pre-flight 4 axes (Asset axis = **mandatory Read of the teammate guide**) → Discovery (Why/When first — before implementation, confirm business rules (save/delete/query/validation/state-transition conditions) → analyze the baseline file → check existing patterns · naming rules → Grep the impact scope (Hard Gate) → minimal-change principle → predict cascading changes) → Alignment (resolve delegate_to · integration judgment first, then 1 required question + 1) → R1 (conditional self-review — 5-case matrix) → Finalize.
- **Input-output**: reads = A-NNN.md · codebase · teammate guide · project agents / writes = A-NNN.md approach · delegate_to · assignment signal.
- **Core**: "when/why" (business rules) before "how". delegate_to is resolved before asking the user. Start from minimal change (don't assume the full scope).

---

## 3. Procedures (4) — per-level creation/execution

### flow-procedure-initiative
- **Trigger**: `initiative-setup` / `initiative-finish` — the top-level unit that bundles multiple Epics.
- **What it does**: create `initiative-[name]/_initiative.md` (SSOT) — value proposition + Philosophy (Φ) + Epic dependency graph + completion criteria. Enforce the 4 layers (Initiative→Epic→Story→Action). Wrap-up is the Initiative retrospective (assess Φ compliance, not an Epic summary) + metric trend.
- **Input-output**: reads = value proposition · Epic dependencies · whether all Epics are ✅ / writes = `_initiative.md` (state · ultimate purpose · value proposition · Φ · Epic decomposition · completion criteria).
- **Core**: **value proposition = the cohesion rule** (not an arbitrary bundle). The retrospective assesses Φ realization. 5+ days / 2+ Epics / a shared theme → Initiative needed.

### flow-procedure-epic
- **Trigger**: `epic-setup` — after the epic-planning DRAFT is confirmed, initialize the Epic folder · `_epic.md` · Story decomposition.
- **What it does**: verify planning completion (DRAFT removed · approved) → create the Epic branch (specify a non-default base) → `_epic.md` required sections (goal/Discovery/scope/constraints/Story decomposition + dependency graph/completion criteria/progress) → Story folder + `_story.md` template → enforce the `**playbook**` field (missing → no-work-without-playbook hook). Wrap-up = verification + retrospective + archiving + PR.
- **Input-output**: reads = planning result · playbook selection / writes = Epic branch · `_epic.md` · Story folder · `_story.md`.
- **Core**: Epic = `_epic.md` is the sole SSOT. Enforce the `**playbook**` field (hook gate). With 3+ Stories, signal the execution order via a dependency graph.

### flow-procedure-story
- **Trigger**: `story-setup` (start) through `story-finish` (completion).
- **What it does**: Hard Gate pre-check (the immediately-preceding Story Squash is complete — Epic mode, to prevent conflicts) → create the Story branch → **create every Action file (A-NNN.md) exhaustively** (before action-execute, verify with `ls` that the count = the AC count) → update `_story.md` (inherit the ultimate-purpose header + Action table + delegation strategy) → execute Actions sequentially → wrap-up (all Actions ✅ + verification + AC assessment + retrospective + Squash → parent + `_epic.md` ✅).
- **Input-output**: reads = planning result · parent Epic/Initiative · Pre-flight 4 axes / writes = Story branch · all A-NNN.md · `_story.md`.
- **Core**: 1 file = 1 Action. Exhaustive A-NNN.md creation = Hard Gate (all must exist to execute). Retrospective mandatory (no empty boilerplate). Squash → parent only (a shared branch only when the user specifies it).

### flow-procedure-action
- **Trigger**: `action-setup` — create A-NNN.md during story-setup or when an additional Action is needed mid-Story.
- **What it does**: Pre-flight 4 axes (Step 0, Hard Gate — directory/persona/branch/Asset, 4-axis self-check with 4-line output) → determine the next Action number (`ls`) → (code) Read the project structure · convention guide → A-NNN.md required header (delegate_to / delegation_mode / target / AC mapping / state ⬜) + template → auto-determine the work type · RT rigor (user override possible).
- **Input-output**: reads = Action planning result · project agents · structure guide · parent AC / writes = A-NNN.md.
- **Core**: the Pre-flight 4 axes preemptively block a fake SSOT · persona intrusion · a wrong branch · an un-Read Asset (on failure, a user-decision flow). delegate_to is delegated to the project teammate definitions (no hardcoding). Supplementary reference `references/action-decomposition.md`: batching by commit topic, simple module integration (≤3 output files + ≤1 external reference), flow-asset Stories use grep/ls auto-discovery ACs.

---

## 4. Lifecycle · support (9)

### flow-phases
- **Trigger**: referenced on Phase transition / when context loss is detected.
- **What it does**: define the state machine of the 8 major Phases + the **Phase-Asset binding table** (11 transitions — entering a Phase requires an Asset Read as a Hard Gate; no entry if missing). 5-step context-loss recovery (judge the current Phase → reload the Asset → verify state → re-confirm `_story.md` → resume point). delegate_to pre-check list.
- **Input-output**: reads = `_epic.md`/`_story.md`/`A-NNN.md` / output = Phase-Asset binding table · recovery protocol.
- **Core**: Phase transition is Hard-Gated by the Asset Read. Context recovery is the mandatory 5 steps, not memory.

### flow-completion
- **Trigger**: the completion judgment before wrapping up an Action/Story/Epic.
- **What it does**: 3-level completion Hard Gate — Action (all ACs ✅ + retrospective) / Story (all Actions ✅ + retrospective + parent integration) / Epic (all Stories ✅ + retrospective + archiving + PR). Retrospective placeholders ("TODO" / "write later") are blocked; only KPT markers + meaningful text pass.
- **Input-output**: reads = task document · AC table · retrospective section / output = completion verification · retrospective quality bar.
- **Core**: completion = verification + retrospective (not a result summary). Dual enforcement at the hook gate + text level. **The parent-integration Hard Gate = the single SSOT for the integration *gate* across all layers (Story→Epic · Epic→Initiative)** — "did integration happen" lives in this one place, while the integration *strategy* (Squash · `--no-ff` · single mode) is in `flow-branch` (2-axis separation). Other procedures cite this gate (no restatement).

### flow-branch
- **Trigger**: branch creation/merge · integration (epic-setup · story-setup · story-finish); mandatory Read when judging branch mode.
- **What it does**: 3-layer naming (initiative/epic/story) + per-level merge strategy — **sub-branch mode**: Story→Epic = Squash, Epic→Initiative · Initiative→base = `--no-ff`. **single-branch mode (T5)**: when everything is meta · a single domain, commit with `[epic-N][US-N][A-N]` tags on one branch, and layer merges = "not applicable" (no disguised no-op). The SSOT for the integration *strategy* (whether there is a gate is in `flow-completion`). Shared-branch merge/push only when the user specifies it.
- **Input-output**: reads = current branch · `**branch mode**` field / output = branch commands · per-level strategy · single-mode rules · shared-branch protection.
- **Core**: shared-branch protection ("merge to main" only when specified; a plain "yes" is insufficient). **2 branch modes** (sub-branch default / single = meta · small-scale). Squash/`--no-ff` presuppose sub-branch mode — single mode has no merge.

### flow-archive
- **Trigger**: right before the epic-finish PR (or story-finish standalone mode · initiative-finish).
- **What it does**: 2-step interactive — Step 1: scan `epic-[name]/` → 4-way classification (completed tasks → `archives/` / retrospectives → integrate into the archive / permanent artifacts → the project-defined location / temporary plans → deletion candidates) + checkpoint / Step 2: confirm archiving complete + user chooses to keep/delete the workspace folder.
- **Input-output**: reads = `epic-[name]/` · `_epic.md` retrospective / output = classification table · checkpoint message · archive manifest.
- **Core**: archiving is never automatic (a checkpoint at each classification). The permanent-artifact location is a project decision. The retrospective is integrated directly into the archive.

### flow-retrospective
- **Trigger**: action/story/epic/initiative-finish; at epic-finish, Part 2 (3-step collection) is mandatory.
- **What it does**: Part 1 (retrospective format — 3 levels × code/meta branch) / Part 2 (interactive 3 steps — collect retrospectives → analyze recurring patterns → prioritize → 3–5 improvement items → Try 5-way classification (rule/skill/playbook/memory/backlog)) / Part 3 (forward loop — the Try tag guides entry into the next task, tracking evolution metrics).
- **Input-output**: reads = all A/Story/Epic retrospective sections / output = KPT · priority table · Try classification · 3 checkpoints · R3 self-attack result.
- **Core**: retrospective = assessment of AI behavior (no self-congratulation). The 3 conversational steps each require user confirmation. The Try tag → reflected in the next Epic planning (the evolution loop).

### flow-retrospective-templates
- **Trigger**: referenced when writing a retrospective (Action×2 / Story×2 / Epic×2 / Initiative×1 — code/meta).
- **What it does**: per-level · per-work-type format schemas. Code metrics (build time · test pass rate · regression · LOC) vs meta metrics (number of changed assets · reference parity · consistency · impact on Claude behavior). All fields mandatory (state "N/A" where not applicable; no empty fields). Action-item 4-column standard (priority/item/target/content).
- **Input-output**: format matched to work type · level / output = filled-in retrospective section · metric table · action items.
- **Core**: metrics branch per work type. No placeholders (only explicit N/A). The Epic retrospective covers reference parity Before/After. Initiative tracks evolution metrics.

### flow-upstream-publish
- **Trigger**: when a retrospective backlog is classified as a plugin-core/upstream improvement and needs board publishing (`retro-processing` backlog routing / retrospective M5 ownership routing).
- **What it does**: read the board coordinates from `settings.upstream_board` (if absent · unauthorized, defer publishing + notify) → check for duplicates → compose the 5-element detailed ticket (problem / recurrence source / target asset / proposal / completion criteria) → publish via `gh project item-create` → record the processing log. Zero board-name hardcoding in the skill body (coordinate SSOT = `config-defaults.json`).
- **Input-output**: reads = `settings.upstream_board` · retrospective backlog items / writes = board ticket + processing log.
- **Core**: general-purpose publishing (installation-independent — the "posting" ends there). The "processing" end is separated into the home repository's `.claude/skills/`. The internal default board is seeded into settings by `flow-config`/`flow-upgrade`.

### flow-must-not
- **Trigger**: referenced for per-situation prohibitions during execution (not the core SSOT — the core rules are in the plugin rules/, mostly hook-enforced).
- **What it does**: 4 hook-uncovered prohibitions — ① an implementation Action spec with no design result (the design artifact is the next spec) ② arbitrary "bundle small things" judgment ③ summarizing work results in the retrospective ④ loading completed (✅) Action files (context waste). No writing script files (use Write/Edit).
- **Input-output**: output = a list of concrete prohibited actions + hook-enforcement status.
- **Core**: per-situation (not blanket). Concrete actions, not abstract "cautions". Text-level enforcement (no technical blocking, an intent flag).

### flow-issue-handling
- **Trigger**: a problem discovered during action-execute (hook rejection · permission block · external-tool failure · procedure gap · SSOT mismatch).
- **What it does**: 3-axis classification (blocker × scope × outside-Epic) → 4 paths — ① immediate fix (blocker + in-scope) ② side commit (blocker + out-of-scope, `[side][scope]`) ③ retrospective + hand-off (non-blocker = Try) ④ explicit user hand-off (external policy/tool/Epic conflict). §2.5 teammate boundary violation (5 steps: detect → classify → return to main → reclassify → route).
- **Input-output**: reads = problem statement · scope · Epic scope / output = classification decision · path · user-option table · side-commit example.
- **Core**: a blocker ≠ deferrable (resolve before the next task, `no-defer-blockers`). An Epic non-goal violation requires explicit user agreement (a plain "yes" is insufficient).

---

## 5. Collaboration (3)

### handoff-protocol
- **Trigger**: when the main (lead) delegates to an expert teammate (Action execution).
- **What it does**: detect A-NNN.md `delegate_to` → spawn the teammate (pass context) → enforce separation of concerns (main = orchestration/verification/commit/retrospective, teammate = the primary work only) → 4-step delegation-failure fallback (auto-match → load the guide directly → A-NNN step → user confirmation) → specify Primary/Secondary in gray areas.
- **Input-output**: input = `delegate_to` (kebab teammate name or `(direct)`) / output = assignment confirmation + fallback gate + responsibility-separation table.
- **Core**: block two failure modes — non-standard notation / a teammate encroaching on flow management (no commit · verification · state update). "No nested teams" (a teammate cannot spawn another teammate; go via the main through the mailbox).

### debate-protocol
- **Trigger**: on design/structure improvement — verifying decisions before implementation.
- **What it does**: Phase A→B→C — A (find all problems P1·P2…, severity + rationale + impact, terminate after 3 consecutive rounds with no new findings) → B (per-category solution candidates + trade-off debate + integrated proposal; even a single candidate self-questions "why is there no alternative") → C (stress-test with Red Team). No compromise ("split the difference") — a higher-level alternative that resolves both sides' concerns.
- **Input-output**: input = design/structure change proposal / output = Phase A finding matrix · B proposal table · C verification rounds. **Record to the SSOT immediately right after each Phase ends** (not batched).
- **Core**: no mixing of finding and verification. SSOT recording = Hard Gate (entering the next Phase fails if the previous Phase is unrecorded).

### debate-redteam
- **Trigger**: debate-protocol Phase C + the R1 (plan review) · R2 (pre-commit code review) · R3 (retrospective) gates.
- **What it does**: define the Red Team attacker persona — no defending the status quo (improvement is the premise), prioritize the 4-stage attack (validity → attribution → consistency → methodology, ≥2 essence attacks per round), attack = a problem-statement + alternative-proposal pair (no criticism without an alternative), no easy concessions (self-audit on 2 consecutive concessions), a higher-level alternative over compromise.
- **Input-output**: input = attack target (B integrated proposal · plan Action · pre-commit code · retrospective) / output = a structured RT attack. **R1/R2 payload standard**: persona input + 4-line essence attack + high-priority issues (file + line + fix) + at least 1 alternative.
- **Core**: play the RT↔defense dual role as a method act (a complete switch). Termination has only 2 conditions (one side's rebuttals exhausted / both sides agree on a higher-level plan); a count ("we did 5 rounds, so stop") is void. An R1/R2 call without persona input is void. **Executor selection (§Executor selection = SSOT)**: Codex runs the RT/review pass when its plugin is available in a Claude Code session; otherwise the plugin's own RT mechanism (independent review agent, or self-review with the same payload) — an optional integration, never a dependency.

---

## 6. Meta (7) — procedures for building the plugin assets themselves (self-improvement)

### meta `user-invocable`
- **Trigger**: a request to create/modify an AI system component (Skill/Rule/Prompt/Subagent).
- **What it does**: judge the component type (Decision Tree) → present a 1-line rationale → grep for duplicates (`.claude/skills/` · plugins · `.claude/rules/` · `.claude/agents/`) → route to the corresponding procedure skill → orchestrate through to completion.
- **Core**: type judgment = a prerequisite to the procedure (a wrong type = a fundamental defect). 4 boundaries — Subagent (multi-turn + autonomous judgment + multiple skills) / Skill (a defined procedure) / Rule (declarative · session auto-load) / Prompt (≤50-line command).

### meta-skill-procedure
- **Trigger**: creating/modifying SKILL.md.
- **What it does**: judge Reference vs Procedure → check frontmatter order (name→description→metadata) · trigger keywords → ≤500 lines (200+ goes to references/) → grep for duplicate trigger keywords → description ≥3 triggers.
- **Core**: frontmatter order · 500-line cap · ≥3 triggers · stop on a duplicate trigger (integrate the existing one or rewrite the description). A Procedure skill requires a Verification section (executable commands).

### meta-skill-writing `reference`
- **Trigger**: referenced for the SKILL.md writing standard.
- **What it does**: synthesize the Agent Skills standard (agentskills.io) + project rules — frontmatter standard, 7-element persona (Role/Expertise/Core Beliefs/Anti-patterns/Decision Heuristics/Output Quality Bar/Sanity Self-Questions, **must be materialized in the body procedure** — no form-filling), 3-stage Progressive Disclosure, Step format (Work+Result), Verification = executable commands (not abstract questions).
- **Core**: the 7 persona elements are materialized as body constraints (Anti-patterns → check gates). Standard vocabulary comes from the rules/ reference table (no coinages).

### meta-rule-procedure
- **Trigger**: creating/modifying `.claude/rules/*.md`.
- **What it does**: distinguish Rule (declarative) vs Skill (procedural) → state the **scope of application** in the first section → 3-part structure (TL;DR + MUST/MUST NOT/SHOULD + checklist) → grep for duplicates · conflicts → confirm the `.claude/rules/` location (auto-load) → **no markdown links inside rule files** (the AI Reads directly; plain-text references only).
- **Core**: MUST ≠ SHOULD. Outside `.claude/rules/` has zero effect. A rule is objective + verifiable. High-cost actions (commit/merge) are insufficient with text alone — pair with a hook or procedural enforcement.

### meta-agent-procedure
- **Trigger**: designing/creating/improving the Subagent (teammate) system.
- **What it does**: classify into 7 work types → 4 teammate-candidate signals (high-frequency + clear persona = separate / low-frequency = keep as a skill / avoid domain overlap / always-on main + user conversation needed = main's responsibility) → 7-element persona → no nested teams (via the mailbox) → 4-tier LLM cost matrix → scope boundary + fallback → 2-step retrospective.
- **Core**: work type is the primary axis (TDD/BDD are variants within feature, not separate playbooks). No undefined teammates (must exist beforehand in `.claude/agents/`). The planning Phase is the main's responsibility (teammates only execute).

### meta-playbook-procedure
- **Trigger**: creating/modifying a playbook (a work-type procedure template).
- **What it does**: primary work-type classification (1 playbook = 1 work type, methodology is a variant) → **absorb** existing procedure flows (don't rewrite; cite the source and reuse) → README 7 elements (frontmatter/procedure/AC format/Hard Gate/feedback loop/violation handling/review·assessment) → placement decision (general → plugin playbooks/ / project-specific → `.flow/playbooks/` override) → grep-verify the 7 elements.
- **Core**: a playbook is an executable procedure, not a document to read. Absorb existing flows to prevent duplication. General ones avoid framework names (if an inherited flow has a framework name, generalize it or override).

### meta-prompt-procedure `reference`
- **Trigger**: creating a Prompt asset or judging a Skill promotion.
- **What it does**: the ≤50-line limit + promotion scorecard (promote to Skill on 2+ matches: line count >50 / procedure >3 steps / Verification needed / references/ needed / reuse ≥3×/week) → judge the type (executable/guide/hybrid) → `.claude/prompts/` location → 1-line description.
- **Core**: the 50-line cap is absolute. Prompt = a simple command wrapper. Promotion is a Hard Gate (with 2+ criteria met, Prompt qualification is void → route to meta-skill-procedure).
