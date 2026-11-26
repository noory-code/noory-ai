# Turning a retrospective lesson into a rule

A retrospective ends with two different kinds of sentence, and they need different homes.

| Kind | Lives until | Goes in |
|---|---|---|
| The next card to run, an id to close, a thing to watch once | that card closes | a planned card or a `state/` record, not the retrospective |
| How work is done from now on, in any card | it is superseded | `## Rule candidate`, then a rule file |

Writing both under one heading is what buries the second kind. A reader scanning for durable
behavior finds a queue instead, gives up, and the lesson stays where it was written.

## What goes in `## Rule candidate`

One sentence in the imperative, naming the behavior — not the incident that produced it. Add the
evidence a later reader needs to judge it, and the two facts the promotion tests read
(DE-00000104):

```yaml
state_with_the_candidate:
  who_caught_it:
    write_one_of:
      - a person, named by role (the user, the supervisor, a maintainer)
      - the close reviewer
      - CI
      - found after merge or release
  second_occurrence:
    if: this is the second time the behavior occurred
    then: say so in words ("second time", "2회차", "in two cards") and cite the earlier
      retrospective or card
if_who_caught_it_is_not_stated: a candidate seen once is held ("When a candidate becomes a rule")
```

```markdown
## Rule candidate

- **Count every place a contract lands, not only the call sites.** This card counted code and
  missed the audit rule that reads the same record. Caught by the close reviewer.
  (2회차 — R-00000200 이 같은 자리를 적었다)
```

Leave the section empty when the work taught nothing durable. Most cards teach nothing durable,
and an empty section is the honest answer. A section filled by habit is worse than a blank one:
it makes the pile look full and the next reader stops reading it.

A machine-written retrospective leaves this section empty. Whoever merges the run fills it, because
judging whether a behavior should bind future work is not something the run can see from inside.

## When a candidate becomes a rule

A candidate is `proposed: promote` when **either** test holds, else `proposed: hold`
(DE-00000104). Both are countable; neither asks the writer whether the lesson felt important.

