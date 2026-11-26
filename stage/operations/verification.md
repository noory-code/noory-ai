# Verification

This document owns the common verification rules for every Stage project.

Project-specific `kind -> passed` criteria are project policy and live in the consuming
project's `.stage/operations/verification.md`.

## Rules

- Both external-perspective and internal-perspective completion are required.
- Tests or equivalent verification must match the change.
- If the project declares a linter or formatter (a config file or a documented command exists), it must pass; if none is declared, this criterion is skipped.
- New behavior needs a verification path.
- A card that changes a procedure a session follows, or writes a new path that other sessions
  will follow, closes only after real work was done once along that path. A fresh session that
  was given only a new skill found eleven gaps in it, and eight more in a second trial; a review
  that reads the document would have found none of them (R-00000404). Two close documents
  blocked each other, and nobody knew until the first card went through them (R-00000418). No
  session had run under the new briefs when their card closed (R-00000420).
  (R-00000404, R-00000418, R-00000420)

  ```yaml
  trial_before_close:
    applies_when:
      - the card adds or changes steps a session walks: a procedure in an `operations/` document
        or a skill, or a brief a script prints
      - or the card writes a new path that other sessions will follow
    does_not_apply_when:
      - the card adds or amends one rule sentence and no step to walk: there is no path to try.
        The five cards that each added one rule sentence beside this one are of this kind
        (W-00000425 to W-00000429).
    at_registration:
      - the card carries a success criterion that names the real work done once along the
        changed path, for example "one real card was closed by the changed close path", "one
        fresh session that was given only the document followed it", or "one real session ran
        under the new brief"
    evidence:
      - one line for that criterion on the card's `## Verification` — a `- Observed` line of a
        verify session (`stage-orchestrate`, "Start a verify session", owns its form) or a
        `- Checked` line (`operations/review.md`, "A check recorded on the card", owns its form)
    not_the_trial:
      - a test that pins the document's sentences or a script's refusals
      - a review that reads the document
    until_the_line_exists: the card stays open
    when_the_trial_can_run_only_after_the_merge:
      - if: the first real use of the path comes after this card's change is merged (a changed
          close procedure whose first real use is the next card's close; a new brief that only
          the next session receives)
        then: the code may merge while the card stays open, by `operations/cloud-execution.md`,
          "Merge a card that waits for the user's machine"
  ```
- `verification: passed` records evidence produced in the session that sets it — the stated checks actually run, with their output observed, not the checks that were merely supposed to run.
- A stored check must discriminate: revert the change and the check breaks. Observing a pass is not evidence when the same command passed before the change existed. A pattern-selected command (`-k`, `-p`, a path glob) is the usual way this goes wrong, because the pattern can select a suite that never touches the changed code — or nothing at all, which unittest reports as `Ran 0 tests ... OK` and exit zero. Confirm the discrimination when the check is stored, not at close. (R-00000244)
- Work without a retrospective is not complete.

## What `passed` means per kind

`verification: passed` on a work item is valid only against the criterion declared for its
`kind` in the project's `.stage/operations/verification.md` table. The audit warns when a work
item uses a kind that has no row there.
