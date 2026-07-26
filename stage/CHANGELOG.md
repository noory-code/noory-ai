# Changelog

## 0.45.1 — 2026-07-27

- Give both close-time reviewer paths a close-owned JSON list of paths carried by the HEAD commit,
  so autonomous and staged reviews receive the same explicit material contract.
- Make configured close-time review strengths open those committed paths directly without deriving
  review material from Git diff or index state.

## 0.45.0 — 2026-07-26

- Give supervised reviewers a driver-owned JSON list of paths changed by the executor so they open
  repository files directly instead of deriving review material from a disposable Git index.
- Stop passing the executor's isolated index to supervised review while retaining executor-side
  index isolation and support for untracked files and repositories without an index.

## 0.44.0 — 2026-07-26

- Isolate executor staging in a disposable Git index shared with review, protecting the human's
  pending commit, and fail an executor attempt whose repository state does not change.
- Make review judge the work card's criteria, separate out-of-criteria observations, and fail
  closed for every review command that exits unsuccessfully or returns no verdict. Pass the work
  card's absolute path to both supervised and close-time reviewers so each review seat applies
  that contract to the selected work.
- Let the driver target one runnable work card directly, and preserve the latest unattended
  blocking output when closure escalates for human attention.

## 0.43.16 — 2026-07-26

- Pass the closing work card's absolute path to both autonomous independent reviews and opt-in
  per-stage reviews through `STAGE_WORK_ITEM_PATH`. Acceptance and additional verification
  commands remain outside this close-time review environment contract.

## 0.43.15 — 2026-07-26

- Make every configured review command fail closed when its reviewer exits nonzero or produces
  neither a `[P1]` blocker nor an `APPROVED` verdict. A `[P1]` result still blocks, while
  `APPROVED` alone passes.
- Document that a review command unable to produce a verdict must fail with a nonzero exit code or
  a `BLOCK:` verdict.

## 0.43.14 — 2026-07-26

- Preserve the latest failed `close_work` output in unattended escalation records when acceptance
  or the independent review blocks closure. The evidence reuses the passing-close bound of the
  final 40 lines and 4000 bytes, including the omission marker, and a retry carries its latest
  close result instead of the earlier failure.
- Update the unattended-mode status to reflect that W-00000075's known code defects are closed
  while retaining the warning that no real work has completed the loop end to end.

## 0.43.13 — 2026-07-26

- Let supervised and unattended driver runs target a runnable leaf work item directly, without a
  wrapper parent. A target with any unfinished child remains a parent and is never selected
  directly, preserving existing child and subtree selection.

## 0.43.12 — 2026-07-26

- Document the post-review disposition step: stage-retrospective requires every review finding to
  carry an accept/decline/defer disposition with a recorded reason (declines included, P1
  declinable), and stage-drive explains that a BLOCK surfaces the reviewer's voice without
  deciding for the human. Rewrite stage-drive's stale `NO-PROGRESS` description to match the
  current fingerprint (tracked diff against `HEAD` plus untracked hashes) and the repository-state
  no-change failure.

## 0.43.11 — 2026-07-26

- Pass the selected work card's absolute path to the supervised independent reviewer through
  `STAGE_WORK_ITEM_PATH`. The review-command contract now separates criterion-by-criterion verdicts
  from non-blocking out-of-criteria observations and permits P1 blocking only for failed card
  success criteria.

## 0.43.10 — 2026-07-26

- Reject a successful supervised or unattended executor attempt when its repository-only
  pre/post fingerprint is identical. The failure names `close_work.py` as the explicit manual path
  for work that was already complete, while the existing acceptance-output-based `NO-PROGRESS`
  fingerprint remains unchanged.

## 0.43.9 — 2026-07-26

- Run supervised and unattended executors with a copied disposable Git index, then carry that same
  index into independent review. Executor staging no longer touches the human's real index, and the
  driver no longer restores an old snapshot over index updates made while a step is running.
- Warn operators not to edit or run repository-changing Git commands in the shared checkout while
  a driver step is active.

## 0.43.8 — 2026-07-26

- Record a passing close-time review under an explicitly labeled evidence block in the card's
  `## Verification` section, preserving the review command and clipped verdict output alongside
  verification evidence.
- Report the number of verification commands actually executed by `close_work`, including stored
  card acceptance commands as well as additional `--check` arguments.

## 0.43.7 — 2026-07-26

- Initialize a missing disposable reviewer index as empty only when the repository has no `HEAD`.
  A committed repository with no real or executor-created index now fails review preparation closed
  instead of showing the reviewer an empty diff.
- Fail progress fingerprinting closed when tracked-diff inspection cannot start or an unborn-branch
  fallback diff fails. A path outside a Git worktree remains an explicit supported state rather
  than being misreported as a Git failure.
- Preserve trailing backslashes when Windows arguments containing `cmd.exe` metacharacters require
  driver-added quotes, so the closing quote cannot be escaped into the argument.

## 0.43.6 — 2026-07-26

- Fail closed when progress fingerprinting cannot enumerate untracked files instead of silently
  omitting them and potentially reporting false `NO-PROGRESS`.
- Treat a repository with no commits and no Git index as an empty-index review case. The driver
  initializes only the disposable reviewer index and leaves the real absent index unchanged.
- Print executor evidence before reporting index snapshot or restoration failures, including when
  both operations fail, so the operator retains the executor's account of the attempt.
- Quote Windows audit-command arguments containing `cmd.exe` metacharacters as well as whitespace,
  preserving project paths containing `&`, `^`, `|`, `<`, or `>`.

## 0.43.5 — 2026-07-26

- Make unattended lifecycle bookkeeping fail closed. Failures to commit escalation, pre-close
  retry, or ancestor-aggregation records now stop the run for human handoff, matching the existing
  item-close behavior instead of continuing without durable Stage history.
- Always include the Stage audit when closing a ready parent. Parent-declared acceptance commands
  now run in addition to the audit rather than replacing it, preserving the aggregation
  verification contract.
- Join the audit command the way the running platform's shell parses it. The audit string is handed
  to a shell, so a path containing a space split into several arguments and the check failed; that
  now matters on every parent close rather than only on parents without their own acceptance. POSIX
  shells strip single quotes and `cmd.exe` does not, so each gets its own joiner rather than one
  quoting style that breaks the other. This covers spaces; a project path containing a `cmd.exe`
  metacharacter (`&`, `^`, `|`, `<`, `>`) is still unhandled and tracked as W-00000077.
- Let `close_work` merge a card's own acceptance commands. The driver had been passing a parent's
  acceptance list as extra checks, but `close_work` already merges the card's own list, so every
  parent close ran those commands twice.

## 0.43.4 — 2026-07-26

- Harden supervised review preparation after the executor exits. Failure to copy the executor's
  index into the disposable reviewer index can no longer bypass restoration of the human's
  original index; if both snapshot and restoration fail, the escalation reports both failures.
  Untracked-file discovery now fails closed even when Git returns no stderr, new untracked paths
  are frozen before acceptance commands run so verification artifacts do not enter the reviewer
  diff, and progress fingerprints cover staged and unstaged changes in repositories with an
  unborn `HEAD`.

## 0.43.3 — 2026-07-26

- Make supervised execution review and progress detection cover the executor's complete output.
  The driver snapshots and restores the real Git index around the executor, then gives the
  independent reviewer a disposable index where only executor-created untracked files are marked
  intent-to-add. Review commands using `git diff` now see new file contents without mixing
  executor staging into the human's index, including after executor failure. Progress fingerprints
  now cover staged changes, unstaged tracked changes, and hashed untracked files, preventing
  new-file-only or staged-only work from being misclassified as `NO-PROGRESS`.

## 0.43.2 — 2026-07-25

