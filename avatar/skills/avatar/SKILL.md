---
name: avatar
description: This skill should be used when the user asks to "record this choice", "show why I chose this", "review my personal criteria", "change my criterion", "revoke my criterion", "compare choices", or explicitly mentions Avatar choice or criterion history.
---

# Avatar

Keep choices and user-confirmed personal criteria in a local, inspectable record. Preserve the
quoted reason, source reference, host, and session supplied by the current conversation. Never
claim that Avatar authenticates the speaker or proves the source is still current.

Resolve `../../scripts/avatar.py` relative to this file. In the source checkout, use
`avatar/scripts/avatar.py`. Run it with the active Python 3.9 or newer interpreter. Store data in
`~/.avatar/avatar.db` by default. Honor `--home` or `AVATAR_HOME` when the user supplies an
alternate location.

## Safety rules

- Record only after the user asks to save a choice or criterion-related action.
- Quote the user's words without rewriting them in `origin.quote` and `reason_quote`.
- Set `origin.actor` to `user` only for an actual user statement in the current conversation.
- Record the current host and session in `origin.recorded_by`; do not describe that metadata as
  identity verification.
- Keep project exceptions as choices or source projections. Do not turn them into a personal
  criterion without a separate `criterion confirm` action backed by a user quote.
- Treat every Distill projection as historical evidence. Use Distill itself to check whether a
  projected criterion is current.
- Reuse one `idempotency_key` only for an exact retry. Use `<host>:<session_id>:<sequence>` when
  the host exposes those values.

## Record a choice

Build a JSON file with `question`, `options`, `chosen`, `reason_quote`, `context`, `origin`, and
`source_refs`. Include the project key and any known `path` or `work_kind` conditions. Then run:

```text
python3 <avatar-plugin-root>/scripts/avatar.py choice add \
  --idempotency-key <host>:<session>:<sequence> --payload-file <payload.json>
```

Report the returned `CH-` ID. If the command returns `E_IDEMPOTENCY_CONFLICT`, create a new key
only when this is a new action; do not hide an accidental payload change by retrying with a new
key.

## Review records

Run `show` for the full local record, or narrow it with `--choice CH-...` or
`--criterion PC-...`. Add `--json` when another program or skill will consume the output.

Present choices with their quoted reasons and sources. Present all criterion versions and change
reasons. When Avatar reports a review candidate, say that the choices differ. If their conditions
differ, keep that fact visible and do not label the pair a contradiction.

## Propose and confirm a personal criterion

Use `criterion propose` for an AI-authored candidate. Include `statement`, `applies_when`,
`exceptions`, `notes`, `overrides`, `ai_confidence`, and `from_choices`. A proposal is not current
and `check` returns `proposed`.

Ask the user to confirm the exact proposal before running `criterion confirm`. Put the confirming
statement in an `origin` object and pass the proposed ID and version:

```text
python3 <avatar-plugin-root>/scripts/avatar.py criterion confirm PC-... --version 1 \
  --idempotency-key <key> --payload-file <confirmation.json>
```

Confirmation creates the next immutable version and returns its new ref. Keep the proposed
version as history. Only the new `user_confirmed` ref can appear in `export` as eligible.

## Revise or revoke

Use `criterion revise` with the current `base_version`, changed fields, and a non-empty `reason`.
The new version is a proposal. Confirm it separately before treating it as current.

Use `criterion revoke` with the current `base_version`, a user `origin`, and a non-empty `reason`.
Keep revoked versions in history. Do not recreate the same criterion silently.

## Attach Distill history

Receive the JSON output of Distill `criteria history` in a file. Attach it with:

```text
python3 <avatar-plugin-root>/scripts/avatar.py source attach \
  --idempotency-key <key> --file <distill-history.json>
```

Stop on `E_PROJECTION_CONFLICT`. It means a known version changed, one generation has two
different histories, or a newer history removed an earlier event. A lower generation may be kept
as historical evidence, but it must not replace the newest projection.

## Export and check

Run `export` to produce `criteria-snapshot/1` for Stage or another consumer. It includes only
confirmed current personal criteria. Run `check --refs avatar:PC-...@N,...` immediately before a
choice that depends on those refs. Apply only refs whose status is `eligible_current`.

Treat `proposed`, `superseded`, `revoked`, `scope_mismatch`, and `unknown` as ineligible. Request
fresh user direction when the work cannot continue without an ineligible criterion.
