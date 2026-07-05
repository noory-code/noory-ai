# Flow Core Rules

**Core rules that the Flow engine and every implementation teammate follows.** (A general-purpose planner engine — work-type based. Expert teammate definitions are supplied as SSOT by the project under `.claude/agents/`. No orchestration middle layer — the main session does it directly.)

> Plugin `rules/` SSOT → once `flow-config` syncs them into `.claude/rules/`, every session auto-loads them. Detailed procedures = the flow-* skills under the plugin's skills/.

---

## Hook-enforced rules (PreToolUse — settings.json trigger + hooks/hook_pre_tool_validate.py unified enforcement)

> A single PreToolUse hook branches through 12-rule validation (Rule 1·2·3·5·6·7·8·9·10·11·12·13 — 4 is a historically vacated number; per-environment tool-name aliases supported). Path rules (R1/R6) check the **workspace_root-relative path** — a repo clone location containing `/apps/` etc. causes no false-positive block. **hook = the non-bypassable layer** (even an explicit user bypass is impossible — `gate-enforcement-default-on`). Hook-code docstring = `flow/hooks/hook_pre_tool_validate.py`.

| Rule | Block condition | Action |
|----|----------|------|
| **no-action-without-doc** (R1) | Modifying source-directory code (apps/packages/plugins/lib/src etc.) with an active Epic but no A-NNN.md | deny |
| **no-commit-without-retro** (R2) | `git commit` while the in-progress Action's retrospective section is empty | deny |
| **no-push-workspace** (R3) | `git push` includes `.flow/workspace` files | ask |
| **no-story-without-action-doc** (R6) | Modifying a non-SSOT file (skill/rule/source) while the active Story has zero A-*.md (even meta work requires an A-NNN.md up front) | deny |
| **no-merge-without-review** (R7) | Merging a Story whose Actions are all ✅ without a review/evaluation record in `_story.md` ("cannot merge without review/evaluation") | deny |
| **no-work-without-playbook** (R8) | In the execution stage but `_epic.md` has no `**playbook**` field (the Planning window = zero Actions is an exception) | deny |
| **no-node-without-purpose** (R9) | A node SSOT (`_initiative`/`_epic`/`_story`/`A-NNN.md`) newly created (Write/full replace) without restating `**Ultimate Purpose**` (Edit excluded) | deny |
| **no-shell-node-write** (R10) | Creating/modifying a node via shell redirection (`>`/`>>`/`tee`) (bypasses the node gate — best-effort) | deny |
| **no-finish-without-archive** (R11) | A completed (✅) item whose `archives/retro-<name>.md` has not been extracted, yet a PR (`gh pr create`) / shared merge / push is attempted (**global** — a single un-archived item blocks even an unrelated PR) | deny |
| **no-action-without-depends-on** (R12) | (hook-enforced — see docstring) | deny |
| **fan-out-attempt-mandatory** (R13) | Missing fan-out attempt during Story execution (AT on) | deny |
| **load-skill-on-phase** | (SessionStart) auto-injects the active Epic/Story/Action state | additionalContext |

### Hook rule boundaries