- Correct three defects a second independent review found in the `stage-drive` skill. Command
  examples no longer use `${CLAUDE_PLUGIN_ROOT}` — that variable is injected into hook commands
  only and expands to nothing in the shell that runs skill commands; per decision DE-00000031 the
  skill now locates the driver relative to its own directory (`../../scripts/drive.py`) and every
  example carries a `<driver>` placeholder for the resolved absolute path, with the Stage source
  checkout's repository path kept as the marked exception. The unattended-mode status no longer
  claims all review findings were fixed: the open defects — unchecked Stage bookkeeping commits in
  three of four places, a parent close that skips the structural audit — are stated and routed to
  W-00000075. The `NO-PROGRESS` description is narrowed to what the fingerprint actually sees:
  unstaged edits to tracked files only, so staged changes are as invisible as untracked new files
  (root fix tracked as W-00000073). The `<driver>` placeholder is quoted in every example, so a
  plugin installed under a path containing spaces still runs.

## 0.43.1 — 2026-07-25

- Correct four defects independent review found in the `stage-drive` skill. Command examples now
  use `${CLAUDE_PLUGIN_ROOT}/scripts/drive.py`, the path that resolves in an installed plugin —
  the previous `stage/scripts/drive.py` form only exists in the Stage source checkout, which is
  now called out as the exception. The conditions that end a step in `blocked` are stated as three
  (exhausted limit, `NO-PROGRESS`, independent reviewer `BLOCK:` verdict), not two — a reviewer
  BLOCK escalates unconditionally and must not be answered by rerunning the step. `NO-PROGRESS` is
  described as what the fingerprint actually watches: the tracked-file `git diff` plus acceptance
  output, which cannot see untracked new files, so it is not proof the executor did nothing.
  The unattended-mode status now matches the record: two independent reviews both demanded
  changes, all eleven findings were fixed, and no pass verdict exists — the reviewer's final
  verdict was never retrieved.

## 0.43.0 — 2026-07-25

- Expose the driver as the `stage-drive` skill. Every other lifecycle flow has an entry skill, so
  an agent that reads the plugin's skill list had no way to learn that `drive.py` exists — the
  driver was reachable only from `docs/SCHEMA_V4.md`. The skill states when to reach for the
  driver, that the default invocation is a side-effect-free dry run, the two settings gates that
  fail closed (`executors`, and a reviewer whose venue differs from the item's), what a single
  `--execute` step deliberately leaves for the human, and that `--unattended` refuses to start
  without a `limits` config. It also records that unattended mode, though code-reviewed and
  tested, has never been exercised on real work, so it is not offered as an ordinary alternative
  to supervised execution.

## 0.42.3 — 2026-07-25

- Document the Windows `cmd.exe` syntax for executor environment variables and cover unattended
  executor context injection with a regression test.

## 0.42.2 — 2026-07-25

- Pass the target work item context to executor processes in both supervised and unattended modes
  through `STAGE_WORK_ITEM`, `STAGE_WORK_ITEM_PATH`, and `STAGE_PROJECT_ROOT`. Previously, the
  executor had no way to know which work item it was operating on.

## 0.42.1 — 2026-07-25

- Warn that a delegation bridge must be restarted after a Stage version change. A bridge process
  resolves this plugin's paths once at startup, so a version bump leaves it reaching for a
  directory that no longer exists and the executor fails on its first tool call — often before it
  can read the card it was sent. This bit two delegated runs in one session, each recovered only
  because a human remembered. `stage-handoff` now names the symptom and the fix.

## 0.42.0 — 2026-07-25

- Support comments in project settings through either `settings.json` or `settings.jsonc`.
  Comment removal recognizes JSON strings, so URL and path values containing `//` remain intact;
  projects that contain both filenames fail closed instead of silently selecting one.
- Initialize new projects with an English-commented `settings.jsonc`. Language selection and
  schema migration update only the existing value token in commented files, preserving
  user-authored comments instead of reserializing the whole file.

## 0.41.0 — 2026-07-25

- Centralize project-settings path construction, reading, and JSON parsing in
  `stage_paths.read_settings()`. Hook and script callers keep their existing failure policies:
  permissive readers still use their prior defaults, validation callers still report errors, and
  the governance gate still fails closed when settings are present but untrusted.

## 0.40.3 — 2026-07-25

- State what the hooks can see. `operations/hooks.md` listed the blocked actions without saying
  that a hook only ever sees a tool call, so a program writing to `.stage/official/` passes with no
  intent and nothing consumes one — which reads as a hole to be plugged rather than the edge of
  what a PreToolUse gate can do. An intent is now described for what it is: a declaration of which
  work item authorized a change, enforced on the writes the guard can see, with `audit_stage.py`
  as the independent check afterwards.

## 0.40.2 — 2026-07-25

- Remove a work item's remaining per-path promotion intents when `archive_work.py` archives it,
  without touching intents owned by other work items. `audit_stage.py` now reports `WORK025`
  warnings for pending intents left behind by already archived work.

## 0.40.1 — 2026-07-25

- Say who commits when a card is delegated. `stage-handoff` described what the executing venue
  produces and who reviews it, but never named the agent that turns the change into a record, so
  a delegated run could be told to commit — and a bridged executor that cannot write to `.git`
  discovers this only after the implementation is finished. The skill now walks the delegated run
  end to end: the executor starts the card, produces the change and stops with a dirty tree; the
  host reviews it, re-runs the checks itself, commits while the card is open, then closes and
  archives.

## 0.40.0 — 2026-07-25

Detect and refresh stale project guidance (W-00000057):

- `audit_stage.py` now compares template-backed `.stage` Markdown guidance with the current
  locale overlay and reports `TEMPLATE004` warnings for drift. `guidance_overrides` declares
  intentionally project-owned paths.
- `refresh_guidance.py` supports plan-only `--dry-run`, full replacement for prose-only
  templates, project-row preservation for a single template-empty table, default exclusion for
  templates with populated tables, and explicit path selection for their full replacement.
  Ambiguous templates with multiple empty tables fail closed.
- Schema-v3 migration keeps guidance drift visible but non-blocking so users can run the explicit
  refresh command after structural migration.

## 0.39.1 — 2026-07-25

- Make the `planning` and `design` verification criteria in the project template
  topology-neutral (W-00000055): they named schema-v3 paths (`present/state/questions/`,
  `present/work/decisions/`), yet `operations/verification.md` is shared byte-identical across the
  v3 and v4 template roots, so no single topology path can be correct. Describe the artifacts
  instead of a path.

## 0.39.0 — 2026-07-25

Block opaque inline interpreter access to Stage paths (W-00000054):

- The PreToolUse guard now refuses shell commands that reference `.stage` while running inline
  interpreter code through `-c`, supported `-e` options, or a heredoc. The guard cannot verify
  writes hidden inside those interpreter bodies, so callers must use gated Write/Edit tools or a
  named script file. Named scripts, `-m` module invocations, and inline code without `.stage`
  remain allowed.

## 0.38.0 — 2026-07-24

Register Stage runtime state in git ignores during initialization (W-00000051):

- `init_stage.py` now adds `.stage/.runtime/` to a git project's `.gitignore` on every
  initialization, including worktree and submodule checkouts whose `.git` is a file. Existing
  content is preserved byte-for-byte, equivalent uncommented entries are idempotent, and non-git
  directories remain untouched.

## 0.37.2 — 2026-07-23

Harden the unattended driver loop per a second independent-review pass (W-00000049):

- A failed parent aggregation-close now stops the run with a non-zero exit instead of being
  silently ignored (`close_ready_ancestors` returns an error the loop checks). `commit_item` and
  `commit_lifecycle` refuse to commit unless HEAD is on a `stage/driver/` run branch — guarding the
  base branch on every commit, not only before the executor-output commit. New regression test.

## 0.37.1 — 2026-07-23

Fix the unattended driver loop per the independent review findings (W-00000049):

- Addresses the Codex review (CHANGES-REQUESTED) of `--unattended`: a failed executor now escalates
  instead of being masked by "nothing to commit"; the `.stage` lifecycle records (card status,
  retrospective, indexes) are committed to the run branch alongside the executor output; the loop
  re-checks it is on the run branch before every commit and requires a clean tree to start;
  selection covers the whole subtree, not just direct children; escalation and parent-close results
  are checked (a failed escalation stops the run); subprocess timeouts are bounded by the remaining
  wall-clock budget; the driver-generated retrospective no longer claims success before close
  verifies; and a parent's aggregation-close verification (audit + aggregation gate, children
  already reviewed) is an explicit contract (DE-00000027). New regression tests cover the failure
  paths the first tests dodged. `--unattended` still needs a re-review before use. (DE-00000024,
  DE-00000027)

