# Handoff: W-00000002

## Purpose chain

### W-00000001

Make configuration parsing predictable for callers.

### W-00000002

Implement configuration parsing in two steps.

## Criteria as of check

These criteria were current at the reported check. Recheck before using them.

distill — generation: 2; checked_at: 2026-10-07T03:44:33.324202Z

### applies

- distill:CR-fbed97eb8cc7@2: Invalid configuration input returns None.
- targets: ["app/"]
- excluded: []
- source_status: not_checkable
- applies_when: [{"any": ["app/"], "kind": "path"}]
- exceptions: []
- notes: []
- overrides: []
- confirmation: "user_stated"
- ai_confidence: null
- origin: {"actor": "user", "captured_at": "2026-10-07T03:44:33.194509Z", "kind": "user_statement", "quote": "[Synthetic test statement] Invalid configuration input returns None.", "quote_sha256": "4942dfcd85366e7926b5ddea770b6832e605bf279386493260739fdccf7835cc", "recorded_by": {"host": "fixture", "session_id": "codex-to-claude-C2", "via": "cli"}, "source_ref": "session:fixture/codex-to-claude-C2/fixture-1", "source_sha256": null}

avatar — generation: 0; checked_at: 2026-10-07T03:44:33.375056Z

store: absent

No current criteria.

## Prior result evidence

{"kind": "file", "path": "app/port.py", "sha256": "742fb7d2523d9df0b93cf788cdbb4f3dd08b5ec9b387975458a1f8fe4a60bbe7", "observed_at": "2026-10-07T03:40:01.380845Z", "status": "matches", "current_sha256": "742fb7d2523d9df0b93cf788cdbb4f3dd08b5ec9b387975458a1f8fe4a60bbe7", "uncommitted": "unknown"}

## Stale judgments

- distill:CR-fbed97eb8cc7@1: superseded. Revisit non-current judgments; do not automatically undo work.

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

distill: ["/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/W-00000274-distill/plugins/distill/.venv/bin/python", "-m", "distill", "criteria", "check", "--project", "test/demo-app", "--refs", "distill:CR-fbed97eb8cc7@2", "--db", "/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/criteria-real-handoff-d_2gh3zp/codex-to-claude-C2/.data/distill.db"]

## Remaining work

### Success criteria

- Valid ports and hosts are parsed.

### Next action

Implement parse_host.
