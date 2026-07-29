---
id: W-00000007
title: Stage skill system — co-locate single-owner scripts, sharpen triggers; audit-enforcement deferred
kind: feature
venue: claude
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000007
promotion: not_applicable
scope: stage/hooks, stage/scripts, stage/skills, stage/docs, stage/templates, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000007 Stage skill system — cohesion, triggering, and a deferred enforcement finding

## Purpose

Two threads came out of the "make execution the source of truth" discussion and the skill-cohesion
question:

1. A skill's single-owner script should live inside the skill, not in a shared `scripts/` bin, so
   the skill is self-contained. Shared infrastructure (audit, promote_intent, init) stays in
   `scripts/` because multiple skills and the hook use it.
2. The skill trigger descriptions should reliably fire in their Stage contexts.

An enforcement idea — run the audit in the Stop hook so a broken `.stage/` can't end a session —
was tried and DEFERRED: running the audit subprocess inside `handle_stop` is invasive (it changed
the hook's return contract and broke `test_stop_writes_summary_and_allows_handoff_with_open_work`).
A non-invasive design (e.g. a PostToolUse structural check on `present/work` index writes) is the
right approach and is left for a separate item.

## Scope

- Move `archive_work.py` into `stage/skills/stage-archive/` (single-owner). Update the skill and
  its central test path.
- Sharpen the `stage-work`, `stage-archive`, `stage-handoff` trigger descriptions.
- Version bump + CHANGELOG.

## Success criteria

- `archive_work.py` lives beside its skill; `stage/scripts/tests` still pass via one discovery run.
- The three skill descriptions state a concrete "when" and are pushier against undertriggering.
- Both manifests bumped; CHANGELOG updated.

## Findings

- Skill triggering could not be validated by `skill-creator`'s `run_eval` in this environment: it
  returned a 0.0 trigger rate for every query including unmistakable matches (at 30s and 120s
  timeouts). Its mechanism (a synthetic slash-command watched for a `Skill` tool call in a bare
  `claude -p`) does not reproduce how an installed plugin skill surfaces, so the result is not a
  trustworthy signal. Real triggering validation needs an actual plugin-installed session.
- Stop-hook audit enforcement is too invasive (see Purpose); deferred.

## Verification

- `python3 -m unittest discover -s stage/hooks/tests -q` — 240 tests OK.
- `python3 -m unittest discover -s stage/scripts/tests -q` — 89 tests OK (archive test runs against
  the co-located script path).
- `python3 stage/scripts/audit_stage.py` — errors=0, warnings=0.

## Retrospective

See [R-00000007](../retrospectives/R-00000007.md). Co-located the single-owner archive script;
treated `run_eval`'s uniform 0.0 as an untrustworthy signal rather than a skill defect; deferred the
invasive Stop-hook audit enforcement.

## Promotion decision

`promotion: not_applicable` — changes live in the `stage/` plugin package.