## 0.37.0 — 2026-07-23

Unattended autonomous-execution driver loop (W-00000048):

- `drive.py --unattended <parent>` runs the whole ready subtree unattended on an ISOLATED
  `stage/driver/<target>-<ts>` branch (full-unattended, DE-00000024) — the base branch is never
  touched. It refuses to start without a `limits` config (no unbounded loop). Each iteration selects
  the next ready autonomous leaf, runs its executor (the `executors` config), commits to the run
  branch, writes a mechanical driver-generated retrospective, and closes the item via `close_work`
  (re-running acceptance + the mandatory independent review); it closes parents up to the target as
  their children become terminal. Any failure / reviewer BLOCK / no-progress / attempt-cap escalates
  the item (`escalate_work` → blocked + a pending decision) rather than fake-completing; a global
  iteration or wall-clock ceiling stops with a non-zero handoff. The loop never creates work,
  promotes official truth, or crosses a human-approval gate. Supervised dry-run/`--execute` is
  unchanged. Real executor commands and live runs are gated behind separate human verification.
  (DE-00000024)

## 0.36.0 — 2026-07-23

Supervised autonomous-execution driver — MVP (W-00000047):

- `drive.py <parent>` plans (and, with `--execute`, runs one supervised step of) the autonomous
  loop for a target parent's subtree, wiring the four controls together: it selects one ready leaf
  child (non-terminal, has acceptance), resolves its executor (new `executors` venue→command
  config), its acceptance checks, its opposite-venue independent reviewer, and the execution limits.
  Dry-run is the default and has ZERO side effects; `--execute` runs exactly one
  executor→acceptance→independent-review sequence, records per-item attempt state and a no-progress
  fingerprint under untracked `.runtime/driver/`, and prints a recommended next action. It never
  commits, closes, escalates, promotes, creates work, or advances a parent — those stay explicit
  steps. Missing executor/reviewer or malformed limits fail closed. The full unattended loop (auto
  commit/close/escalate/aggregate over a whole subtree) is a later ship. (DE-00000013, DE-00000023)

## 0.35.0 — 2026-07-23

Escalation exit and execution-limit config for the autonomous-execution driver (W-00000046):

- `escalate_work.py` transitions an open (active/review) work item to `blocked` and creates a
  linked pending decision recording why the autonomous loop stopped and what human decision is
  needed — the invariant is `blocked` + a decision, never `completed`.
  `stage_paths.load_limits_config` reads an optional settings.json `limits` section (per-item
  attempt cap + global iteration and wall-clock ceilings) with fail-closed validation. This is the
  escalation EXIT and the limit thresholds; the driver (W-00000047) does the attempt counting,
  no-progress detection, and budget enforcement that trigger the exit. (DE-00000017, DE-00000022)

## 0.34.0 — 2026-07-23

Parent aggregation gate for the autonomous-execution driver (W-00000045):

- A parent work item may complete or close only when every direct child is terminal (status in
  {completed, archived, rejected}); children are gathered across the current, planned, and archive
  zones, so an unstarted (planned) or in-progress child blocks the parent. Enforced uniformly at
  `close_work`, the completion/commit gate, `archive_work`, and the audit (WORK024) through a single
  `non_terminal_children` definition. A rejected child counts as terminal; a leaf item with no
  children is unaffected. Auto-advancing the parent is deliberately left to the driver (W-00000047);
  this item builds only the query and the gate. (DE-00000015, DE-00000021)

## 0.33.0 — 2026-07-23

Venue-separated independent review for autonomous items (W-00000044):

- An `autonomous: true` work item must, at close, pass an independent reviewer whose venue differs
  from the item's execution `venue` — an executor cannot grade its own work (the third control of
  the autonomous-execution driver). `review.reviewers` in settings.json maps venue → reviewer
  command; `close_work.py` resolves the sole differing-venue reviewer and runs it, blocking on a
  nonzero exit or a `BLOCK:` line. No differing-venue reviewer, or an ambiguous map, fails closed —
  the item cannot auto-complete and escalates. `WorkItem` gains a parsed `venue`; the completion
  gate requires `review: passed` for autonomous items. Non-autonomous items keep the opt-in
  per-stage review unchanged. (DE-00000016, DE-00000020)

## 0.32.0 — 2026-07-22

Machine-checkable acceptance for autonomous work items (W-00000043):

- Work items gain two frontmatter fields: `autonomous` (boolean eligibility signal, default
  `false`) and `acceptance` (YAML list of shell-command verification steps). `register_work.py` and
  `start_work.py` refuse an `autonomous: true` item that carries no `acceptance` command (Fail
  Fast). `close_work.py` runs the item's stored `acceptance` commands merged with any `--check`
  arguments — all must exit zero — so an autonomous item verifies its own completion without a
  human supplying the checks. The current and planned templates and `docs/SCHEMA_V4.md` document
  the fields. This is the first control of the autonomous-execution driver contract (DE-00000014,
  DE-00000018).

## 0.31.3 — 2026-07-15

Bug fix (enum gate):

- The PreToolUse enum gate validated a planned work card's `status` against the current-work
  enum (`active/blocked/review/completed/archived/rejected`), rejecting the planned statuses the
  audit accepts (`captured/triaged/ready/selected/deferred/rejected`). Writing any new
  `work/planned/` card was denied. The gate now selects the status enum by the card's zone —
  planned cards validate against `WORK_PLANNED_STATUSES`, current/archive cards against
  `STATUS_VALUES` — mirroring the audit split (BACKLOG001 vs WORK005). The other work fields
  never appear on a planned card, so one field table still serves both.

## 0.31.2 — 2026-07-13

Concept-layer docs rewritten to schema v4 (docs only):

- README, the operations docs (before/during/after/artifacts/backlog/hooks/review), and
  docs/BLUEPRINT.md now describe the v4 topology (official/work/decisions/state/proposals/
  roadmap) and the planned/current/official lifecycle vocabulary enforced by gates, instead of
  the retired past/present/future directories. The artifact catalog documents the roadmap
  family (TH-/M-), per-type id counters, the milestone/terminal_disposition fields, and closure
  semantics. Historical design records (docs/DISCUSSION.md, docs/IMPLEMENTATION_AUDIT.md) keep
  their v3 references as history. (W-00000039)

## 0.31.1 — 2026-07-13

Schema-v4 migration and external-project QA hardening:

- Added adversarial v3->v4 fixtures for mutation-free preflight refusals, exact abort,
  customized and Korean content, Contract X decision identity, milestone closure gates, and a
  strict-audit-clean full lifecycle on a migrated project. Fixed `.stage/.runtime/` dirt being
  misclassified as blocking git dirt and made abort remove only migration-created empty runtime
  directories while preserving pre-existing runtime state. (W-00000038)

## 0.31.0 — 2026-07-13

Schema v4 activation and one-shot project migration:

- schema v4 ACTIVATED — enforced contract version is now 4; stage-migrate skill performs the
  one-shot v3->v4 migration; v3 projects fail closed with a banner naming stage-migrate
  (no-stranding invariant); read-only audit and migration remain callable on v3. (W-00000037)

## 0.30.0 — 2026-07-13

Schema-v4 milestone closure with immutable evidence:

- Added v4-only milestone closure snapshot + fail-closed promotion revalidation + preventive
  re-attribution gate; v3 unchanged; enforced version stays 3. `close-milestone` freezes the
  exact linked W ids, card-owned accepted/rejected terminal dispositions, and completion-criteria
  attestation behind the Contract X predecessor chain. Promotion prints exact live-basis diffs,
  effective snapshots prevent milestone changes unless the same change supersedes the closure,
  and superseding reopen decisions return computed milestone status to active. (W-00000036)

