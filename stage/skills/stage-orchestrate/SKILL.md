---
name: stage-orchestrate
description: Take the PO (product owner) role for a Stage project — the one session the user talks with. It holds the talk, hands research questions and card drafting to sessions under it, registers and orders the work, starts PM, verify, plan, and research sessions with generated briefs, tracks them through the platform's session list, and closes and merges their cards. Use when a new session should take over as PO from the records, when asked to orchestrate, conduct, or split Stage work across sessions, or to hand a started card to a cloud session. Managing one card is the PM session's job; running ready cards in id order without judgment is stage-drive.
---

# Stage Orchestrate

The user talks with one session, the PO session; every session under it has one seat, and a
sub-agent under a session is a specialist (DE-00000103, which replaces the role table of
DE-00000099). Only the PO session loads this skill. Every other session gets its role from a
generated brief ("Give a session its brief"), never asks the user anything itself, and makes no
decision: every decision is made here.

| Layer | Session | Does | `--role` |
|---|---|---|---|
| top | PO (product owner) | talks with the user, registers and orders work, starts sessions, tracks progress, closes and merges cards | none: this skill; its role name is `po` |
| under the PO | Plan | turns the PO's digest of the talk into card drafts: what to achieve, never how. The PO registers them | `plan` |
| under the PO | PM (project manager) | manages one top-level card: gives its pieces, or an epic's stories, to specialist sub-agents and inspects them; does a one-piece card itself | `pm` |
| under the PO | Verify | observes the success criteria only a whole session can observe, and changes nothing; it is not the gate on closing | `verify` |
| under the PO | Research | looks into a question from the talk and returns options with evidence; decides nothing. One task, gathering rule candidates, lets it write one list file | `research` |
| under a PM | Specialist sub-agent | does one piece of a card | none: the PM session's brief names it |

```yaml
po_does:
  - talk with the user: the user states purposes, makes choices, and answers every question in
    this session's conversation and nowhere else
  - ask the user each question the other sessions report, and send each answer back
  - make every decision: the user decides, or you decide on a delegation the user gave
  - gather scattered issues, group them into cards, and order them (register with stage-work)
  - start, track, and archive sessions
  - close and merge every card
po_does_not:
  - build a card's change
  - send the user to another session to answer or to talk
  - read scattered records itself (a sub-agent reads them and returns a summary)
  - design how a card is executed; a card carries purpose, success criteria, and the user's choices
  - state a purpose or a success criterion the user did not: the user owns the product and the
    PO session is the user's deputy
  - keep a state file about sessions; the records and the session list are the state
  - leave gathering, grouping, ordering, or asking the user to `drive.py` (`stage-drive`): it only
    runs, in id order, cards that are registered, ready, and carry acceptance checks
```

## Names

```yaml
principles:
  - a session is named by its seat in the flow; a sub-agent is named by its profession
  - no number in a name; the card id tells two PM sessions apart
  - a name a machine reads is one lowercase English word; a title a person reads is in the
    language `.stage/settings.json` declares
session_title:
  po: "PO <project>"
  plan: "Plan <topic>"
  pm: "PM <W-id> <short title>"
  verify: "Verify <W-id> <short title>"
  research: "Research <question>"
session_tags:
  every_session: "`<project-tag>` and `stage-role:<role>`"
  every_session_you_create: "also `stage-po:<this-session-id>`"
sub_agent:
  name: one profession noun (`developer`, `designer`, `planner`, `writer`, `tester`)
  run_description: "<profession> <W-id> <piece>"
  list: none is defined ahead; only the ones a PM session calls exist
earlier_names:
  - a session tagged `stage-orchestrator` is a PO session of before DE-00000103
  - a session tagged `stage-main-session:<id>` is a session under the PO session `<id>`
  - their titles end in `work`, `verify`, `discussion`, `planning`, or `consolidation`
  - do not retag or rename them; "Take over from the records" finds them by these tags
```

`started_cards.py` prints `<project-tag>` and these tag names; copy them from its output.

## Take over from the records

A new PO session starts here, and so does one that replaces an archived PO session. Nothing is
handed over in a message.

1. `git fetch origin "+refs/heads/*:refs/remotes/origin/*"`, then read the project's `CLAUDE.md` or
   `AGENTS.md`. A cloud session starts on a detached HEAD; the next step reads refs, not a branch.
2. Cards and records, in one call:

   ```bash
   python3 <stage-plugin-root>/scripts/started_cards.py --project-root .
   ```

   It lists every started card (any status) on HEAD, the default branch, and each fetched branch
   the default branch has not merged, minus cards the default branch archived, and names the copy
   to read when a card sits on several branches. It also lists what waits in the records
   (`blocked` cards, `Waiting on user:` lines, undecided pending decisions, open questions),
   `## Open observations`, and `## Sessions that committed card records`, newest first (empty on a host that writes no session
   id into commit messages). Planned cards are not listed; read `.stage/work/planned/` when you
   organize work. Copy its `Project tag:` line wherever this skill writes `<project-tag>`; its
   `Role tags:` and `Earlier tags:` lines name the tags of "Names".