- **R6 — finish-stage meta work is no exception**: the archive step and rule/skill/hook propagation edits of epic/initiative-finish also trip R1/R6 — **intended** (a finish exception in the hook would open a gate-bypass channel). Wrap such work in a **lightweight "propagation Action"**: an A-NNN.md carrying only `**Ultimate Purpose**` + `depends_on`. Never add a finish exception to the hook code.
- **R7 scope**: the gate enforces only whether review/evaluation *was executed*; what/how to review is declared by the playbook (`flow-procedure-story` §7-2). Concrete review is delegated to the project's review teammate/skill; if absent, the main reviews directly per the playbook criteria.
- **R8 mechanics**: the playbook is selected by `flow-playbook-selection` in Plan Mode and recorded in the `_epic.md` `**playbook**` field. Enforced only in the execution stage (0 Action docs = still Planning → passes).
- **R9 rationale/boundary**: enforces design-time purpose propagation from top (Initiative/Epic) to floor (Story/Action); the **precondition** of the purpose-anchoring rule (runtime derivation) — complementary, not duplicate. Independent of whether an epic exists; Edit excluded to avoid false positives.
- **R10 boundary**: perfect blocking is impossible — only `>`/`>>`/`tee` + node-path combinations are caught. Write nodes with the Write/Edit tools.
- **R11 boundaries**:
  - Enforcement target = only the existence of `archives/retro-<name>.md` (retrospective extraction/consolidation). The git commit is procedure-enforced; preserving vs deleting the workspace original stays the user's choice (`flow-archive`).
  - Judgment: the top SSOT node of the top workspace unit (`_initiative` > `_epic` > `_story`) is ✅ + `archives/retro-<name>.md` absent → unarchived. Parity with `flow-completion` § upper-integration Hard Gate / `flow-archive`.
  - **Global scope = decided; do not re-litigate without data** (Epic epic-retro-enforce US-004): even an *unrelated* PR/merge is blocked — enforces "don't pile up completed items; archive immediately". Resolution = extract that item's retro into `archives/retro-<name>.md` + commit (low-cost, never a deadlock).
  - Detection limit (best-effort): only `gh pr create` / `gh api ...pulls` / direct push/merge on a shared branch. Web-UI PRs, auto-PRs, and MCP GitHub tools go undetected.
- **R13 exemption**: fan-out is the main session's responsibility — the hook detects a teammate session via input JSON `agent_id` (absent = main / present = subagent) and passes subagents.

---

## Text rules (not hook-enforced — enforced by default via `gate-enforcement-default-on`; arbitrary AI bypass forbidden)

### gate-enforcement-default-on (CRITICAL meta rule)
**Every Gate/Rule/Hard Gate is enforced by default (default on). Arbitrary AI bypass is forbidden.**
- **Default behavior**: every Gate/checklist/Hard Gate in a rule or procedure must be executed, never skipped. "It's simple / to save time / just this once" — not accepted as bypass grounds. The AI must not decide on its own that "this Gate is unnecessary this time".
- **Bypass = only explicit user phrasing**: skip · move on / let's move on / go past it · bypass · skip over / let's skip over · omit just this once · just proceed.
- **Insufficient (not a bypass)**: ❌ OK / yes / yeah (mere agreement) · ❌ hurry / it's urgent (time pressure) · ❌ AI-inferred intent.
- **When bypassing**, output:
  ```
  ⚠️ Bypass: [Gate name] ([procedure-doc path])
  Reason: explicit user request
  Expected risk: [the failure type this Gate was blocking]
  ```
  Record any failure after a bypass in the retrospective Problem section. Bypassing one Gate ≠ automatic bypass of the next — each Gate needs its own explicit bypass; a blanket "skip everything" requires the AI to output the full bypass list for user re-confirmation.
- **Scope**: Hook = non-bypassable (system-enforced) / Hard Gate & ordinary text rules = bypassable (procedure above) / all procedure steps including Assumption, AI Review, Pre-flight.
- **Violation cases**: ❌ "Discovery result is obvious, so skip the Assumption Gate" (self-judgment) · ❌ "Tests passed, so skip the code-reviewer" (removing a procedure step) · ❌ reading an "OK" reply as bypass consent.

### no-hook-equivalence
No hook block ≠ rule compliance — hooks enforce only partially (verification-scope limit). Directly verify the rule documents' explicit provisions + skill Hard Gates, loading the rule with Read before work. Correct thinking = "OK only when the hook scope + the rule's own verification + the Hard Gate `ls` verification all pass". E.g., in an active Story, confirm A-NNN.md existence with `ls .flow/workspace/epic-*/US-*/A-*.md` regardless of the hook.