## 0.29.0 — 2026-07-13

Schema-v4 roadmap creation and derived state:

- Added the v4-only `stage-roadmap` skill and CLI for registry-allocated Theme/Milestone
  creation, index synchronization, pursuit decisions, and computed roadmap listing. Decision
  chains now reject dangling links, cycles, unresolved forks, and multiple effective heads;
  roadmap audits validate references and family indexes; session context renders the derived
  active-milestone table. Schema v3 is unchanged and the enforced version stays 3.
  (W-00000035)

## 0.28.0 — 2026-07-13

Dormant schema-v4 lifecycle operations and milestone attribution:

- Lifecycle CLIs gain dormant v4 capability + milestone field/question; v3 unchanged; enforced
  version stays 3. `register_work.py`, `start_work.py`, `close_work.py`, and `archive_work.py`
  dispatch through the topology registry for schema-v4 fixtures, while registration accepts one
  optional `milestone:` attribution and the stage-work skill asks about milestones only when its
  open-milestone detector reports at least one. Real-CLI coverage drives a v4 card from planned
  through current and review into the official archive with a clean audit after every step.
  (W-00000034)

## 0.27.1 — 2026-07-13

Dormant schema-v4 lifecycle visibility and stale-topology defense:

- Added v4-only legacy-root denial and derived lifecycle views; v3 unchanged; enforced version
  stays 3. The write gate now rejects attempts to recreate retired v3 roots and points to their
  registry-derived v4 replacement, while session-start context summarizes planned, current,
  official, and decision-derived roadmap records from registry scan roots. (W-00000033)

## 0.27.0 — 2026-07-13

Dormant per-project schema-v4 consumer dispatch:

- `stage_guard`, `stage_work`, `stage_context`, `stage_records`, and `audit_stage` now derive
  schema-v4 project paths from the topology registry when that project's `settings.json`
  declares `schema_version: 4`. Schema-v3 behavior is unchanged; consumers gain dormant v4
  capability gated on the project's `schema_version`; the enforced contract version stays 3.
  Regression fixtures cover both initialized v3 projects and the dormant v4 template across
  write/commit gate decisions, record scans, audit, and session context. (W-00000032)

## 0.26.0 — 2026-07-13

Dormant v4 template tree, no behavior change:

- Added the dormant v4 template tree and Korean prose overlays, including Theme and Milestone
  templates and family indexes. This is a files-only addition with no behavior change; v3
  initialization and consumers remain active and unchanged. (W-00000030)

## 0.25.3 — 2026-07-13

Schema v4 design amendment (design only — no behavior change):

- The v3-to-v4 migration is specified as a user-facing `stage-migrate` skill (not just an
  internal script), and a no-stranding release-ordering invariant is added: no shipped plugin
  version enforces schema v4 unless that same version also ships the migration skill and a
  completed migration path. C3-C6 ship dormant and v3-compatible; the C7 release activates v4
  enforcement and carries the migration skill together (SCHEMA_V4.md, DE-00000011, W-00000029).

## 0.25.2 — 2026-07-13

Git-add redirection leak fix:

- `git_add_paths_from_command` now stops scanning at the first shell redirection, so
  redirection tokens and everything after them are not treated as added paths. (W-00000028)

## 0.25.1 — 2026-07-13

Backlog index row placement fix:

- `register_work.py --backlog` now inserts captured work rows inside the Current backlog
  table, preserving populated tables and any sections that follow them. Direct active-work
  registration uses the same table-aware insertion path, with regression coverage for empty,
  populated, and trailing-section index shapes. (W-00000027)

## 0.25.0 — 2026-07-13

Close/archive ordering guard:

- `close_work.py` and `archive_work.py` now refuse to proceed when git reports staged or
  unstaged paths inside the item's scope, excluding `.stage/` changes. Non-git projects keep
  the existing flow, and regression coverage pins in-scope, out-of-scope, Stage-only, and
  non-git behavior. (W-00000025)

## 0.24.6 — 2026-07-13

Global retrospective identity validation:

- The Stage audit now reports `RETRO003` when an R-id appears in both present and archived
  retrospective locations, including conflicts where the files name different work items.
- `close_work.py` now fails closed before running verification when the item's
  `retrospective_ref` already belongs to a different archived work item. Regression coverage
  pins both enforcement points. (W-00000024)

## 0.24.5 — 2026-07-13

Archive retrospective collision fix:

- `archive_work.py` now refuses to overwrite an archived retrospective whose `work_item`
  belongs to a different work item, while preserving idempotent re-archive behavior for the
  same work item. Regression coverage verifies both paths and prevents partial archive
  mutations on conflict. (W-00000023)

## 0.24.4 — 2026-07-13

Verification evidence preservation fix:

- `close_work.py` now preserves the existing `## Verification` body and appends a dated
  `Executed at close` block with the executed check evidence instead of replacing hand-recorded
  evidence. Regression coverage verifies that both forms of evidence survive. (W-00000022)

## 0.24.3 — 2026-07-13

Archive review-row cleanup fix:

- `stage-archive` now removes a completed card's `review.md` row by its item link, so rows
  with hand-written artifact labels no longer survive archiving and trigger `INDEX002`.
  The regression coverage retains the machine-generated row case and adds the hand-written
  variant. (W-00000021)

## 0.24.2 — 2026-07-13

Cardless board upkeep doctrine (docs only):

- `operations/before.md` declares that board upkeep (registering, moving, indexing, closing,
  archiving cards) is performed directly through skills, scripts, and hooks and never gets its
  own work card; cards exist only for product changes traced to an incident, a user request,
  or a decided design. (W-00000020)

## 0.24.1 — 2026-07-13

Cross-venue delegation and review contract (docs only):

- `stage-handoff` gains the Delegated execution doctrine: `venue` names the surface that
  EXECUTES the work, not the window that hosts it; a bridge-equipped window may carry out
  another venue's card by delegation, monitors the run, and reviews the output before close.
  Decision points and promotion approvals never delegate.
- `operations/review.md` gains the Cross-venue review posture: the executor of a card and the
  reviewer of that card must be different venues; delegated output is reviewed by the hosting
  window at close, and self-closed cards bind the counter-venue through the existing
  `review: pending` + settings strength gate. (W-00000020)

## 0.24.0 — 2026-07-13

Schema-v4 topology registry foundation (dormant until the consumer-adoption cards):

- New `hooks/stage_topology.py` is the tooling SSOT for v4 families and zones, lifecycle and
  status projections, family-local artifact counters, stable `DE-` plus legacy `D-` decision
  resolution, scan roots, retrospective locations, and the bijective v3-to-v4 relocation map.
- `stage_paths.py` exposes the v4 `official/` authorization-zone and work-archive predicates;
  schema-v3 consumers retain their existing predicates until their scheduled rewiring.
- Registry tests cover every public resolver, relocation and identity compatibility, and
  parity between the registry's official root and the authorization boundary. A measured
  conformance ratchet rejects new legacy-topology consumers and count increases while C4-C5
  and C7 reduce the 11 existing schema-v3 consumers to zero (DE-00000010).

## 0.23.2 — 2026-07-12

Schema v4 design amendment (design only — no behavior change):

- The authorization zone renames `past/` → `official/` in the v4 design: the zone name now
  equals the lifecycle state name (planned/current/official), since canon and model are living
  official truth rather than history. The rename rides the same one-shot v4 migration; the
  migration contract gains intent preflight (zero pending intents/claims) and post-relocation
  verification that no durable field still targets legacy roots (DE-00000009 amended).

## 0.23.1 — 2026-07-12

Schema v4 design freeze (design only — no behavior change):

- New `docs/SCHEMA_V4.md`: the canonical PAST-ANCHORED topology design — `past/` retained
  verbatim as the sole authorization zone; `present/`/`future/` wrappers retire in favor of
  responsibility roots (`work/`, `decisions/`, `state/`, `proposals/`, `roadmap/`); lifecycle
  becomes the planned/current/official vocabulary enforced by gates; topology registry,
  Contract X decision identity, W `milestone:`/`terminal_disposition` contracts, roadmap
  closure semantics, migration contract, and the C1-C9 implementation plan (DE-00000009,
  W-00000018).