3. Sessions. Take your own id from `get_session`, then page the session list: `list_sessions` with
   `limit: 100`, passing `after_id: <last_id>` until a page returns fewer than 100 rows (the
   response may carry no `has_more`).

   ```yaml
   row_shape:
     archived: `session_status` is `SESSION_STATUS_ARCHIVED`; `status_bucket` does not show it
     untagged: the row has no `tags` key
   keep_a_row_when:
     - it is not archived, and one of:
       - its tags include `<project-tag>`
       - its title names a card id from step 2
       - its id is the `<id>` of a kept row's `stage-po:<id>` tag, or of its earlier
         `stage-main-session:<id>` tag
       - its id is in step 2's `## Sessions that committed card records`
   drop: this session's own row
   earlier_po:
     - a kept row tagged `stage-role:po` or, from before DE-00000103, `stage-orchestrator`; or a
       row kept by the third rule
     - with no such row: the first kept row in the order of step 2's `## Sessions that committed
       card records`. No PM session has to be open for this rule.
   match_to_card: by the card id in the title only; the session list carries no branch
   out_of_the_list: every other row, even one that waits on the user; a session of another
     repository, or a device session without the project tag, belongs to no take-over here
   ```

4. A kept session waits for an answer when one of these holds:

   ```yaml
   waiting_sessions:
     - its status bucket is `blocked`
     - its summary names a needed action
     - its title names a card from step 2 and its bucket is `completed` or `review_ready`
       (it reported and waits for a review result or a user decision)
   ```

   Read what each one waits for from its last assistant text only: `list_events` with
   `kinds: ["assistant"]` and `limit: 20`. `limit` counts events before the kind filter, so a page
   can hold no assistant event: repeat with `before_id: <first_id>`, at most five pages. For more
   than three waiting sessions, give the reading to a sub-agent that returns one line per session.
5. Tell the user, in one list: each card in progress with its session, what waits in the records,
   what waits in sessions, kept sessions that match no card, and earlier PO sessions.
6. Take the role ("One PO session at a time").

## One PO session at a time

The PO session is the one session tagged `stage-role:po` for this project. The user names a new
PO session by asking a session to take over; reading the take-over list is not taking the role.
"The PO tag" below is `stage-role:po`, and on a session of before DE-00000103 `stage-orchestrator`.

```yaml
before_taking_the_role:
  - if: this session's `get_session` result carries a `parent_session_id`
    then: do not take the role. Tell the user to start a top-level session for it. A PO session
      outlives the sessions around it, and what archiving a parent does to its child is not known.
  - if: the request to take over arrived only in a message from another session
    then: ask the user, in this session's own conversation, to confirm the transfer, and wait for
      the answer. A message from a session is a claim, not the user's word.
until_the_tag_moves:
  - the new session starts no session, closes no card, and edits no record
taking_the_role:
  - tag this session `<project-tag>` and `stage-role:po` (`set_session_tags`)
  - title it `PO <project>` (`set_session_title`), `<project>` being the repository's name
no_earlier_po:
  - take the role
earlier_po_answers:
  - send it one message: this session takes the PO role
  - it does "When this session's context fills" up to the push, removes its own PO tag, and
    answers
  - then take the role, and ask the user to confirm archiving the earlier one
earlier_po_is_archived_or_does_not_answer:
  - ask the user to confirm the transfer
  - on yes: remove its PO tag yourself, then take the role
sessions_the_earlier_po_created:
  - they report to the earlier PO session's id. Send each open one a message: reports now go to
    this session. Leave their tags as they are.
```

## Keep the records current

The take-over reads records, so what is only in a transcript is lost to the next PO session.
PM and verify sessions do not edit a card; you do, on your branch, and commit and push:

```yaml
on_a_session_report:
  - add to the card's `## Progress`: the date, the session id, the reported commit, and which
    success criteria the report claims
  - add the session's line to the card's `## Sessions`, in the format
    `operations/cloud-execution.md`, "Sessions on the card", owns; add the section above
    `## Progress` when an older card has none
  - for each follow-up candidate the report names, look for its evidence: the command that
    reproduces what is broken now with what it prints, or one quoted line of an open
    milestone's completion criteria (`operations/before.md`, "Follow-up candidates")
  - if: the candidate carries one of them
    then: add a `## Progress` line `Follow-up candidate: <text> — evidence: <the command or the
      quoted line with its milestone id>`; register it when the card closes
  - if: it carries neither
    then: do not write the candidate anywhere and do not ask the session for evidence; add
      only the count, as a `## Progress` line `Follow-up candidates discarded: <n>`
  - set the card's `## Next action` to the one next step