### preflight-gate-enforcement
Just before entering a Phase, the Pre-flight 4 axes (directory / Persona / branch / Asset) must run automatically — emit a self-check checklist; zero runs is forbidden. Entry points: `story-planning` (flow-planning-story § Pre-flight), `action-planning` (flow-planning-action Discovery §0), `action-execute` (flow-procedure-action Step 0). On pass → next Phase; on non-pass → report to user + enter only after a decision. Violation impact: work on a fake SSOT / non-standard persona infiltration / wrong branch / guesswork.

### no-auto-proceed
Do not auto-advance to the next Action/Story/Epic without user confirmation. Do not move on with only a completion report. On an affirmative reply, execute only the single task that was asked about.

### no-write-without-plan
Do not call write tools (create / modify / commit / merge) without Planning (common to all levels; no arbitrary omission). Research / analysis / proposals are free. **Approval of a design proposal ≠ permission to start implementation** — direction approval only; even an approved design must not write without first producing that level's Planning artifact (A-NNN.md / `_story.md` Action breakdown, etc.). Enforcement = the planning-artifact hooks (no-action-without-doc · no-work-without-playbook · no-node-without-purpose). (Absorbs the deprecated `plan-mode-enforcement` rule.)

### fan-out-attempt-mandatory
On entering Story execution, a fan-out attempt is mandatory: analyze each Action's `depends_on` → identify independent Actions → attempt `Flow.parallel` parallel spawn (`flow-procedure-story` Step 6). Backed by hook R13.
- **AT on** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) = enforced; bypass only via explicit user expression. **AT off** = the hook passes automatically — parallelizing via parallel subagents is still the recommended default; serial is the exception (dependency-serial waves, explicit disable); non-Claude tools have no AT env and use their own parallel mechanism.
- **Silent fallback allowed**: spawn attempt fails → the main takes over, not blocked — work must keep rolling.
- **Main-session only**: fan-out is the main's responsibility (subagent-deployment-timing (b)/(c)); teammate sessions are exempt (hook `agent_id` detection).
- Violation impact: lost parallel opportunity / executing without grasping the dependency-graph structure.

### no-direct-handoff-exec
The Flow must not directly execute an Action that specifies `delegate_to` (= the specialist teammate for the Action's main work; concrete names defined in the project's `.claude/agents/` — detail: `handoff.md`). The main assigns that teammate (handoff-protocol §3.1/§3.2) and **does not write code directly**. Even a user's "just implement it yourself" — the Protocol takes precedence (explicit bypass per `gate-enforcement-default-on`). `delegate_to: (direct)` = the main performs it directly (meta work). Can be forced via `delegation_mode` (`auto` default / `subagent` / `direct`).

### subagent-deployment-timing
4 teammate-deployment-timing principles (body SSOT = handoff-protocol §3.4; (a)(b)(c) absolutely enforced, (d) signal-based — no separate bypass):

| # | Principle | Meaning |
|:-:|------|------|
| (a) | **Epic Planning = main's responsibility** | Epic analysis / Story outline breakdown / user confirmation is main + user conversation. No teammate assignment. |
| (b) | **Story Planning (Action breakdown) + orchestration = main's responsibility** | Action-breakdown draft, finalization, and user confirmation are the main's; then the main assigns specialists per the playbook procedure. |
| (c) | **Main orchestrates up to the PR (Epic cycle)** | The main executes all Stories + Actions + retrospective + Squash Merge + PR within the Epic (specialists = Action execution only). |
| (d) | **User confirmation = important decision points** | Default autonomous. On a big decision (shared-branch merge / non-goal change / directory deletion / Epic entry) or undecidable ambiguity → return to the main + call the user. |

### no-shared-branch-merge
Merge/rebase/push to a shared branch (`develop`/`main`/`master`/`release/*` etc.) only on the user's explicit direct instruction — never by AI judgment or a "Story is done, so merge" auto-proceed. On Epic/Story completion, always ask about merging + wait for the reply. Story branch → Epic branch Squash Merge is auto-allowed (an Epic branch is not shared). Violation impact: shared-code contamination, impact on other workers, hard reverts.

