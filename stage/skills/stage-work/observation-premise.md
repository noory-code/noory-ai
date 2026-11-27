## Run the premise before turning an observation into a card

An observation records what was true when someone wrote it. By the time it becomes a card, the code
may already have moved — and a card built on a stale premise sends the executor to do work that is
already done. Four such cards shipped in one day here, and every executor correctly refused them
(R-00000211, R-00000212, R-00000213).

**Reading the code is not enough. Run the behavior once.** Reading only catches a premise that was
never true; running catches one that stopped being true. Both cards that a read-through would have
passed were caught by someone executing the command (R-00000227, R-00000239).

This applies hardest to gates and hooks, which change fastest and whose behavior is least visible
in the source.

**When the observation calls for an artifact rather than a change — a decision record, a document,
a command — open the place it would live before writing the card.** There is no behavior to run
here, so the check above does not fire: the artifact can already exist, promoted and superseding
the very record the observation cites, and the observation still reads as if nothing happened. One
card was registered, started, and rejected on exactly that (R-00000245); the decision it meant to
write had shipped the previous day.

**When a proposal comes from a number — a size, a count, a duration, a cost, a limit that looks
missing, too high, or too low ("this text is N characters, cap it"; "this list has no limit, add
one") — read how the place got its present shape before proposing it to the user, as a card, or as
a follow-up candidate.** The number shows the present shape, not the reason for it, and running the
behavior does not show a reason either. Run `git blame <path>` and
`git log -L <start>,<end>:<path>` on the lines the number measures; read the messages of the
commits that last changed them, the comment beside the code, and the decision record or card those
commits name. If one of them states a reason for the present shape, the proposal says what has
changed since that reason was written, or it is withdrawn. A cap on the open-observation list of
the session-start text was proposed from the text's size alone; commit `db9f74f1` had removed that
cap on purpose, because with it 6 of 17 open observations did not reach the session, and the
proposal was withdrawn. The day before, a release card's completion criteria were written before
checking where the plugin is read from, and the file they named did not change (R-00000334).

An observation's `## Next action` is a claim from the day it was written, not a work order. Confirm
it is still true — that is what makes the card's purpose the human's, not the record's.
