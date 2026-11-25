# After

This document owns the work-completion gate.

Source changes are committed while their authorizing work card is still open. Closing the card
then appends verification evidence, and archiving is the final step after closure.

## Gate

After work:

1. Verify external-perspective completion.
2. Verify internal-perspective completion.
3. Perform the retrospective.
4. Promote approved artifacts to `official/`.
5. Return insufficient work to `work/current/`.
6. Register a follow-up candidate as a planned card (`work/planned/`) only when it carries
   evidence: the command that reproduces what is broken now, or one quoted line of an open
   milestone's completion criteria. Discard every other candidate without recording it, and
   write `Follow-up candidates: registered <n>, discarded <m>` on the closing card's
   `## Progress`. `operations/before.md`, "Follow-up candidates", owns the conditions.
