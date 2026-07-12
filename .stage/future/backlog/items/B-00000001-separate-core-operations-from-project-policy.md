---
id: B-00000001
title: Separate Stage core operations from project policy
kind: feature
parent:
status: triaged
priority:
realized_by:
---

# B-00000001 Separate Stage core operations from project policy

## Purpose

Make the Stage plugin the single owner of common operational rules while project-local `.stage/`
files own only project-specific policy, overrides, and runtime records.

## Source

User-requested follow-up to the repository analysis that compared all 12 files under
`stage/templates/project-stage/operations/` with this project's `.stage/operations/`.

## User value

Projects can upgrade Stage without carrying duplicated common policy, silently retaining stale
rules, or losing project-specific verification criteria during a forced template refresh.

## Scope

### Included

- Define and record the ownership boundary between plugin-owned core operations and
  project-owned policy.
- Move common lifecycle, artifact, hook, review, retrospective, portability, documentation, and
  output defaults to one plugin-owned location.
- Define a minimal project policy surface for work-kind verification criteria, venues,
  governance exclusions, and explicit overrides.
- Separate common verification rules from project-specific `kind -> passed` criteria.
- Update initialization, audit, context injection, skills, templates, documentation, and tests to
  use the new ownership model.
- Add a migration path for existing `.stage/operations/` directories without overwriting
  project-specific policy.
- Migrate this repository's `.stage/` and resolve the current `venue` contract drift.

### Excluded

- Changing the meanings of `past`, `present`, or `future`.
- Changing the work completion requirement of verification plus retrospective plus promotion
  decision.
- Replacing Markdown and plain-file project records with a service or database.

## Dependencies

- Complete or otherwise close W-00000007 before implementation because its scope overlaps
  `stage/hooks`, `stage/scripts`, `stage/skills`, `stage/docs`, and `stage/templates`.
- Record the common-versus-project policy ownership boundary as a working decision before
  implementation.
- Define backward compatibility for projects initialized by older Stage plugin versions.

## Risks

- Existing projects may contain intentional edits mixed with copied common policy.
- A forced migration could destroy project-specific verification criteria or output rules.
- Resolving policy from the installed plugin may make behavior depend on plugin version unless
  the effective contract version is explicit and auditable.
- Host differences between Codex and Claude could reintroduce duplicated adapter rules.

## Verification criteria

- A fresh Stage initialization does not copy identical common operational rules into the
  consuming project.
- Project-local policy contains only declared project values or explicit overrides.
- Existing project-specific verification kinds survive migration without manual reconstruction.
- The audit detects unsupported policy versions, malformed overrides, and unresolved ownership
  drift.
- The effective rules used by hooks, scripts, skills, and documentation resolve from one common
  owner plus project overrides.
- This repository's `venue` values and `kind -> venue` routing have one declared project owner.
- Stage hook and script unit tests pass on the supported Python and host contracts.
- The migrated repository passes `audit_stage.py` with zero errors and zero warnings.

## Next action

After W-00000007 closes, select this backlog item, create its realizing work item, and record the
policy ownership/interface decision before modifying Stage implementation files.
