# Work Items

This directory owns the SSOT of in-progress work hierarchies.

An epic directory contains `_epic.md` plus story directories. A story directory contains
`_story.md` plus action cards. An independent story may be top-level; an action may not.

## Rules

- Folder placement is the only hierarchy fact; work frontmatter has no `parent` field.
- One top-level epic or independent story moves through lifecycle locations as a whole.
- `work/active.md` and `work/review.md` are current views and never duplicate bodies.
- When work becomes a completion candidate, link its verification, retrospective, and promotion decision.
- Hooks use each work file's frontmatter as the status SSOT.
- When work no longer belongs to the current flow, set `status: archived` and move it to `official/work/archive/items/`.

## Status fields

The document SSOT of the work status enum is `operations/artifacts.md`.

- `kind`: what kind of work this is (for example `planning`, `design`, `development`, `qa`, `ops`). The project defines its own taxonomy in `official/canon/vocabulary.md`.
- `venue`: optional. Which execution surface should carry out this work item — the routing signal a human reads to open the right window when more than one agent or session works the project. Values are project-defined: the machine-readable `kind -> venue` routing lives in `settings.json` `venue_routing` (registration derives the venue from it and the audit checks consistency; exceptions need a decision record with `authorizes: venue_exception`), while `official/canon/vocabulary.md` owns what each venue means. No hook gates on `venue`; with no declared routing it is a purely advisory per-item field. An empty value means unassigned.
- `scope`: paths this work owns. Separate multiple entries with commas. An empty value owns no path. Declare `*` only for a truly global scope.
- `promotes`: `.stage/official/` paths this work may promote. Separate multiple entries with commas.
- `retrospective_ref`: the retrospective file ID or path linked when `retrospective: completed`.
- `decision_refs`: optional decision record IDs or paths in `decisions/pending/`.
- `source`: optional historical source reference.