### no-debate-without-record
`debate-protocol` discussion outputs are recorded to the SSOT the moment they settle: Phase A discovery list / Phase B integration proposal → `_story.md` (or `_debate.md`) `## debate record`; Phase C per-issue conclusion → immediately after each issue closes (not batched). Completing the previous Phase's record before entering the next Phase is a Hard Gate.

### ssot-write-only
The source of work-item state = only `_epic.md`/`_story.md`/`A-NNN.md`. A state change modifies only these files. A Read is required when referencing them elsewhere.

### no-code-change-without-doc-sync
A code/asset port/change Action pre-measures the documentation-impact baseline (`grep` at Planning/Discovery time → reflected in the Action-scope estimate) + syncs the affected docs (README/DESIGN/manual/config comments) within the same Action scope, with the accompanying doc update in the AC (do not assume a single file — `grep` search). If zero, record "no doc impact (baseline 0)". Verification: `grep -rn "<identifier|old path>"` across docs → confirm 0 stale references. **Deletion/migration is also a change** — scan all referencing docs even when deleting a file. Violation impact: a follow-up worker/AI trusts a stale doc → wrong path / deleted feature.

### no-defer-blockers
A discovered blocker must not be handed off to the next unit (Action/Story/Epic). Blocker = any of: ① blocks this Action/Story itself (hook deny, permission block, missing dependency) ② directly damages a follow-up unit's evaluation/verification quality (missing required tool, broken SSOT parity) ③ a High retrospective-Try item that is a prerequisite of a follow-up Story. Handling paths:
- **Fix immediately** — within this Action's scope: bundle in the main commit + record in retrospective Problem
- **Side commit** — outside scope but separable: separate `[side][scope]` commit on the same branch
- **Retrospective handoff** — non-blocker: record as a Try item, handle in a batch at Epic wrap-up
- **Explicit user handoff** — not self-resolvable (external policy/tool, Epic non-goal conflict): request an explicit user decision

Epic non-goal conflict: defect reinforcement is allowed only after explicit user agreement — the AI reports the conflict + a defect classification → the user decides (immediate / separate Story / hand off) → record in the Action retrospective + the `_epic.md` non-goal section. Detail: flow-issue-handling.

### skill-trigger-obligation
When a skill's description matches the user message (question or command form alike, mere mention included), calling the Skill tool is mandatory — no bypass via direct Bash calls (`gh pr create`, `git ...`), no "efficiency/simplification" skips, no reading an interrogative as a weak signal. Self-check before work: ① work-area keyword (PR/retrospective/refactoring/build, etc.)? ② grep the matching skill description ③ match → Skill tool obligatory ④ none → direct call OK. Bypass only via explicit phrasing ("without the skill" / "directly"). Violation impact: bypassing the skill's standard procedure → non-standard deliverable + post-hoc cleanup (case: direct `gh pr create` violated the `flow-pr` standard → cleanup PR).

### retro-evolution (cross-ref → the retro-evolution rule)
Retrospective accumulation + independent application (`retro-processing` — independent of the flow unit; human-triggered + reviewed). 5-way classification / extract-and-consolidate on archive / TaskCompleted hook = accumulation guarantee. Blocks automatic coupling of retrospective reflection to the flow (independent · human-controlled). Procedure SSOT: `flow-retrospective` Part 3 + `playbooks/retro-processing.md`.

### purpose-anchoring (cross-ref → the purpose-anchoring rule)
Before asking the user for a decision: ① Read the `**Ultimate Purpose**` of the entry-scope top node (`_initiative.md`/`_epic.md`/`_story.md` — go to the real essence, not just the hierarchy top) ② try to derive the answer from the purpose + child SSOT ③ ask only when derivation is impossible. Blocks unnecessarily asking back at large scale by missing the upper essence. Boundary-distinguished from `no-auto-proceed` (checkpoint preservation). Purpose-chain source: `flow-scale-judgment` §ultimate-purpose interview.
