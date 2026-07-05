# rules/

Flow text rules (always loaded — distinct from playbooks).

- Flow rule = always applied (common to all work) ↔ playbook = one selected per work item

## File layout

| File | Role |
|------|------|
| `flow-rules.md` | 12 hook-enforced rules (Rule 1·2·3·5·6·7·8·9·10·11·12·13 — no rule 4, a historically vacated number) + the text rules (`gate-enforcement-default-on`, etc.) — the core source |
| `commit.md` | Atomic commit criteria |
| `directory-standard.md` | Workspace path standard (`.flow/workspace/`) |
| `handoff.md` | Delegation (`delegate_to`)·teammate-assignment enforcement signal |
| `personas.md` | Persona SSOT |
| `retro-evolution.md` | Retrospective Try → evolution loop enforcement |
| `ssot-vocabulary.md` | SSOT standard vocabulary |
| `tool-usage.md` | Tool-first (dedicated tool > general shell) |
| `decision-criteria-first.md` | The 4-way distinction gate before asking — just before escalating, distinguish (d) data-shortage/(c) application-ambiguity/(b) criteria-conflict/(a) criteria-absence (the entry point for asking) |
| `purpose-anchoring.md` | Purpose anchoring — the gate to derive the answer from the ultimate purpose before asking the user (the detail of the (c) branch of `decision-criteria-first`) |
| `verify-before-assert.md` | Ground-truth inspection before asserting — verify with tools before stating unverified facts |

> Each rule file is self-contained (core + compressed detail in one file). Older plugin versions shipped a separate `rule-details/` tier; it was merged into `rules/` and the split no longer exists.
