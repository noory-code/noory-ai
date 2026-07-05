# Action decomposition detailed criteria

The detailed criteria for Action decomposition in the `flow-planning-story` Draft stage. The main body (SKILL.md) keeps only the core merge/split judgment; load and reference the detailed criteria below when decomposing Actions.

> SSOT: this file is a reference of `flow-planning-story`. It is the single source of the Action-decomposition criteria, and the main body points to this file as a pointer.

## Change-batch criteria (organize/migration/migration-type Epics)

Splitting Actions per deliverable category (source / test / resource) makes each Action perform the same verification redundantly. Decompose Epics of this nature by "change batch" (a bundle of related changes) instead.

| Criterion | Existing (category decomposition) | Improved (change batch) |
|------|---------------------|------------------|
| **Decomposition unit** | source / test / resource | commit group (bundle of related changes) |
| **Verification unit** | per category | whole per feature |

**Judgment criteria**:
- [ ] If organize/migration in nature, prefer "change batch"
- [ ] If a general feature Epic, prefer "work type / teammate"
- [ ] Change batch = grouping by commit topic

## Simple module-integration criteria

When both design and implementation are simple, consider integrating into 1 Action:

| Condition | Integrate | Keep split |
|------|------|----------|
| Deliverable files ≤ 3 | ✅ | |
| External references ≤ 1 place | ✅ | |
| Structure change only (large edits deferred) | ✅ | |
| Deliverable files > 5 | | ✅ |
| External references > 3 places | | ✅ |
| Includes a large structural edit | | ✅ |

## 1:1 wrapper Action integration criteria

An Action that simply wraps an existing deliverable is not split out but integrated:

| Pattern | Judgment | Reason |
|------|------|------|
| A wrapper that merely wraps an existing deliverable | Integrate | Splitting into an independent Action only adds overhead |
| Wrapper + extra logic (state, event handling) | Split | Needs separate testing/verification |

## Minimal-change-scope-first principle

When decomposing Actions, first identify the minimal change unit, then decompose. Do not assume a large scope from the start.

| Item | Recommended | Avoid |
|------|------|------|
| Files changed in 1 Action | ≤ 3 (surgical) | ≥ 10 (scope explosion) |
| Extra deliverables (expected outside scope) | Handle as non-goal via an explicit "Scope Out" | Unplanned expansion |
| The "better way" impulse | Conflicts with the Story non-goal → promote to a separate Action/Story | Absorbing non-goal work inside the Action |

**Checklist**:
- [ ] Identify the "minimal change unit" in the Discovery stage (grep + Read impact scope)
- [ ] Proceed from "minimal change" when decomposing Actions → expand incrementally if insufficient
- [ ] On finding a "better pattern", promote it to a separate Action (keep the current Action's scope)

## AC of a guide-work Story = "auto-discovery verification"

The AC of a Story that works on flow resources (guides/rules/docs) is defined in "auto-discovery verification" form.

**Auto-discovery verification**: the AC can be auto-verified with a `grep` / `ls` / `find` command. No manual user confirmation needed.

| AC type | Recommended (auto-discovery) | Avoid (manual confirmation) |
|---------|---------------|---------------|
| Rule addition | `grep "keyword" <target file>` ≥ N | "the rule is clear" (subjective) |
| New doc creation | `ls <target path>` exists | "the doc is appropriate" (subjective) |
| Persona parity | `grep "As a"` cross-check against the SSOT table | "the persona is natural" (subjective) |
| Retrospective marker | `grep -c "✅ reflected"` ≥ N | "the marker is appropriate" (subjective) |
