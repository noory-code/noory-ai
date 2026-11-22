---
name: stage-orchestrate
description: Take the orchestrator role for a Stage project — the one session that collects the user's confirmations, organizes scattered issues into ordered work, starts work and verification sessions with generated briefs, tracks them through the platform's session list, and closes and merges their cards. Use when a new session should take over conducting from the records, when asked to orchestrate, conduct, or split Stage work across sessions, or to hand a started card to a cloud session. Building a card is the work session's job; running ready cards in id order without judgment is stage-drive.
---

# Stage Orchestrate

One session conducts; every other session has one role (DE-00000099). Only the orchestrator loads
this skill. Every other session receives its role in its first message.

| Session | Does | Gets its role from |
|---|---|---|
| Orchestrator | takes the user's confirmations, organizes work, starts sessions, tracks progress, closes and merges cards | this skill |
| Discussion | a long talk with the user about new work or a change of direction; ends in decision records and cards | a first message you write |
| Planning | designs what to achieve, never how | a first message you write |
| Work | builds one top-level card; an epic's stories run in sub-agents inside it | `subsession_brief.py --role work` |
| Verification | judges success criteria and changes nothing | `subsession_brief.py --role verify` |

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
```

## Take over from the records

A new orchestrator starts here, and so does one that replaces an archived orchestrator. Nothing is
handed over in a message.

1. `git fetch origin`, then read the project's `CLAUDE.md` or `AGENTS.md`.
2. Cards in progress: every record under `.stage/work/current/` whose `status` is `active` or
   `blocked`, on the checked-out branch and on each fetched branch
   (`git ls-tree -r --name-only origin/<branch> .stage/work/current`). A card that exists only on
   another branch was started by the session that owns that branch.
3. Sessions: read the platform's session list. On Claude Code cloud that is `list_sessions`
   without `children`: sessions an earlier orchestrator created are not this session's children.
   A session on the user's device is read the same way as a cloud session.
4. Confirmations waiting for an answer come from three places:

   ```yaml
   waiting_confirmations:
     - a listed session whose status bucket is `blocked`, or whose summary names a needed action
     - a card whose status is `blocked`; its `## Next action` names the question
     - a decision under `.stage/decisions/pending/` whose status is not `decided`
   ```

   Read a waiting session's question from its last messages (`list_events` with kinds `assistant`
   and `result`).
5. Match each session to a card by the card id in its title or branch. Tell the user, in one list:
   the cards in progress and their session, the confirmations waiting, and the sessions that
   match no open card.

When step 2 or 4 means reading more than the open cards and pending decisions, give the reading to
a sub-agent and keep its summary.

## Organize work

Gather what is scattered (observations, questions, retrospective rule candidates, follow-up
candidates in session reports), group it into cards, and order the cards. A sub-agent reads; you
register with `stage-work`. Ask the user for a missing purpose or success criterion; do not invent
one. When organizing takes a long talk with the user, start a discussion session for it and read
its records afterward.

## Session or sub-agent

Every new session pays to read the same documents from the start.

```yaml
start_a_session_when:
  - the unit is a top-level card to build (an epic, or a story that has no epic)
  - the user will talk at length (discussion, planning)
  - a judgment needs a context that did not see the building (verification)
use_a_sub_agent_when:
  - the task returns a summary to this session (reading records, searching, comparing)
  - the task is a story inside an epic; the work session that holds the epic runs it
do_it_in_this_session_when:
  - it is a confirmation, a relay, a start, a close, or a merge
never:
  - two work sessions at the same time whose cards declare overlapping scope paths
  - a work session for a card whose success criteria need the user's choice before any building
```

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
4. Print the brief and send it as the session's first message, unedited:

   ```bash
   python3 <stage-plugin-root>/scripts/subsession_brief.py --project-root . <W-id> \
     --main-session <this-session-id> --branch <session-branch>
   ```

   Create the session from the branch that holds the start, and put the card id in its title.
5. The session reports the branch, the commit of each card, changed paths, checks, decisions,
   scope crossings, what needs the user, and follow-up candidates. Ask the user what needs the
   user, and send the answer back to that session.

## Start a verification session

Start one when a work session has reported. Create it from the work session's branch.

```bash
python3 <stage-plugin-root>/scripts/subsession_brief.py --project-root . <W-id> \
  --main-session <this-session-id> --role verify --branch <work-session-branch> --commit <sha>
```

For an epic, omit `--commit`: the brief lists the stories and the session judges each one on the
commit that names its id. The session answers with `PASS` or `FAIL` per success criterion.

```yaml
on_verdict:
  - if: every criterion passes
    then: close the card
  - if: a criterion fails
    then: send the failed criteria and their reasons to the work session, and ask the verification session again after the new commit
  - if: the verdict names something only the user can decide
    then: ask the user, and relay the answer to the session that needs it
```

The verification session's verdict decides whether you close. `close_work.py` still runs the
project's configured close review as its own command; this skill does not replace that step.

## Close and merge

Close from this session: `operations/cloud-execution.md`, "Close a sub-session's card". Register
the follow-up candidates yourself; other sessions register nothing. Archive a session once its
card is merged.

## When this session's context fills

Bring every open card's Progress and Next action up to date, commit and push, tell the user, and
archive this session. The next orchestrator starts at "Take over from the records". The git
records and each session's transcript remain; only this session's working memory is lost, so
anything not in a record or a pushed commit must be written down first.

## Boundary with the driver

`drive.py` (`stage-drive`) picks the next ready leaf by work id and runs it; it never gathers,
groups, orders, or asks the user. Use it for cards that are already registered, ready, and carry
acceptance checks; decide what those cards are, and in what order, here.

## Verify

- `python3 <stage-plugin-root>/scripts/audit_stage.py --project-root <project-root>` — no work
  item finding.
- Every card in `.stage/work/current/` maps to a listed session or to this session.