## 0.23.0 — 2026-07-12

Unified work-card lifecycle — the backlog becomes the planned column of one W-card board
(DE-00000007):

- A work card is ONE `W-*` artifact for its whole life: captured in `future/backlog/items/`
  (planned statuses `captured`/`triaged`/`ready`/`selected`/`deferred`/`rejected`), physically
  moved to `present/work/items/` when work starts, archived as before. The `B-` family and the
  `source`/`realized_by` realization links retire; `parent` is the only work lineage and legacy
  `source:` fields are inert history.
- `register_work.py --backlog` captures a planned card (indexed in the backlog index, no
  venue/split checks yet); new `scripts/start_work.py` performs the move: sets `active`,
  requires the `scope` declaration, derives the venue from `venue_routing`, and enforces the
  split/exception contract (DE-00000005) at start. Card ids are unique across all three
  lifecycle locations (a card in two columns is an SSOT001 error).
- The audit validates planned-card statuses and cross-column parents, keeps the backlog index in
  lock-step with W (and legacy B) rows, and drops the retired realization checks
  (WORK020/WORK023/BACKLOG004/005/006).
- `STAGE_SCHEMA_VERSION` bumps to 3. `migrate_stage.py` converts unrealized `B-` items to
  planned `W-` cards (bodies preserved, parents remapped), removes realized/rejected `B-` items
  (their record lives in the archived work card; git history keeps the files), rewrites the
  backlog index, and stamps the schema — idempotent, dry-runnable.
- English and Korean backlog templates, the plugin backlog/artifacts operation docs, skills, and
  the SessionStart artifact map describe the board model.

## 0.22.0 — 2026-07-12

Routing contract completion — review fixes for the B-00000001..3 releases (DE-00000005):

- Split contract: `venue_routing` values may be the reserved token `split`, declaring a kind
  mixed by definition. `register_work.py` refuses to register such a kind as one item and
  prints the resolution (separate design/implementation items with `parent` lineage); the
  audit reports an open single item of a split kind (`VENUE005` error).
- Validated venue exceptions, one contract for CLI and audit: a policy-contradicting venue or
  a deliberate single split-kind item is accepted only with a linked decision record that
  exists, is `decided`/`promoted`, declares `authorizes: venue_exception`, and names the work
  item. `register_work.py --decision <DE-id>` validates at registration and stamps
  `decision_refs`; message-only acceptance is removed; `VENUE003` becomes an error.
- Completion gate on open decisions: `close_work.py` refuses to complete an item whose
  `decision_refs` names a decision still `status: open`, and the audit reports any
  completed/archived item referencing one (`DECISION002` error).
- Routing SSOT guidance corrected everywhere it was stale: English and Korean templates
  (canon vocabulary, work-item README, decisions README) now state that `settings.json`
  `venue_routing` owns machine routing while canon owns venue meaning only, and no longer
  call audited routing "advisory".
- No-policy, single-venue, and custom-venue projects keep current behavior; every new check
  activates only when a policy is declared or a decision is actually linked.

## 0.21.0 — 2026-07-12

Role-policy-driven venue routing and self-contained handoffs (DE-00000004):

- `settings.json` gains `venue_routing`: a project-declared `kind -> venue` map (venue names
  are project-defined strings; no AI product is hard-coded). Missing or empty → venue stays a
  purely advisory per-item field with zero new findings.
- `register_work.py` derives an omitted `--venue` from the policy and announces a
  policy-contradicting explicit venue as an exception that must carry a `decision_refs` link.
- The audit gains `VENUE001` (routed kind, no venue), `VENUE002` (venue outside the declared
  set), `VENUE003` (policy contradiction without a decision link), and `VENUE004` (malformed
  map) — open present items only; archived history is not judged against today's policy.
- SessionStart injects the declared routing map with the behavior rules: derive venue without
  asking the human, split mixed design+implementation work into separate items with `parent`
  lineage, and route unresolved product/design decisions back to the planning venue with the
  implementation evidence.
- `stage-handoff` now requires each handed-off item to state purpose, completed context,
  remaining problem, success criteria, and the explicit next action, and documents the
  back-routing rule; the machine policy owner moves from canon prose to `settings.json`
  (`stage-work`, `operations/artifacts.md` updated accordingly).

## 0.20.0 — 2026-07-12

Human-readable Stage documents in the user's language (DE-00000003):

- `settings.json` gains `language` (lowercase IETF-style tag, e.g. `en`, `ko`; missing key
  defaults to `en` for full backward compatibility). The audit reports a malformed value
  (`LANG001`) and never attempts semantic language detection; hooks fall open to English.
- `init_stage.py --language <tag>` initializes with bundled locale templates
  (`templates/locales/<tag>/` overlays the canonical English tree file-by-file, English
  fallback) and stamps the tag into the created `settings.json`. Korean (`ko`) is bundled:
  40 translated prose files guarded by a structural parity test (frontmatter keys, backtick
  machine tokens, heading counts, and token-table first cells must match the canonical
  templates).
- SessionStart injects a language directive for non-English projects: human-readable Stage
  content follows the configured language while IDs, paths, frontmatter keys, enum values,
  work kinds, and record section headings stay language-neutral. Record-creation skills need
  no per-skill changes.
- The Stop-hook session summary localizes its labels (`en`, `ko`; unknown tags fall back to
  English).
- Boundary rule: the Stage setting owns `.stage/` document language; host instructions own
  everything outside `.stage/`. Switching the setting affects newly generated content only.

## 0.19.0 — 2026-07-12

Plugin-owned common operations, project-owned policy (DE-00000002):

- Common operational rules (`after`, `artifacts`, `backlog`, `before`, `documentation`,
  `during`, `hooks`, `output`, `portability`, `retrospective`, `review`, and the common
  verification rules) move to the plugin-owned `operations/` directory and are no longer
  copied into consuming projects; initialization now creates `.stage/operations/` with only
  the project-owned `verification.md` (`kind -> passed` criteria table).
- `settings.json` gains `operations_overrides`: the declared list of plugin common docs a
  project intentionally replaces with its own `.stage/operations/<name>`.
- `STAGE_SCHEMA_VERSION` bumps to 2. Hooks stay version-agnostic (they never read
  operations docs); version-dependent behavior lives in the audit and migration.
- The audit gains ownership-drift checks gated to v2 layouts: `OPS001` (byte-identical
  stale copy of a plugin doc), `OPS002` (undeclared differing shadow copy), `OPS003`
  (declared override without a file), `OPS004` (malformed or unknown override declaration).
  The artifact-catalog sync check now reads the plugin-owned catalog when the project
  carries no copy (`CATALOG002` if the plugin copy itself is missing).
- New `scripts/migrate_stage.py` migrates an existing `.stage/` idempotently: deletes
  common-doc copies byte-identical to the plugin's, keeps and reports differing undeclared
  copies (never deletes them), rewrites `verification.md` to the table-only form when its
  prose matches the known legacy template (preserving every project kind row), drops dead
  `index.md` routing rows, and stamps `schema_version: 2` only once no undeclared drift
  remains. `--dry-run` reports without changing files.

## 0.18.0 — 2026-07-12

Optional, field-driven review requirement (design refined with the user; code
red-teamed):

- Work items gain an optional `review` field (`not_required` | `pending` |
  `passed`; absent defaults to `not_required`). Review is bypassed by default — an
  item completes with no review unless it declares one.
- Declaring `review: pending` opts that item in: the completion gate refuses to
  complete it (so a commit of a hand-edited `status: completed` is blocked too)
  until `review: passed`. `close_work.py` runs the configured review only for a
  `pending` item, and sets `passed` when it succeeds — fail-closed if the item is
  pending but its stage configures no command. `register_work.py --review` stamps
  a new item as review-required.