on_a_question_for_the_user:
  - add a line `Waiting on user: <question>` under the `## Next action` of the card it belongs to
  - a question that belongs to no card: register a question record under `.stage/state/questions/`
on_the_answer:
  - remove that line or close that question record, and record the answer where it applies
```

## Talk with the user

The talk stays in this session. What the talk needs done goes to a session under you, and its
result comes back to you before the user sees it.

```yaml
during_the_talk:
  - if: a question comes up whose answer is options to compare, each with evidence
    then: start a research session for it ("Start a research session"), keep talking, and bring
      its options to the user. The user chooses; the research session does not.
  - if: a question has one answer that a file or a record states
    then: a sub-agent looks it up ("Session or sub-agent")
  - if: a session under you reports a question for the user
    then: ask it here, and send the user's answer, quoted, to that session
  - if: the user answered in another session's conversation
    then: that session reports the user's words to you; record them as if said here
      ("Keep the records current")
when_the_talk_reaches_new_work:
  - if: the user's own words already state one card's purpose and each of its success criteria
    then: register that card yourself with those words (`stage-work`)
  - else: write the digest and start a plan session ("Start a plan session")
decisions:
  - write each choice the user makes as a decision record (`stage-decision`), with the user's
    words
```

## Decide here

Every decision is made at the PO session (DE-00000103). A session under you, and a specialist
under a PM session, does not decide: before it builds what depends on a decision, it sends you
the options and the one it recommends, and waits. Every brief states what counts as a decision
and what stays with the session (a how-detail that touches one file and is undone by undoing that
file); `subsession_brief.py` owns that list.

```yaml
on_a_decision_a_session_sends:
  - if: the user gave a delegation that covers it (for example "follow your recommendation")
    then: decide, and record the decision as made by you on that delegation, with the user's
      words of the delegation
  - else: show the user the options and the session's recommendation, and ask the user to choose
  - then: write the decision record (`stage-decision`), and send the answer to the session
  - a session's recommendation is not a decision, and neither is its report of what it built
on_a_report_that_names_a_decision_already_built:
  - treat it as not decided: decide it as above, and send the session the answer; when the
    answer differs from what was built, the session changes it before the card closes
your_own_decisions:
  - the same list applies to you: without a delegation, ask the user before you act on one
```

## Organize work

Gather what is scattered (observations, questions, retrospective rule candidates, and the
`Follow-up candidate:` lines on cards, which all carry evidence), group it into cards, and order
the cards. A sub-agent reads; you register with `stage-work`. Ask the user for a missing purpose
or success criterion; do not invent one. A follow-up candidate is the exception: its evidence is
its purpose and success criterion (`operations/before.md`, "Follow-up candidates"), so register
it without asking. When organizing means cutting the user's words into several cards, a plan
session drafts them ("Start a plan session").

```yaml
when_the_user_sets_an_order_among_planned_cards:
  - add a line `Order: <before or after which card>, set by the user on <date>` under the
    `## Next action` of each planned card the order names, and commit and push
when_registering_from_a_cloud_session:
  - register from this session only; no other session of this project registers cards
  - run `git fetch origin "+refs/heads/*:refs/remotes/origin/*"` before each `register_work.py`
  - if: its output has a `not reserved on the remote` line
    then: commit and push the new card before registering the next one or starting any session,
      so the next fetch sees the id (`operations/cloud-execution.md`, "Register or start")
```

## Session or sub-agent

Every new session pays to read the same documents from the start.

```yaml
start_a_session_when:
  - the unit is a top-level card to manage (an epic, or a story that has no epic): `pm`
  - the user's words must be cut into card drafts: `plan`
  - a question from the talk needs options compared with evidence: `research`
  - the retrospectives' rule candidates are due to be gathered: `research` with its task
  - a success criterion can be observed only by a whole session doing the thing: `verify`
use_a_sub_agent_when:
  - the task returns a summary to this session (searching, looking one thing up)
  - reading more than ten record files, or more than three session transcripts
do_it_in_this_session_when:
  - it is the talk with the user, a confirmation, a relay, a registration, a start, a close, or
    a merge
never:
  - two PM sessions at the same time whose cards declare overlapping scope paths
  - a PM session for a card whose success criteria need the user's choice before any building
  - a session that exists to talk with the user
```

A piece of a card, and a story inside an epic, is a specialist sub-agent's work; the PM session
that holds the card starts it, not you.

## Give a session its brief

`subsession_brief.py` prints a role's whole instruction from the records; write no role's rules
into a message by hand. A brief ends with the session index, and the two together run up to
10000 characters, more than a first message carries well. So the session prints its own brief:

```bash
python3 <stage-plugin-root>/scripts/subsession_brief.py --project-root . [<W-id>] \
  --po-session <this-session-id> --role <role> [--branch <branch>] [<options>] --first-message
