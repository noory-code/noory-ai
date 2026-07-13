---
name: stage-discuss
description: |
  Start or continue an asynchronous file-based discussion between different LLM sessions.
  The user carries the discussion file to each LLM, so use this to accumulate multiple
  models' perspectives in one thread without any API connection.
---

# Stage Discuss

Use this skill when multiple LLMs discuss one topic through files.

## Premises

- Participants are LLMs in different sessions or hosts. The only shared medium is the file.
- The user delivers the discussion file to each participant. Participants never talk directly.
- A discussion file is a work-in-progress artifact, not official truth.

## Discussion file location

- Place it under `.discuss/` at the root of the component under discussion.
- Exclude `.discuss/` from git tracking; register it in `.gitignore` if missing.
- Name files `<topic>-YYYY-MM-DD.md`. One topic, one file.

## File structure

```markdown
# <topic>

- Status: open | settled | closed
- Participants: <author(host)> list
- Settle criterion: user confirmation

## Round 1 — <author> (<host>) — YYYY-MM-DD

### Points
- P1: <claim> — evidence: <file:line / reproduction / source>
- P2: ...

### Questions for the other side
- ...

## Round 2 — <author> (<host>) — YYYY-MM-DD

### Responses
- P1 agree: <reason>
- P2 refute: <evidence>
- P3 hold: <what is still needed>

### New points
- P4: ...

### Questions for the other side
- ...
```

## Procedure: starting a discussion

1. Check that `.discuss/` exists and is gitignored.
2. Create the topic file and fill the header (status, participants, settle criterion).
3. Write the points in Round 1 with a `P<n>` ID per point.
4. Attach evidence to each point — file paths with line numbers and reproduced commands first.
5. State the questions for the other side and tell the user the file path.

## Procedure: responding to a discussion

1. Read the whole file. Never answer from the last round alone.
2. Take an explicit position on every open point: agree, refute, or hold. Silence is not a response.
3. Write refutations and new claims only after verification. Read code and documents directly;
   reproduce whatever is reproducible. Mark what cannot be verified as "unverified — presumed".
4. Append a new round at the end of the file. Never modify previous rounds.
5. Update the header status and list the questions for the other side.

## Procedure: after finishing a round (handoff)

When the round is written, print a handoff prompt the user can paste into the other LLM as-is.

```text
Follow the procedure in <skill path from repo root>/SKILL.md,
read the whole discussion at <discussion file path from repo root>, and respond as Round <next number>.
Sign as: <responder name> (<host>).
```

- Use repo-root-relative paths. If the other session's working directory differs, confirm with the user.
- The other side does not need the skill installed; reading SKILL.md shares the same procedure.
- The user does the delivery. Assume nothing outside the file reaches the other side — put all
  context needed for a response inside the discussion file.

## Rules

- Sign every round with author, host, and date.
- Always reference points by `P<n>` ID. Never restate the same claim in different words.
- Previous rounds are append-only. If a position changes, state it in a new round with the reason.
- When summarizing the other side's point, cite the original round number.

## Settling and promotion

1. The user decides when a discussion settles. Participating LLMs only propose settlement candidates.
2. A settled conclusion is promoted to truth, not left in the discussion file —
   `.stage/official/decisions/` when the project has the harness, otherwise the component's design document.
3. After promotion, set the file status to `settled` and link the promoted location. The user decides
   whether to delete the file.
4. If the discussion stops without a conclusion, set status `closed` and summarize the remaining
   open points under the header.