- The PreToolUse enum gate and the audit (`WORK013`) validate the `review` value.
  `operations/review.md` documents the field-driven, opt-in model.
- Behavior change from 0.17.0: the `implementation`-stage review no longer runs on
  every close — it runs only for an item marked `review: pending`. A project that
  wants review on a close must now opt the item in (`register_work.py --review`).
  `register_work --review` warns when no review command is configured yet.

## 0.17.0 — 2026-07-12

Configurable per-stage, per-strength review (design red-teamed before build):

- `.stage/settings.json` gains a `review` block. `strengths` maps each named level
  (`off`, `light`, `standard`, `deep`, `red-team`) to a real, verdict-emitting
  review COMMAND — the harness fixes no command, the project declares it (like
  `venue`). `stages` picks the level per lifecycle stage (`design`,
  `implementation`, `promotion`). Strength is therefore bound to an executable
  review, not a bare label the tooling can't honor.
- `close_work.py` runs the `implementation`-stage review at close (executes the
  command, records its output as evidence, refuses to complete on a failing exit
  or a `BLOCK:` verdict). Fail-closed: a stage set to a strength with no bound
  command, or a typo'd strength, blocks the close until settings are fixed.
- The audit reports an unusable review config as `REVIEW001` (error) and an
  unknown stage as `REVIEW002` (warning); `stage_paths.resolve_review_command`
  is the one owning resolver shared by close_work and the audit.
- `operations/review.md` documents the config; `stage-init`'s settings template
  ships the block with every stage `off` (no behavior change until configured).

Execution scripts and a real field-validity gate (design and code both
red-teamed before landing):

- New `stage/skills/stage-work/register_work.py` — scaffold a work item and its
  `active.md` link-row after the human confirms scope. Ids are allocated with
  `open(…, "x")` (O_EXCL) so two concurrent windows never take the same number;
  re-runs reconcile the index instead of duplicating.
- New `stage/skills/stage-retrospective/close_work.py` — close a work item by
  RUNNING its `--check` commands: `verification: passed` is set only when they
  pass, with their (bounded, fenced) output recorded as evidence — passed becomes
  a byproduct of execution, not a hand-typed claim. Also requires a completed
  retrospective and a FINAL promotion decision (what the commit gate and audit
  demand), and runs checks in the project root. Honest scope: it verifies the
  checks ran, not that they were sufficient.
- New PreToolUse enum-validity gate: a work-item write whose projected
  `status`/`verification`/`retrospective`/`promotion` value is invalid (e.g. the
  `retrospective: not_required` typo) is now blocked at write time, reusing the
  hierarchy projection. The gate and `audit_stage.py` share one owning definition
  of the valid sets (SSOT) in `stage_work.py`.

## 0.15.0 — 2026-07-12

Skill cohesion and triggering:

- `archive_work.py` now lives inside its skill at
  `stage/skills/stage-archive/archive_work.py` — a single-owner script belongs with
  the skill that documents it. Shared infrastructure (`audit_stage.py`,
  `promote_intent.py`, `init_stage.py`) stays in `scripts/` because several skills
  and the hook use it.
- Sharpened the `stage-work`, `stage-archive`, and `stage-handoff` trigger
  descriptions to state a concrete "when" and push against undertriggering.

## 0.14.0 — 2026-07-12

Self-service lifecycle skills so mechanical Stage flows are executed, not
re-derived from hook source each session:

- New `stage-archive` skill and `stage/scripts/archive_work.py` one-shot helper.
  Archiving a completed/rejected item is now a single validated, idempotent
  command (`archive_work.py W-… | --all-completed`) that moves the item and its
  retrospective into `past/work/archive/`, records the terminal status in
  `archive/index.md`, and drops the present-flow rows.
- Clarified the archive contract: archiving passes exactly ONE gate — a per-path
  archive intent. `.stage/` is excluded from `is_source_path`, so the
  registration and commit gates never fire on it and NO new work item is needed
  to archive. New `hooks/tests/test_archive_gate.py` locks this, guarding against
  the false "two gates" belief that once spawned a spurious archive work item.
- New `stage-work` skill: plan the work, confirm scope with the human, then
  register the item and its `active.md` row before touching governed files.
- New `stage-handoff` skill: route open work between LLM windows by `venue`, make
  each item self-carrying, and point the human at the window with open work.
- `stage-retrospective` now delegates archiving to `stage-archive` (SSOT) instead
  of carrying its own archive-intent block.
- Fix: a shell redirection after `git commit` (`2>&1`, `> out`, a piped `| tail`)
  was read as a commit pathspec and produced false registration-gate denials on
  ordinary commit invocations. `git_commit_pathspec_files` now stops argument
  scanning at the first redirection; real `-- path` pathspecs are still caught.
- `operations/verification.md` gains the rule that `verification: passed` records
  evidence produced in the session that sets it — the stated checks actually run,
  not the checks that were merely supposed to run (a recurring retrospective
  learning made durable).
- Clarified the SessionStart context line about `past`: it is gated only by an
  intent naming the completed item being promoted/archived — no new work item —
  since `.stage/` is not governed source. This is the ambiguity that once led a
  session to create a spurious archive work item.

## 0.13.0 — 2026-07-12

Work-item routing for multi-agent projects:

- New optional `venue` frontmatter field on work items names the execution
  surface that should carry out the work — the routing hint a human reads to
  open the right window when more than one agent or session works a project.
  Added to `templates/project-stage/present/work/items/_template.md` and
  surfaced as a `Venue` column in `present/work/active.md`.
- Field is advisory: no hook gates on `venue`, and the frontmatter parser
  already ignores/defaults unknown or absent keys — existing work items and
  `.stage/` instances stay valid with no migration.
- Values are project-defined, like `kind`. `operations/artifacts.md` documents
  the field; `past/canon/vocabulary.md` gains a `Venue` term plus a
  clearly-marked two-surface example `kind -> venue` routing table the project
  replaces. The harness fixes no venue names.

## 0.12.1 — 2026-07-12

Documentation-accuracy pass (no runtime behavior change):

- PostToolUse hook coverage synced across docs: root `README.md`'s Hooks
  section, the project-injected `templates/project-stage/operations/hooks.md`
  (plus its delete-gate wording), and both `docs/BLUEPRINT.md` hook diagrams
  (§10, §15) now include the `PostToolUse` hook shipped in `hooks/hooks.json`
  since 0.12.0.
- Evergreen violation removed from `hooks/README.md`: a past-review-round
  citation ("Codex round-10 review, Low") is dropped from the doc body —
  history belongs in CHANGELOG/commit records, not doc bodies.
- `docs/IMPLEMENTATION_AUDIT.md`: P3's stale "Gap" status is closed (it
  conflicted with P26's own claim of having resolved it), and the conclusion
  now matches the scope actually listed in the 구현된 범위 table instead of
  undercounting it.
- `README.md`/`skills/README.md` skill descriptions had drifted between the
  two files; `skills/README.md` is now the sole canonical wording and
  `README.md` links to it instead of restating.

## 0.12.0 — 2026-07-11

The two items the re-review debate deliberately split out
(`.discuss/stage-review-debate-2026-07-11.md` §분리 항목), each through its
own codex review rounds. **Codex hosts must re-trust the plugin's hooks
(TUI `/hooks`) after upgrading — the hook set changed.**

- Shell WRITE extraction joins delete extraction on the shared command-group
  scaffolding: output redirects and cp/mv/tee/`sed -i` targets are anchored
  at the tracked effective cwd (a preceding `cd` rebases them, fail closed),
  `--` ends option parsing, and redirect classification is quote-aware —
  quoted/escaped `<`/`>` carry sentinels through tokenization, so
  `echo "> src/app.py"` is an argument, `cp x 'src>backup.py'` keeps its
  full destination, a redirect inside a DOUBLE-quoted command substitution
  (`echo "$(printf x > rogue.py)"`) is still gated, and a single-quoted
  literal (`echo '$(...)'`) is not.
