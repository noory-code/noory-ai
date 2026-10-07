# Handoff packet

`scripts/handoff_packet.py` carries a work card's purpose, fresh criteria, prior evidence, and
remaining work into another session. It reads current Stage cards and calls public producer CLIs.
It neither imports other plugins nor opens their databases.

## Inputs

```text
python3 stage/scripts/handoff_packet.py --project-root <root> W-00000003 \
  --project-key example/app --producers <local-producers.json>
```

The project key must match the key used to record Distill criteria. Producer configuration is
local caller input. Resolve the executable with the host's executable lookup before writing it.
Each `argv` is an array; its first element must be an absolute executable path on that host.

```json
{
  "distill": {
    "argv": ["/absolute/path/to/uv", "run", "--directory", "/path/to/distill", "python", "-m", "distill"],
    "db": "/path/to/criteria.db"
  },
  "avatar": {
    "argv": ["/absolute/path/to/python3", "/path/to/avatar/scripts/avatar.py"],
    "home": "/path/to/avatar-data"
  }
}
```

Use Windows paths for Windows. Spaces remain part of an argument. Commands run with no shell
and a 30-second timeout. `db` and `home` are optional; when omitted, the producer uses its own
default. No snapshot-file input is accepted. An omitted producer is marked as not queried.

## Evidence in Progress

Record one JSON object per line in the card's `## Progress`:

```text
Applied criteria: distill:CR-aaaaaaaaaaaa@2
Condition judgment: distill:CR-aaaaaaaaaaaa@2 path=app/config.py -> applies
Evidence: {"kind":"file","path":"app/config.py","sha256":"<64 hex>","observed_at":"<UTC time>"}
Evidence: {"kind":"check","command":"python -m pytest -q","exit":0,"result":"3 passed","observed_at":"<UTC time>"}
```

The packet rehashes files and reports uncommitted changes. It reports missing or changed files
without claiming completion. Recorded commands are displayed and never executed by the packet.
Run the card's acceptance commands and independent review separately.

## Conditions and sources

Path conditions accept repository-relative files or directories ending in `/`. Conditions combine
with AND; values in `any` combine with OR. An exception excludes matching targets. A narrow
overlap produces `partial`, with targets and exclusions. Reclassify the actual file before use.
Notes require an explicit judgment for every note. Unknown conditions and unsafe paths remain
`unresolved`.

Stage card scopes retain Stage's prefix semantics: `app` includes `app/config.py`, and `*`
means the whole project. Producer path conditions still use `/` to distinguish a directory.
An unsuffixed producer path that names a directory or is an ancestor of a scope or condition path
is ambiguous and remains `unresolved`, even before the directory exists. A directory-marked path
that names an existing file is also unresolved. Existing file scopes keep file targets. Unknown scope
paths retain Stage's prefix semantics; `.` is invalid and never means the whole project.
When a partial scope also has notes, narrow to the actual file first, then satisfy every note.
Progress records may be plain lines, bulleted lines, or lines prefixed with an ISO date. An
unrecognized prefix or malformed criterion ref is reported as an unparsed record.
`Applied criteria: none` remains explicit.

For `stage:` sources, compare the project key before reading a path. Reject absolute paths,
parent traversal, and symlinks that escape the project. Hash the referenced H2 body as UTF-8
after normalizing line endings to LF and stripping its outer whitespace. Headings inside code
fences do not end the section. The packet reports `matches`, `changed`, `missing`,
`rejected_ref`, or `not_checkable`. A changed, missing, or rejected Stage source makes its
criterion unresolved. `matches` attests only to unchanged text, not to its correctness.

## Freshness and errors

`generation` and `checked_at` describe the producer's query, not a lasting guarantee. Before each
criterion-dependent choice, execute its supplied check argv and require `eligible_current`.
On any other status or command failure, refresh the packet or defer that choice.

- Missing producer: exit 0, explicitly not queried.
- Failed, timed-out, or malformed producer response: exit 0, explicitly unavailable; no old criteria.
- Invalid configuration: exit 2, `E_PRODUCERS_INVALID`, no packet.
- Wrong snapshot scope: exit 2, `E_SCOPE_MISMATCH`, no packet.
- Multiple current versions of one criterion: exit 2, `E_VERSION_CONFLICT`, no packet.

Use current user instructions, project purpose, then user-backed explicit overrides to resolve
conflicts. Ask only when the remaining conflict blocks progress. Preserve prior applied refs as
history; a stale ref calls for review and does not automatically undo completed work.