**It was seen twice.** Read the consolidated list first when it exists ("Consolidating
candidates"), then search the retrospectives newer than it for the same behavior. The second
occurrence is the evidence — the first could be one card's circumstance, the second is structure.
This is the project's AHA principle applied to behavior instead of code. A retrospective that
itself states that this is its second occurrence counts as seen twice.

**It was seen once, and a person caught it or it surfaced after merge or release.** One occurrence
is enough here, because the cost already landed on someone. What the close reviewer or CI caught
does not count: when they catch it, the harness did its job. "This seems important" is not this
test; "the close review passed and the user caught it anyway" is.

```yaml
seen_twice:
  - if: two retrospectives state the same behavior
    then: "seen 2", `proposed: promote`
  - if: one retrospective states that this is its second occurrence (it writes "second time",
      "두 번째", "2회차", "in two cards", "카드 두 장에서", or the same in other words)
    then: "seen 2", `proposed: promote`
seen_once:
  - if: its retrospective names a person who caught it, or says it was found after merge or
      after release
    then: `proposed: promote`
  - if: its retrospective says the close reviewer or CI caught it
    then: `proposed: hold`
  - if: its retrospective does not say who caught it, or says only "caught outside the harness"
      without naming who
    then: `proposed: hold`, until a retrospective names a person or a find after merge or release
  - if: its bullet in the list carries `user declined <date>`
    then: `proposed: hold`, until a second occurrence is seen; then it is "seen 2" and promotes
      by the first test
```

Nothing else promotes. A candidate that meets neither test stays in the list as `proposed: hold`,
and the next occurrence promotes it.

## Consolidating candidates

One retrospective sees one card. Whether a behavior happened twice is only visible across all of
them, so a separate session reads them together and keeps one list (DE-00000100). That session
is a research session whose task is the list (DE-00000103). The `stage-orchestrate` skill owns
when the task is given ("The rule-candidates task"): before a milestone is closed, and when 20 or
more retrospectives are newer than the list.

The list is `.stage/state/rule-candidates.md`. The session index shows its `proposed: promote`
lines to every session, one line each, carries the count of the other candidates, and counts the
retrospectives newer than its `through:` id (DE-00000104).

```markdown
---
through: R-00000399
---
# Rule candidates

- **Count every place a contract lands, not only the call sites.** (seen 2: R-00000200,
  R-00000311) — proposed: promote
- **Do not put a records-only commit above the code commit before closing.** (seen 2:
  R-00000368; R-00000368 states its second occurrence) — proposed: promote
- **Do not cut a parallel run's output with `tail -N`.** (seen 1: R-00000246; caught by a
  person: the supervisor noticed) — proposed: promote
- **Set stdout to UTF-8 in `main()`.** (seen 1: R-00000393; caught by CI) — proposed: hold
- **Name the session that did the work on the card.** (seen 1: R-00000390) — proposed: hold
```

```yaml
list_format:
  through: the id of the newest retrospective the session read; required
  one_candidate: one top-level bullet; a wrapped line is indented
  each_bullet_carries:
    - the behavior as one imperative sentence
    - "seen <n>: <R-ids>": every retrospective that states it, so a reader can open the evidence
    - "proposed: promote" when one of the two tests above holds, else "proposed: hold"; no
      third value
  inside_the_parentheses_after_the_R_ids:
    - if: one retrospective states its second occurrence
      then: "seen 2: <R-id>; <R-id> states its second occurrence"
    - if: seen 1 and the retrospective says who caught it
      then: "caught by a person: <role and what they noticed>", "found after merge", "found
        after release", "caught by the close reviewer", or "caught by CI"
    - if: seen 1 and the retrospective does not say who caught it
      then: nothing after the R-id
    - if: the user declined the line
      then: "user declined <date>"; the PO session writes this mark, and the research session
        keeps it and never writes it
  leave_out: a candidate a rule file already states; name that rule file in the session's report
grouping:
  - if: two retrospectives name the same behavior in different words
    then: one bullet that cites both
  - if: it is unclear whether two candidates are the same behavior
    then: keep two bullets
```

Grouping is done by Claude, and nobody checks it before it counts: a wrong merge of two different
behaviors makes a one-time occurrence `seen 2`, and a `seen 2` line becomes a rule with nobody
asked (DE-00000104). When in doubt, two bullets.

### What happens to a `proposed: promote` line

The `seen` count decides who makes the rule (DE-00000104). The `stage-orchestrate` skill
("The rule-candidates task") owns the PO session's steps.

```yaml
proposed_promote:
  - if: seen is 2 or more
    then: it becomes a rule without the user's verdict; the PO session registers a card that
      amends the rule file
  - if: seen is 1
    then: it waits for the user's verdict; the PO session shows the user one table of these
      lines and registers a card that amends the rule file for each line the user chooses
  - if: seen is 1 and the user declines it
    then: the PO session changes the bullet to `proposed: hold` and writes `user declined <date>`
      inside its parentheses (DE-00000104, W-00000421)
proposed_hold: stays in the list; the session index carries only its count
```

A declined line, as the PO session rewrites it:

```markdown
- **Do not cut a parallel run's output with `tail -N`.** (seen 1: R-00000246; caught by a
  person: the supervisor noticed; user declined 2026-11-26) — proposed: hold
```

What the research session with this task does not do:

| It does not | Because |
|---|---|
| edit a retrospective or a decision record | they are the source; the list is derived from them and cites them |
| edit a rule file, a skill, or `operations/` | a card the PO session registers carries a promotion out; this session writes only the list |
| drop a candidate because it looks unimportant | only the two tests promote, and only a stated rule removes a candidate from the list |
| make a `proposed: promote` line a rule, or write `user declined` | it marks the line; the PO session registers the card for a line seen twice and takes the user's verdict on a line seen once |

The list replaces no retrospective. A bullet without its `R-` ids cannot be checked, and a reader
who doubts a bullet opens the retrospectives it cites.

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
