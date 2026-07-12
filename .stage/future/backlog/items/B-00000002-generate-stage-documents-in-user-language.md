---
id: B-00000002
title: Generate Stage documents in the user's language
kind: feature
parent:
status: triaged
priority:
realized_by:
---

# B-00000002 Generate Stage documents in the user's language

## Purpose

Let each consuming project declare the language used for human-readable `.stage/` documents so
Stage-generated context follows the user's language without changing machine-readable contracts.

## Source

User request after confirming that Stage currently copies English templates and has no language or
locale setting.

## User value

Users can read, review, and maintain Stage work items, decisions, questions, retrospectives, and
summaries in their own language while hooks and audit tools continue to parse a stable contract.

## Scope

### Included

- Add an explicit project setting for the human-readable Stage document language.
- Define precedence between an explicit project setting, initialization input, and the default
  language.
- Make Stage initialization and record-creation skills use the configured language for titles,
  headings, prose bodies, generated index labels, and session summaries.
- Keep IDs, paths, frontmatter keys, enum values, schema keys, commands, and other machine-readable
  tokens stable and language-neutral.
- Support at least English and Korean through the same generation contract.
- Define backward-compatible behavior for existing projects with no language setting.
- Update initialization, context generation, skills, documentation, audit coverage, and tests.
- Document how an explicit host-project language rule interacts with the Stage language setting.

### Excluded

- Translating source code identifiers, artifact IDs, paths, frontmatter keys, or status values.
- Automatically translating user-authored historical records without an explicit migration action.
- Using unreliable natural-language detection as a completion or audit gate.
- Changing the repository-wide language policy of the Stage plugin source itself.

## Dependencies

- Coordinate with B-00000001 because removing copied common operations changes which `.stage/`
  documents still need localized generation.
- Decide the setting name and language identifier format before implementation.
- Decide whether explicit host-project instructions override, populate, or conflict with the Stage
  language setting.

## Risks

- Translating headings that scripts or skills currently match as literal text could break parsing.
- Inferring a language from one conversation may not represent the project's durable preference.
- Duplicated per-language templates could recreate the SSOT and drift problem.
- Existing projects may contain mixed-language records and need an explicit migration boundary.
- This repository currently requires executable artifacts to be English, so its local setting must
  not silently contradict the host instruction.

## Verification criteria

- A project can explicitly configure its human-readable Stage document language.
- Fresh English and Korean initializations produce the requested human-readable language while
  preserving identical machine-readable fields and enum values.
- Work items, backlog items, decisions, questions, retrospectives, indexes, and session summaries
  generated after initialization follow the configured language.
- Existing projects without the setting retain backward-compatible behavior.
- Switching the setting affects newly generated content without silently rewriting historical
  user-authored records.
- Hooks and audit tools parse English and Korean document bodies without relying on translated
  prose or headings.
- Stage hook and script tests pass, including English, Korean, missing-setting, and invalid-setting
  cases.
- The audit reports an invalid language setting without attempting unreliable semantic language
  detection.

## Next action

After B-00000001 defines the project-policy surface, decide the language-setting schema and
generation boundary, then select this item and create its realizing work item.
