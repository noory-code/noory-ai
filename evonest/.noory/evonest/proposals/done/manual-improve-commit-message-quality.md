# Proposal: improve commit message quality in run_improve()

**Priority**: medium  
**From persona**: manual  
**Cycle**: 0  
**Status**: pending review

## Description

Currently `verify.commit_message` falls back to "evolve: auto-improvement
(cycle 0)" when Claude does not produce a meaningful commit message. This
results in uninformative commit history when running `evonest improve`.

The fix should either:
1. Instruct the execute prompt to always produce a descriptive English
   commit message summarizing what was actually changed, OR
2. Fall back to a slug derived from the proposal title (translated to
   English via the execute phase language instruction)

## Relevant Files

- src/evonest/core/improve.py — _commit_message_from_proposal(), run_improve()
- src/evonest/prompts/execute.md — add explicit commit message instruction

---

*This is a design-level proposal. No code was changed.*  
*Review, reject, or act on this as the team sees fit.*
