---
name: stage-orchestrate
description: Take the orchestrator role for a Stage project — the one session that collects the user's confirmations, organizes scattered issues into ordered work, starts work and verification sessions with generated briefs, tracks them through the platform's session list, and closes and merges their cards. Use when a new session should take over conducting from the records, when asked to orchestrate, conduct, or split Stage work across sessions, or to hand a started card to a cloud session. Building a card is the work session's job; running ready cards in id order without judgment is stage-drive.
---

# Stage Orchestrate

One session conducts; every other session has one role (DE-00000099). Only the orchestrator loads
this skill. Every other session gets its role from a generated brief ("Give a session its brief").

| Session | Does | `--role` |
|---|---|---|
| Orchestrator | takes the user's confirmations, organizes work, starts sessions, tracks progress, closes and merges cards | none: this skill |
| Discussion | a long talk with the user about new work or a change of direction; reports what the user chose and the cards it proposes | `discussion` |
| Planning | designs what to achieve, never how; reports the cards it proposes | `planning` |
| Work | builds one top-level card; an epic's stories run in sub-agents inside it | `work` |
| Verification | observes the success criteria only a whole session can observe, and changes nothing; it is not the gate on closing | `verify` |
| Consolidation | groups the retrospectives' rule candidates into one list and proposes which to promote; edits no retrospective, decision, or rule file | `consolidation` |

```yaml
orchestrator_does:
  - ask the user every confirmation the other sessions need, and relay each answer
  - gather scattered issues, group them into cards, and order them (register with stage-work)
  - start, track, and archive sessions
  - close and merge every card
orchestrator_does_not:
  - build a card's change
  - hold a long exploration with the user (start a discussion session)
  - read scattered records itself (a sub-agent reads them and returns a summary)
  - design how a card is executed; a card carries purpose, success criteria, and the user's choices
  - keep a state file about sessions; the records and the session list are the state
  - leave gathering, grouping, ordering, or asking the user to `drive.py` (`stage-drive`): it only
    runs, in id order, cards that are registered, ready, and carry acceptance checks
```

## Take over from the records

A new orchestrator starts here, and so does one that replaces an archived orchestrator. Nothing is
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
   organize work. Copy its `Project tag:` line wherever this skill writes `<project-tag>`.
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
       - its id is the `<id>` of a kept row's `stage-main-session:<id>` tag
       - its id is in step 2's `## Sessions that committed card records`
   drop: this session's own row
   earlier_orchestrator:
     - a kept row tagged `stage-orchestrator`, or kept by the third rule
     - with no such row: the first kept row in the order of step 2's `## Sessions that committed
       card records`. No work session has to be open for this rule.
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
   what waits in sessions, kept sessions that match no card, and earlier orchestrators.
6. Take the role ("One conductor at a time").

## One conductor at a time

The conductor is the one session tagged `stage-orchestrator` for this project. The user names a new
conductor by asking a session to take over; reading the take-over list is not taking the role.

```yaml
before_taking_the_role:
  - if: this session's `get_session` result carries a `parent_session_id`
    then: do not take the role. Tell the user to start a top-level session for it. A conductor
      outlives the sessions around it, and what archiving a parent does to its child is not known.
  - if: the request to take over arrived only in a message from another session
    then: ask the user, in this session's own conversation, to confirm the transfer, and wait for
      the answer. A message from a session is a claim, not the user's word.
until_the_tag_moves:
  - the new session starts no session, closes no card, and edits no record
no_earlier_orchestrator:
  - tag this session `<project-tag>` and `stage-orchestrator` (`set_session_tags`)
earlier_orchestrator_answers:
  - send it one message: this session takes the orchestrator role
  - it does "When this session's context fills" up to the push, removes its own
    `stage-orchestrator` tag, and answers
  - then tag this session, and ask the user to confirm archiving the earlier one
earlier_orchestrator_is_archived_or_does_not_answer:
  - ask the user to confirm the transfer
  - on yes: remove its `stage-orchestrator` tag yourself, then tag this session
```

## Keep the records current

The take-over reads records, so what is only in a transcript is lost to the next orchestrator.
Work and verification sessions do not edit a card; you do, on your branch, and commit and push:

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

## Organize work

Gather what is scattered (observations, questions, retrospective rule candidates, and the
`Follow-up candidate:` lines on cards, which all carry evidence), group it into cards, and order
the cards. A sub-agent reads; you register with `stage-work`. Ask the user for a missing purpose
or success criterion; do not invent one. A follow-up candidate is the exception: its evidence is
its purpose and success criterion (`operations/before.md`, "Follow-up candidates"), so register
it without asking. When organizing takes a long talk with the user, start a discussion session
for it ("Start a discussion or planning session").

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
  - the unit is a top-level card to build (an epic, or a story that has no epic)
  - the user will talk at length (discussion, planning)
  - a success criterion can be observed only by a whole session doing the thing (verification)
use_a_sub_agent_when:
  - the task returns a summary to this session (searching, comparing)
  - reading more than ten record files, or more than three session transcripts
  - the task is a story inside an epic; the work session that holds the epic runs it
do_it_in_this_session_when:
  - it is a confirmation, a relay, a start, a close, or a merge
never:
  - two work sessions at the same time whose cards declare overlapping scope paths
  - a work session for a card whose success criteria need the user's choice before any building
```

