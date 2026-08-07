# Turning a retrospective lesson into a rule

A retrospective ends with two different kinds of sentence, and they need different homes.

| Kind | Lives until | Goes in |
|---|---|---|
| The next card to run, an id to close, a thing to watch once | that card closes | `## Next changes` |
| How work is done from now on, in any card | it is superseded | `## Rule candidate`, then a rule file |

Writing both under one heading is what buries the second kind. A reader scanning for durable
behavior finds a queue instead, gives up, and the lesson stays where it was written.

## What goes in `## Rule candidate`

One sentence in the imperative, naming the behavior — not the incident that produced it. Add the
evidence a later reader needs to judge it:

```markdown
## Rule candidate

- **Count every place a contract lands, not only the call sites.** This card counted code and
  missed the audit rule that reads the same record. (2회차 — R-00000200 이 같은 자리를 적었다)
```

Leave the section empty when the work taught nothing durable. Most cards teach nothing durable,
and an empty section is the honest answer. A section filled by habit is worse than a blank one:
it makes the pile look full and the next reader stops reading it.

A machine-written retrospective leaves this section empty. Whoever merges the run fills it, because
judging whether a behavior should bind future work is not something the run can see from inside.

## When a candidate becomes a rule

A candidate is promoted when **either** holds. Both are countable; neither asks the writer whether
the lesson felt important.

**It happened twice.** Search the archived retrospectives for the same behavior. The second
occurrence is the evidence — the first could be one card's circumstance, the second is structure.
This is the project's AHA principle applied to behavior instead of code.

**Something outside the harness had to catch it.** A person, a security check, a reviewer, a failed
release — anything that is not Stage's own gates. One occurrence is enough here, because the cost
already landed on someone. "This seems important" is not this test; "the audit passed and a person
caught it anyway" is.

Nothing else promotes. A candidate that meets neither test stays a candidate, and the next
occurrence promotes it.

## Where the rule goes

| The rule binds | Goes to |
|---|---|
| every project that installs Stage | the plugin's `operations/` or the skill that owns the step |
| this project only | `.stage/operations/` |

Ask which one before writing. A rule about how Stage work is done anywhere belongs upstream; a rule
about this repository's venues, verification bar, or tools belongs in the project. Putting a common
rule in `.stage/operations/` means every other project relearns it from scratch.

## Amending beats appending

Check first whether a rule for this behavior already exists. It usually does, and it is usually one
item short — that is exactly why the lesson recurred. Amend the existing rule and cite the new
retrospective beside the earlier ones.

A procedure that can only add rules leaves every stale rule stale, and the same candidate keeps
arriving. When a rule is amended, say what was added and what it now covers that it did not.

## Provenance

Every rule line this procedure adds or amends names the retrospective it came from, so a later
reader can open the evidence and disagree. A rule with no provenance cannot be argued with, and a
rule nobody can argue with is the kind that outlives its reason.

Lines that predate this procedure carry no provenance and do not gain one retroactively.
