# PM, Plan, and Research Sessions

## Start a PM session

A cloud session cannot reserve record ids on the remote, because its proxy refuses pushes outside
its own branch, so you hold the ids its card may need (DE-00000094).

1. `git fetch origin`, then start the card: `start_work.py <W-id> --scope "<paths>"
   --environment cloud --review`. Starting an epic starts its stories with it, and each story
   takes the epic's `review: pending`, its `environment`, and that environment's venue, so every
   story closes with its own review (`operations/cloud-execution.md`, "Register or start").
   `start_work.py` refuses the start when a story names another venue or environment, and
   refuses a card another fetched branch already started or archived.
2. When the card may create records with new ids (a decision, an observation), hold a block:
   `stage_record_ids.py --project-root . --reserve-for <W-id> --count <n> <PREFIX>`. It writes the
   ids to the card's `reserved_ids:`. Reserve nothing for a card that creates no records; the
   brief then forbids new records.
3. Commit and push the start and the block before creating the session.
4. Create the session and give it its brief ("Give a session its brief", `--role pm`). Record
   its report ("Keep the records current"), ask the user what the report says needs the user, and
   send the answer back to that session.

The PM session decides whether the card is one piece it does itself or several pieces for
specialist sub-agents; its brief owns that rule and the specialists' names.

## Start a plan session

The plan session does not see the talk. It sees your digest, so what the digest gets wrong
becomes a card.

```yaml
digest:
  - the topic, in one sentence: the same sentence as `--topic`
  - each thing the user asked for or chose, with the user's words quoted exactly and their date
  - each research result the user chose from, and what the user chose
  - what the user left undecided
  - the ids of the records the talk bears on
never_in_the_digest:
  - a purpose or a success criterion in your words, given as the user's
send:
  - create the session and give it its brief (`--role plan`)
  - then send the digest as one message to that session
on_its_report:
  - the session wrote no record. Register each card draft yourself (`stage-work`), with the
    user's words the draft quotes; the plan session registers nothing
  - if: a draft's purpose or success criterion has no user's words behind it
    then: ask the user before registering the card
  - if: a draft's purpose differs from what the user said
    then: do not register it; send the difference to the plan session and ask for a new draft
```

## Start a research session

```yaml
start_one_for_a_question:
  - give it its brief with `--role research --topic "<the question>"`
  - it edits nothing and decides nothing; its report is options with evidence
on_its_report:
  - show the user the options and their evidence, and ask the user to choose
  - write the choice as a decision record (`stage-decision`), with the user's words
  - archive the session when the user has chosen, or send it the next question on the same topic
```

### The rule-candidates task

Gathering rule candidates is a task you give a research session, not a role of its own
(DE-00000103). The session reads every retrospective's rule candidates from a clean context and
writes one list (DE-00000100): the only file a research session ever writes.
[rule-promotion.md](../stage-retrospective/rule-promotion.md), "Consolidating candidates", owns
the list's place and format; the brief owns what the session may write; this section owns when
to give the task and what follows its report.

```yaml
give_the_task_when:
  - a milestone is about to be closed: before the closing decision is written
  - the session index says `Rule candidates are due`: 20 or more retrospectives are newer
    than the list's `through:` id
  - the list does not exist yet and the index counts retrospectives that state a candidate
give_it_to_none_when:
  - a research session of this project already has the task and is open
brief: "`--role research --task rule-candidates --branch <its own branch>`, and no `--topic`"
on_its_report:
  - merge the list through a card of kind `chore` that you register and close
  - for_each_proposed_promote_line:  # DE-00000104
      - if: its `seen` count is 2 or more
        then: register a card that amends the rule file; do not ask the user
      - if: its `seen` count is 1
        then: put it in the table and wait for the user's verdict
  - show_the_user_only:
      - one table of the `proposed: promote` lines seen once; columns are the behavior, the
        retrospective, and who caught it
      - one tally line; how many lines seen twice became rule cards, how many lines seen once
        are in the table, and how many lines are `proposed: hold`
      - nothing else from the list
  - for_each_line_of_the_table:
      - if: the user chooses it
        then: register a card that amends the rule file
      - if: the user declines it
        then: change its bullet to `proposed: hold` and write `user declined <date>` inside its
          parentheses (DE-00000104, W-00000421). Commit that in the `chore` card that merges the
          list while that card is open; after it closed, through a new `chore` card.
  - the research session writes no rule file and no `user declined` mark
```