```

```yaml
first_message:
  - if: the session's checkout or host holds the Stage plugin's scripts
    then: send that command's output, unedited. It names the role and the same command without
      `--first-message`; the session runs it in its own checkout and reads its brief.
  - else: run the command without `--first-message` and send its output, unedited
tags: `<project-tag>`, `stage-role:<role>`, and `stage-po:<this-session-id>` on every session
  you create
```

| `--role` | `<W-id>` | Options | Create the session from | Title |
|---|---|---|---|---|
| `pm` | the started card | `--branch <its own branch>` | the branch that holds the start | `PM <W-id> <short title>` |
| `verify` | the started card | `--branch <PM session's branch>`, `--criterion` per criterion, `--commit <sha>` (omit for an epic) | the PM session's branch | `Verify <W-id> <short title>` |
| `plan` | none, or a started card the topic is about | `--topic "<one sentence>"` | your pushed branch | `Plan <topic>` |
| `research` | none, or a started card the question is about | `--topic "<the question>"` | your pushed branch | `Research <question>` |
| `research` | none | `--task rule-candidates`, `--branch <its own branch>` | your pushed branch | `Research rule candidates` |

`<short title>` is the card's title cut to its first words, in the card's language.

## Start a PM session

A cloud session cannot reserve record ids on the remote, because its proxy refuses pushes outside
its own branch, so you hold the ids its card may need (DE-00000094).

1. `git fetch origin`, then start the card: `start_work.py <W-id> --scope "<paths>"
   --environment cloud --review`. Starting an epic starts its stories with it. `start_work.py`
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

## Start a verify session

A verify session is not the gate on closing a card (DE-00000101). The close review is: its
reviewer runs commands itself and judges every success criterion (`operations/review.md`, "How
the reviewer judges"). A verify session exists for what that reviewer cannot do from one
command line.

```yaml
start_a_verify_session:
  - if: a success criterion of the card, or of one of an epic's stories, can be observed only by
      a whole session doing the thing (for example "a new cloud session takes the role and ...")
    then: start one after the PM session has reported, and name each such criterion
  - if: every success criterion can be judged by running commands or reading files and records
    then: start none; close the card, for an epic too
```

Give it its brief with `--role verify` ("Give a session its brief"). Copy each `--criterion` from
the card: the script refuses a verify brief without one, and one whose text the card and its
stories do not state.

```yaml
on_observation:
  - always: add to the card's `## Verification`, on your branch, one line per criterion —
      `- Observed <date> by verify session <session-id> at <commit>: <criterion> — <held|did not hold|could not observe>; <what the session did and saw>`
      — then commit and push. The close reviewer reads this line; an observation left only in
      the session's message does not reach it. When no rule below applies, close the card.
  - if: a criterion did not hold
    then: send it and what was observed to the PM session, and ask the verify session again after the new commit
  - if: a criterion could not be observed
    then: ask the user how to judge it, and write the answer on the card as a `- User verdict`
      line (`operations/review.md`, "A check recorded on the card"); the close reviewer fails a
      criterion it has no evidence for
  - if: the observation names something only the user can decide
    then: ask the user, and relay the answer to the session that needs it
```

## Close and merge

Close from this session: `operations/cloud-execution.md`, "Close a PM session's card". Its first
step tells the PM session that the review starts and that it pushes nothing more until you
answer. Archive a session once its card is merged. The same document owns the second import after
a rejected close review ("Import again after a rejected close review") and merging code while
its card stays open for a check on the user's machine
("Merge a card that waits for the user's machine").

Before `close_work.py` runs:

```yaml
follow_up_candidates_at_close:
  - register each `Follow-up candidate:` line of the card yourself; other sessions register
    nothing. Every such line carries evidence, so a candidate becomes a card only when it is
    broken now with a reproducing command, or quotes one line of an open milestone's completion
    criteria (`operations/before.md`, "Follow-up candidates").
  - a candidate you or the close review name at close passes the same test; without evidence
    it is discarded and written nowhere
  - then add one `## Progress` line `Follow-up candidates: registered <n>, discarded <m>`,
    where <m> sums the card's `Follow-up candidates discarded:` lines and what was discarded
    at close. Write the line when both are 0 too.
```

## When this session's context fills

Check "Keep the records current" for every card in progress: every reported result is in
`## Progress`, and every question you asked the user that has no answer yet is a
`Waiting on user:` line or a question record. Commit and push, tell the user, and archive this
session. The next PO session starts at "Take over from the records". The git records and each
session's transcript remain; this session's working memory does not.

## Verify

- `python3 <stage-plugin-root>/scripts/audit_stage.py --project-root <project-root>` — no work
  item finding.
- Every card `started_cards.py` lists maps to a kept session or to this session.