- Intent consumption is two-phase (measured: both hosts deliver PostToolUse;
  Codex 0.144.0 includes `tool_response`/`tool_use_id`, also for failing
  commands): the promotion gate's rename reservation is held through tool
  execution and PostToolUse completes it, so a tool crash or a rejected
  permission prompt after the allow no longer burns the authorization. A
  claim whose post never arrives is restored to a pending intent after ten
  minutes (measured from reservation, stamped at claim time); posts consume
  only their OWN claim (tool_use_id/session correlation), and a re-planted
  intent wins over a stale claim — one authorization never becomes two.
- hooks.json: new PostToolUse hook; both tool-use matchers widen to `*` so
  the `extra_write_tools` settings seam (0.11.0) actually fires for names
  the static matcher cannot know. Unknown tools still return the early
  allow.

## 0.11.0 — 2026-07-11

Ten agreed items from the v0.10.0 full re-review debate (Claude self-review ↔
Codex, five rounds, joint sign-off — `.discuss/stage-review-debate-2026-07-11.md`
§R5), in the agreed priority order, plus two mid-batch review rounds.

Gates:

- `extra_write_tools` in `.stage/settings.json`: registered host/MCP
  file-writing tool names are classified before the unknown-name early allow,
  putting them behind the registration/promotion/hierarchy/governance gates
  (content payloads project into the hierarchy gate and dereference symlinks
  like `Write`); a mistyped registration marks settings untrusted. Unregistered
  names remain ungated — now documented in §Limits and the host contract.
- Archive transitions keep their evidence: a present item archives only from
  exactly `completed|rejected` (`archived` is maintenance of archive-located
  records), a rejected item requires its completed retrospective
  (`retrospective_ref`) — rejection reasons are learning assets — and the
  archive-index row (Final status = the state the `archived` overwrite erases)
  lands in the same archive intent.
- The promotion gate validates LAST, so a call denied by any other gate no
  longer burns the pending intent (atomic rename reservation); the remaining
  pre-time window and the one-command re-issue are documented.
- File deletions are gated like writes: `rm`/`del`/`erase`/`Remove-Item`/`ri`
  operands (cwd-anchored, `--`-aware, fail closed across possible anchors) run
  the registration/promotion pipeline. The cwd tracker also follows a cd into
  a directory the same command creates (`mkdir s && cd s && …`) — closing a
  pre-existing delete-gate bypass.

Audit (new findings — existing projects may see new errors; run the audit
after upgrading and close them):

- ARCHIVE001–004: archived items indexed with a terminal Final status,
  completed transitions keep closed gates, every archived item keeps a
  completed retrospective, index rows point at real records.
- BACKLOG008/009, ROADMAP001/002, PROPOSAL001/002: each future family's index
  matches its records in both directions (roadmap theme rows are exempt).
- RETRO002 / DECISION002: reverse links — a completed item's
  `retrospective_ref` is the one binding retrospective, and a recorded
  decision must be linked back from its work item's `decision_refs`.
- BACKLOG007: backlog parent chains must not cycle (same contract as WORK018).
- SCHEMA001 (warning): `.stage/settings.json` `schema_version` missing or
  different from the plugin's contract version (`STAGE_SCHEMA_VERSION`,
  independent of the release version; new harnesses are stamped, preserved
  settings are never overwritten).

Infrastructure:

- Cross-platform CI (`.github/workflows/stage.yml`): both suites, an
  init→audit `--strict` smoke, and the real hook entrypoint on
  ubuntu/macos/windows × python 3.9/3.12.
- One frontmatter→WorkItem constructor with an explicit missing-field policy
  (gate: safe progress / audit: empty), both policies pinned.
- stage-retrospective SKILL archives the index row in the same intent.

## 0.10.0 — 2026-07-11

- P31 record-graph audit: `scripts/stage_records.py` scans every frontmattered
  W/R/DE/B/state record once into typed nodes and reference edges (topology
  documented in one table), and every audit link check reads that graph —
  per-check globbing/re-parsing and cross-method side channels are gone. The
  finding surface (codes, messages, paths, order) is unchanged, held by an
  ordered kitchen-sink pin test plus the per-code suite.

## 0.9.0 — 2026-07-11

- P33 module split: `hooks/stage_guard.py` (3,010 lines) is now a thin
  entrypoint — payload plumbing, tool-gate orchestration, event handlers, and
  facade re-exports (597 lines) — over six sibling modules: `stage_paths`
  (path canonicalization + governance), `stage_shell` (shell tokenization,
  cwd tracking, the `.stage` delete gate, write-path extraction), `stage_git`
  (git invocation parsing), `stage_work` (work-item graph + edit projections),
  `stage_runtime` (`.runtime/` intent slots, session summaries, ack pruning),
  and `stage_context` (SessionStart context assembly). Every module
  self-bootstraps `sys.path`, and `stage_guard` re-exports all
  consumer-referenced symbols, so direct execution (`hooks.json`),
  `import stage_guard`, and file-path loading are unchanged. Behavior is
  identical: both test suites pass on python 3.9 and current, guarded by the
  facade coverage pin (`hooks/tests/test_facade.py`).
- Dead code dropped (no caller anywhere): `_contains_stage`, `git_subcommand`,
  `open_items_for_paths`, `latest_session_summary`.
- Codex hosts: the plugin's hook script set changed — re-approve hook trust
  (TUI `/hooks`) after upgrading.

## 0.8.0 — 2026-07-11

- External-review gate (`operations/review.md`, routed in `index.md`): findings
  from an external review (codex, another agent, a human) are not accepted
  uncritically. The gate anchors on the work's purpose and `past/canon` truth,
  rebuts findings that do not serve the goal, sends the rebuttal back for a
  counter-review, and processes only the survivors — recording what was
  accepted and rebutted. Rebuttal is goal-alignment verification, not
  contrarian nitpicking; when rounds stop converging the remaining edges are
  documented best-effort rather than chased. Injected into every project Stage
  creates.

## 0.7.0 — 2026-07-10

- Hardening from the full-audit design proposals (P28-P35):
  relative_to_workspace resolves existing symlink parents + `..` so a symlink
  into `.stage/past` can no longer dodge the promotion gate; recursive-delete
  detection adds `find .stage -delete`/`-exec rm`; SessionStart injects all
  handoffs tied on the newest mtime; the audit verifies operations/artifacts.md
  and RECORD_LOCATIONS stay in lock-step (CATALOG001); vague operation-doc
  thresholds are replaced with explicit conditions; the instruction inventory
  documents its selected-backlog relevance signal. P31 (record-graph audit) and
  P33 (module split) are deliberately deferred — see docs/IMPLEMENTATION_AUDIT.md.
