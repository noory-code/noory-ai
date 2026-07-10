# Changelog

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
