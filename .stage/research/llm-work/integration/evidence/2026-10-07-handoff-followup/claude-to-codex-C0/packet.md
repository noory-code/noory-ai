# Handoff: W-00000002

## Purpose chain

### W-00000001

Make configuration parsing predictable for callers.

### W-00000002

Implement configuration parsing in two steps.

## Criteria as of check

These criteria were current at the reported check. Recheck before using them.

distill: Criteria were not queried; absence is not established.

avatar: Criteria were not queried; absence is not established.

## Prior result evidence

{"kind": "file", "path": "app/port.py", "sha256": "9186926652fd50bca9a6c2389ce12e5112b4b659b8745c0cc05809016da1c5a8", "observed_at": "2026-10-07T03:38:59Z", "status": "matches", "current_sha256": "9186926652fd50bca9a6c2389ce12e5112b4b659b8745c0cc05809016da1c5a8", "uncommitted": "unknown"}

## Stale judgments

- distill:CR-d5be2ead99e6@1: unknown (not queried). Revisit non-current judgments; do not automatically undo work.

## Decision order

Follow the user's current explicit instruction. Start with the purpose chain.
When purpose answers the question, proceed. Otherwise use criteria classified as applies.
For partial criteria, classify the actual file again and record
`Condition judgment: <ref> path=<file> -> applies` before applying it to that file.
If that file still needs note judgments, record its narrowed path as needs_judgment and satisfy
every note before applying it. A partial scope never removes the note requirements.
For needs_judgment, first satisfy all code-checkable conditions, then record each note as
`Condition judgment: <ref> note="<original note>" -> met|not_met because <reason>`.
Every note must be met. Never apply unresolved or not_applicable criteria.
Resolve conflicting criteria through the current user instruction, then project purpose,
then explicit overrides supported by a user quote. If none resolves the conflict, defer that
choice. Ask the user only when missing information prevents progress, and state what is missing.
Immediately before each choice that depends on a criterion, run its check command below.
Record `Applied criteria: <ref>, <ref>` in the card's Progress, or `Applied criteria: none`.
Prior evidence does not replace acceptance checks or independent review.

## Check before each criterion-dependent choice

Run each JSON argv array without a shell. Apply a criterion only when its status is eligible_current.
Any other status, non-zero exit, or timeout: do not apply it. Refresh the packet or defer that choice.

No applicable criteria have a check command in this packet.

## Remaining work

### Success criteria

- Valid ports and hosts are parsed.

### Next action

Implement parse_host.