- Final-entry identity for exact-path gates (Codex round-12 review, 5 findings):
  an entry-canonical form (parents resolved, leaf kept as named) now backs
  `promotes`/intent/archive matching, so a grant for one leaf never covers a
  sibling symlink aliasing the same target; patch projection matches headers
  the same way targets are selected (symlinked work-item leaves cannot slip a
  `parent:` change past the hierarchy gate); the OS-script suffix check is a
  per-form conjunction (`.stage/run.sh -> outside.txt` is still an `.sh` entry
  inside `.stage`); governance prefixes match on both canonical and lexical
  forms (an escaping `exclude_paths` symlink keeps excluding); and a symlinked
  `.stage/settings.json` stays classified stage-internal, so the malformed-
  governance gate cannot deny its own repair. Second pass: find's pre-path
  traversal options (`-H/-L/-P`, BSD `-E/-X/-x/-s/-d/-f`, GNU `-O/-D`) no
  longer hide the start paths from the whole-tree deletion check, and the
  registration/scope matchers include the entry-canonical form so `alias/link`
  (alias -> src) is governed — and authorizable — as the entry `src/link`.
  Third pass: `find -- .stage` (end-of-options separator) is scanned past, and
  a recursive delete rooted at an ANCESTOR of `.stage` (`rm -rf .`,
  `find . -delete` — filtered or not, since the hook cannot evaluate find
  expressions) is denied as deleting the Stage tree. Fourth pass: the resolved
  (leaf-dereferenced) form participates only in fail-closed directions —
  find's `-H/-L/-follow` modes traverse a symlink root, so the link-only
  exemption is dropped there; configured governance exclusions win on the
  entry/lexical forms only (deleting `src/link -> generated/file` acts on the
  governed entry, structural `.stage`/`.git` exclusions still win on any
  form); and scope matching drops the target's leaf-deref form so two leaves
  aliasing one file never cross-authorize. Fifth pass: clustered BSD find
  flags (`find -Lx .stage -delete`) are scanned past (and carry follow mode);
  a preceding `cd` rebases relative delete operands (`cd build &&
  find . -delete` cleans build, not the workspace); and ancestor deletes cover
  the workspace's logical `.stage` entry, so removing the workspace cannot
  silently detach an externally symlinked harness. Sixth pass: the workspace's
  own `.stage` symlink entry is never link-exempt (removing it detaches the
  harness); GNU `find -delete` roots at the implicit `.`; a failed `cd`
  (missing directory) keeps the previous anchor; scope authorization uses the
  entry-canonical form alone (a lexical collapse like `alias/../other/x`
  cannot smuggle authorization); canonical classification is authoritative in
  the delete gate, so a foreign `.stage` basename outside the project
  (`cd build && rm -rf .stage`) is no longer denied by spelling; and find's
  follow mode honors the LAST `-H/-L/-P`. Seventh pass: the cwd tracker keeps
  a SET of possible anchors — a conditionally executed cd (`false && cd build
  ; rm -rf .stage`) adds its state instead of replacing the workspace anchor,
  and any anchor hitting the Stage tree denies; structural exclusions join
  configured ones in winning on entry/lexical forms only, so deleting a
  governed entry whose leaf points into `.git` still requires registration.
  Eighth pass: a pipeline-local cd (`cd build | rm -rf .stage`) keeps the
  caller anchor; bare `cd`/`cd -`/`popd` track HOME and the previous anchor
  set instead of acting as no-ops; and declaration parsing (scope, promotes,
  intent paths) keeps `..` intact so a spelling through a symlink
  (`scope: alias/../other`) canonicalizes to its real entry instead of a
  mis-anchored lexical collapse. Ninth pass: shell control operators are
  tokenized as their own tokens even without whitespace (`true;find .stage
  -delete`) and across newlines/background `&`; a cd through a missing
  intermediate (`cd build/missing/..`) fails like the real shell instead of
  collapsing to `build`; `pushd`/`popd` track a directory stack and `cd -`
  tracks OLDPWD; and find's follow-mode scan skips `-exec` program arguments so
  a `-P` handed to the exec'd program cannot cancel `-L`. Tenth pass: the
  tokenizer runs on the whole command (multiline quotes and backslash
  continuations survive), drops heredoc bodies, and turns unquoted newlines
  into separators; the write scan and cwd conditional both recognize `&`
  (background); the cwd model keeps a failed-cd branch, swaps on bare `pushd`,
  fails a multi-operand `cd`, and treats `cd build & …` as a subshell; the find
  grouper keeps an escaped `\;` exec terminator inside the find group; `find --`
  accepts dash-led roots; and a file-valued symlink scope no longer
  cross-authorizes the distinct target it points at (only directory scopes
  dereference). Eleventh pass: heredoc-body removal is quote-aware (a quoted
  `'<<EOF'` is literal text, not a heredoc); the find `-exec … \;` terminator
  is only honored inside an actual `find` group; and redirections
  (`cd build >/dev/null`) are stripped before counting cd operands. Twelfth
  pass: quoted/escaped `;`/`&`/`|` and fd-redirection `&` (`2>&1`) carry
  sentinels so they never read as separators; `<<` inside `$(( ))` arithmetic
  is not a heredoc; heredoc delimiters keep punctuation (`END-MARKER`) and a
  missing delimiter no longer swallows the rest of the command; and `pushd -n`
  edits only the stack without moving the tracked cwd. Thirteenth pass: a
  failed cd/pushd no longer advances OLDPWD or pushes a phantom stack entry;
  attached `&>`/`&>>` redirections are stripped; leading wrappers (`command`,
  `nohup`, …) and PowerShell cwd verbs (`Set-Location`) are normalized; bare
  `(( … ))` arithmetic suppresses heredoc detection; `cd -- -foo` honors the
  end-of-options marker; heredoc delimiters accept backslash/split quoting
  (`<<\EOF`); and the whole-tree delete gate fires for a strict-ancestor delete
  only when a `.stage` exists (a pre-init workspace is not over-denied).
  Fourteenth pass: the cwd tracker follows bash `cd -L` logical semantics (`..`
  pops a segment lexically so `cd link ; cd ..` returns to link's logical
  parent); a cd into a directory without execute permission fails; `pushd
  +N/-N` rotate the directory stack; PowerShell backtick-escaped separators are
  literals; and a heredoc terminator matches exactly (`<<`) or strips only
  leading tabs (`<<-`), so a space-indented delimiter line stays body.
  Fifteenth pass (representative subset — the rest documented as best-effort):
  a redirection glued to a cd operand (`cd build>/dev/null`) is split off; an
  unknown cd option (`cd -Z`) fails closed; and a CONTENT write (Write/Edit)
  that follows a symlink is governed and scope-matched by the resolved target,
  so a write through `.git/link.py -> src/app.py` or `aliases/link.py` cannot
  modify the governed source outside a work item's scope. Rarely-hand-typed
  shell forms (`cd -P`, `pushd +N`, `nohup cd`, find-predicate-spelled options)
  are left as documented best-effort — see hooks/README.md.
- Over-engineering audit (review-gate lens on the accepted findings): removed
  the `pushd +N/-N` indexed stack rotation (contradicted the round-15 decision
  to leave it best-effort) and dropped `nohup`/`nice`/`time`/`stdbuf` from the
  cd-wrapper set (they cannot run the `cd` builtin, so peeling them was
  fail-open — now their `cd` is a no-op that keeps the caller anchor).

## 0.6.0 — 2026-07-10

- Security/correctness fixes from a full adversarial audit (10 findings):
  lexical `..`/`.` normalization closes registration/promotion/delete bypass;
  multi-target registration requires every path covered (not any); recursive
  delete detection is tokenized (rm -R/--recursive, rmdir /s, Remove-Item
  -Recurse); git commit pathspec is registration-checked; hierarchy is judged
  on the patch's post-state; legacy session-summary migration never drops a
  handoff; audit gains bidirectional lineage (WORK023/BACKLOG006), orphan
  decision/retrospective validation (DECISION001/RETRO001), template file-type
  (TEMPLATE003), and exact routing-row matching.

## 0.5.0 — 2026-07-10

- SessionStart inventories host-project instructions (CLAUDE.md, AGENTS.md,
  .cursorrules, copilot-instructions, .claude/rules and skills) and injects a
  use-and-challenge directive: apply them while planning/executing, and when
  one contradicts observed reality, register an open question with a proposed
  correction instead of silently deviating or obeying. Before/During gates and
  the stage-decision Truth Gate carry the same rule.

## 0.4.0 — 2026-07-10

- Audit: SSOT001 (duplicate record IDs across files), OWN001 (records outside
  their owning catalog location, including body-only heading IDs), ROUTE001/002
  (existing artifact locations and operations documents missing from index.md
  routing). Template index now routes the model record directories.

## 0.3.0 — 2026-07-10

- SessionStart injects the newest three open questions and up to three
  `status: selected` backlog records as bounded one-line entries.

## 0.2.0 — 2026-07-10

- Multi-session `.runtime/`: per-(work item, path) promotion intents consumed
  by atomic rename reservation, per-session Stop handoffs with skew-safe
  pruning, per-session question-gate markers, lazy migration of 0.1.0 slots.

## 0.1.0 — 2026-07-10

- Initial release: `.stage/` artifact structure, init/audit/promote-intent
  CLIs, entry skills, and one hook set enforcing registration, promotion,
  hierarchy, commit, and portability gates on Claude Code and Codex.
