# Avatar

Avatar is a local CLI and host skill for reviewing explicitly recorded choices and
user-confirmed personal criteria. It keeps quoted reasons, provenance, versions, revocations, and
read-only Distill history projections in SQLite.

Avatar does not collect conversations automatically, infer personality, authenticate speakers, or
promote project exceptions into personal criteria. It works without Stage or Distill.

## Requirements

- Python 3.9 or newer
- No third-party packages

The default database is `~/.avatar/avatar.db`. Override it with `--home <directory>` or the
`AVATAR_HOME` environment variable. The database stays outside the plugin installation cache.

## Commands

Run commands from this repository with `python3 avatar/scripts/avatar.py`. From an installed host
plugin, resolve `scripts/avatar.py` from the plugin root.

```text
avatar choice add --idempotency-key <key> --payload-file <json>
avatar criterion propose --idempotency-key <key> --payload-file <json>
avatar criterion confirm <PC-id> --version <N> --idempotency-key <key> --payload-file <json>
avatar criterion revise <PC-id> --idempotency-key <key> --payload-file <json>
avatar criterion revoke <PC-id> --idempotency-key <key> --payload-file <json>
avatar source attach --idempotency-key <key> --file <distill-history.json>
avatar show [--choice <CH-id> | --criterion <PC-id>] [--json]
avatar export
avatar check --refs <avatar-ref,...>
```

All mutating commands require an idempotency key. Replaying the same request returns the original
result with `replayed: true`. Reusing the key for different content returns
`E_IDEMPOTENCY_CONFLICT` and writes nothing.

Confirmation creates a new immutable version and returns its ref. For example, confirming
proposal `@1` returns confirmed version `@2`. Use the returned ref. Revision creates a new
unconfirmed proposal; it does not reuse the earlier user's confirmation as its source.

## Data boundaries

- `CH-` records belong to Avatar and describe one explicit choice.
- `PC-` records belong to Avatar and describe versioned personal criteria.
- Distill `CR-` history is stored as a read-only projection. `show` labels it historical and does
  not claim that it is current.
- `export` emits `criteria-snapshot/1` with `scope: personal`. It includes only the current
  `user_confirmed` versions.
- `check` returns `eligible_current`, `proposed`, `superseded`, `revoked`, `scope_mismatch`, or
  `unknown`. Consumers must apply only `eligible_current` refs.

## Development

Run the package suite from the repository root:

```bash
python3 -m unittest discover -s avatar/tests -q
python3 -m unittest tests.test_plugin_contracts -q
```