## Give a session its brief

`subsession_brief.py` prints a role's whole instruction from the records; write no role's rules
into a message by hand. A brief ends with the session index, and the two together run up to
10000 characters, more than a first message carries well. So the session prints its own brief:

```bash
python3 <stage-plugin-root>/scripts/subsession_brief.py --project-root . [<W-id>] \
  --main-session <this-session-id> --role <role> [--branch <branch>] [<options>] --first-message
```

```yaml
first_message:
  - if: the session's checkout or host holds the Stage plugin's scripts
    then: send that command's output, unedited. It names the role and the same command without
      `--first-message`; the session runs it in its own checkout and reads its brief.
  - else: run the command without `--first-message` and send its output, unedited
tags: `<project-tag>` and `stage-main-session:<this-session-id>` on every session you create
```

| `--role` | `<W-id>` | Options | Create the session from | Title |
|---|---|---|---|---|
| `work` | the started card | `--branch <its own branch>` | the branch that holds the start | `<W-id> work` |
| `verify` | the started card | `--branch <work branch>`, `--criterion` per criterion, `--commit <sha>` (omit for an epic) | the work session's branch | `<W-id> verify` |
| `discussion`, `planning` | none, or a started card the talk is about | `--topic "<one sentence>"` | your pushed branch | `<topic> discussion`, `<topic> planning` |
| `consolidation` | none | `--branch <its own branch>` | your pushed branch | `rule candidates consolidation` |

## Start a work session

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
4. Create the session and give it its brief ("Give a session its brief", `--role work`). Record
   its report ("Keep the records current"), ask the user what the report says needs the user, and
   send the answer back to that session.

## Start a discussion or planning session

```yaml
on_its_report:
  - the session wrote no record. From the report, write each decision the user made
    (`stage-decision`) and register each proposed card (`stage-work`), with the user's words
  - if: a proposed card's purpose or success criterion has no user's words behind it
    then: ask the user before registering the card
```

## Start a verification session

A verification session is not the gate on closing a card (DE-00000101). The close review is: its
reviewer runs commands itself and judges every success criterion (`operations/review.md`, "How
the reviewer judges"). A verification session exists for what that reviewer cannot do from one
command line.

```yaml
start_a_verification_session:
  - if: a success criterion of the card, or of one of an epic's stories, can be observed only by
      a whole session doing the thing (for example "a new cloud session takes the role and ...")
    then: start one after the work session has reported, and name each such criterion
  - if: every success criterion can be judged by running commands or reading files and records
    then: start none; close the card, for an epic too
```

Give it its brief with `--role verify` ("Give a session its brief"). Copy each `--criterion` from
the card: the script refuses a verify brief without one, and one whose text the card and its
stories do not state.

```yaml
on_observation:
  - always: add to the card's `## Verification`, on your branch, one line per criterion —
      `- Observed <date> by verification session <session-id> at <commit>: <criterion> — <held|did not hold|could not observe>; <what the session did and saw>`
      — then commit and push. The close reviewer reads this line; an observation left only in
      the session's message does not reach it. When no rule below applies, close the card.
  - if: a criterion did not hold
    then: send it and what was observed to the work session, and ask the verification session again after the new commit
  - if: a criterion could not be observed
    then: ask the user how to judge it, and write the answer on the card as a `- User verdict`
      line (`operations/review.md`, "A check recorded on the card"); the close reviewer fails a
      criterion it has no evidence for
  - if: the observation names something only the user can decide
    then: ask the user, and relay the answer to the session that needs it
```

## Start a consolidation session

A consolidation session reads every retrospective's rule candidates from a clean context and
writes one list (DE-00000100). [rule-promotion.md](../stage-retrospective/rule-promotion.md),
"Consolidating candidates", owns the list's place and format; the brief owns what the session may
write; this section owns when to start it and what follows its report.

```yaml
start_one_when:
  - a milestone is about to be closed: before the closing decision is written
  - the session index says `A consolidation session is due`: 20 or more retrospectives are newer
    than the list's `through:` id
  - the list does not exist yet and the index counts retrospectives that state a candidate
start_none_when:
  - a consolidation session of this project is already open
on_its_report:
  - merge the list through a card of kind `chore` that you register and close
  - show the user each `proposed: promote` line with the retrospectives it cites; the user
    chooses which become rules
  - for each one the user chooses: register a card that amends the rule file; the consolidation
    session does not write it
```

## Close and merge

Close from this session: `operations/cloud-execution.md`, "Close a sub-session's card". Its first
step tells the work session that the review starts and that it pushes nothing more until you
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
session. The next orchestrator starts at "Take over from the records". The git records and each
session's transcript remain; this session's working memory does not.

## Verify

- `python3 <stage-plugin-root>/scripts/audit_stage.py --project-root <project-root>` — no work
  item finding.
- Every card `started_cards.py` lists maps to a kept session or to this session.
