# Handoff: W-00000002

## Purpose chain

### W-00000001

Make configuration parsing predictable for callers.

### W-00000002

Implement configuration parsing in two steps.

## Criteria as of check

These criteria were current at the reported check. Recheck before using them.

distill — generation: 1; checked_at: 2026-10-07T03:40:18.698948Z

### applies

- distill:CR-d5be2ead99e6@1: Invalid configuration input raises ConfigError.
- targets: ["app/"]
- excluded: []
- source_status: not_checkable
- applies_when: [{"any": ["app/"], "kind": "path"}]
- exceptions: []
- notes: []
- overrides: []
- confirmation: "user_stated"
- ai_confidence: null
- origin: {"actor": "user", "captured_at": "2026-10-07T03:38:46.604447Z", "kind": "user_statement", "quote": "[Synthetic test statement] Invalid configuration input raises ConfigError.", "quote_sha256": "b2c5f9ae213ada4afde8c75876dd2ec8806bd10617965ee782f15b1b12bf4557", "recorded_by": {"host": "claude", "session_id": "sender-claude", "via": "cli"}, "source_ref": "session:claude/sender-claude/fixture-1", "source_sha256": null}

avatar — generation: 0; checked_at: 2026-10-07T03:40:18.761717Z

store: absent

No current criteria.

## Prior result evidence

{"kind": "file", "path": "app/port.py", "sha256": "9186926652fd50bca9a6c2389ce12e5112b4b659b8745c0cc05809016da1c5a8", "observed_at": "2026-10-07T03:38:59Z", "status": "matches", "current_sha256": "9186926652fd50bca9a6c2389ce12e5112b4b659b8745c0cc05809016da1c5a8", "uncommitted": "unknown"}

## Stale judgments

- distill:CR-d5be2ead99e6@1: eligible_current. Revisit non-current judgments; do not automatically undo work.

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

distill: ["/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill/.venv/bin/python", "-m", "distill", "criteria", "check", "--project", "test/demo-app", "--refs", "distill:CR-d5be2ead99e6@1", "--db", "/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/criteria-real-handoff-d_2gh3zp/claude-to-codex-C1/.data/distill.db"]

## Remaining work

### Success criteria

- Valid ports and hosts are parsed.

### Next action

Implement parse_host.
