---
id: W-00000013
title: Generate Stage documents in the user's language
kind: feature
venue: claude
source: B-00000002
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000013
promotion: not_applicable
scope: stage, .stage
promotes:
decision_refs: DE-00000003
---

# W-00000013 Generate Stage documents in the user's language

## Purpose

Let each consuming project declare the language of human-readable `.stage/` documents so
Stage-generated content follows the user's language while hooks and audit tools keep parsing a
stable, language-neutral machine contract.

## Scope

- Record the language-setting schema, precedence, and machine/human boundary as a working
  decision before implementation.
- Add a project setting for the human-readable Stage document language with a backward-compatible
  default for projects that lack it.
- Make initialization produce the configured language for human-readable template content while
  keeping IDs, paths, frontmatter keys, enum values, and machine-matched tokens identical.
- Make record-creation skills and session context generation follow the configured language.
- Support at least English and Korean through the same generation contract, guarded by a
  structural parity test between language variants.
- Make the audit report an invalid language setting without semantic language detection.
- Document how explicit host-project language rules interact with the Stage setting.
- Bump the Stage plugin version in both manifests and record the change in the changelog.

## Success criteria

- A project can explicitly configure its human-readable Stage document language.
- Fresh English and Korean initializations produce the requested human-readable language with
  identical machine-readable fields, enum values, and file sets.
- Records generated after initialization follow the configured language via the injected session
  contract.
- Existing projects without the setting keep current behavior; switching the setting affects only
  newly generated content.
- Hooks and audit tools parse English and Korean document bodies without relying on translated
  prose or headings.
- Stage hook and script tests pass, including English, Korean, missing-setting, and
  invalid-setting cases.

## Related truth

- Realizes `B-00000002`.
- Builds on the v2 ownership contract of `DE-00000002` (plugin-owned common rules).

## Progress

- DE-00000003 fixed the language-setting schema, the machine/human boundary, locale overlays,
  and the host-instruction interaction rule before implementation.
- `settings.json` gained `language` (backward-compatible default `en`); the audit reports
  malformed values as `LANG001` without semantic detection; hooks fall open to English.
- `init_stage.py --language` overlays bundled locale templates over the canonical English tree
  and stamps the tag; Korean shipped as 40 translated prose files.
- A structural parity test pins every locale file to its canonical counterpart (frontmatter keys,
  backtick tokens, heading counts, token-table first cells, audit markers).
- SessionStart injects the generation directive for non-English projects; the Stop-hook session
  summary localizes its labels (`en`, `ko`).
- Docs, stage-init skill, changelog, and both manifests updated. Released as 0.20.0.

## Verification

Executed this session:

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 263 tests in 0.516s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 135 tests in 3.802s

OK
```

## Retrospective

See `R-00000013` in `work/retrospectives/`.

## Promotion decision

`promotion: not_applicable` — all changes live in the `stage/` plugin; no `official/` artifact of
this repository changes (this repository keeps its explicit English setting).
