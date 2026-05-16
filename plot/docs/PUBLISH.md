# PUBLISH — Plot per-node publish reference

> Companion to [`SPEC.md` §Publish](./SPEC.md#publish-v0180) and
> [`D-2026-05-16-E`](./DECISIONS.md). This document is the
> reference for **what publish writes to disk** and **how to
> recover from a misclick** until the automated Unpublish button
> ships.

---

## What publish writes

Each click of the **📤** button in the Inspector header (after the
confirm dialog), Plot atomically performs:

1. Bumps the node's ``version`` MAJOR component (``v1.0 → v2.0``;
   MINOR resets to ``0``). Phase 4 will introduce MINOR
   propagation up the ancestor chain.
2. Renders a per-node MD file at
   ``<project_id>/<canvas>/published/{kind}-{slug}-{version}.md``.
3. Writes the bumped ``canvas.json`` via the regular atomic-write
   path.
4. Creates a git commit in the project's git repo
   (``.plot/<project_id>/.git``) with **5 ``Publish-*:`` trailers**
   that Phase 4 reads as the MINOR-propagation contract.

The bumped canvas + new MD file land in the same commit; there is
no intermediate state visible to the next reader.

---

## MD file format (uniform across 15 kinds)

YAML frontmatter (7 keys in fixed order) + one ``## Heading`` per
declared typed field on the per-kind Pydantic class.

```markdown
---
id: msn_xyz789
kind: mission
version: v2.0
label: Tolerance
parent_id: null
canvas: foundation
published_at: 2026-05-16T15:42:11+00:00
---

## What we do

We listen first.

## Why

To preserve diverse opinions.

## Direction

Listen → respond → reflect.

## Body

Free-form rationale paragraph.
```

### Field rendering rules

| Field type | Rendered as |
|---|---|
| ``str`` (typed text / MD-syntax) | verbatim under the H2 heading |
| ``int`` / ``float`` / ``bool`` | scalar token under the H2 heading |
| ``dict`` / ``list`` | inline YAML under the H2 heading |
| ``None`` | empty body (heading present, no text) |

Empty fields still emit the heading. This keeps the per-kind MD
shape stable across publish versions — diffs only show the typed
content that actually changed, never the headings.

### Slug derivation

The ``{slug}`` portion of the filename comes from the node's
``label`` via ``plot_mcp.slug.slugify``. Korean / CJK characters are
preserved verbatim; ASCII letters/digits are lowercased; everything
else collapses to a single dash. Empty labels fall back to
``untitled``.

### Phase 3 known limitation

Two nodes with the same label on the same canvas would collide on
the same MD filename. Phase 3 does not disambiguate via short-id
suffix; the per-version differentiator handles the per-node history
correctly, but cross-node collisions need Phase 5's folder
hierarchy fix. If you hit this in real use before Phase 5, raise it
as a follow-up D-entry.

---

## Git commit format

```
publish: mission "Tolerance" → v2.0

Publish-Node-Id: msn_xyz789
Publish-Kind: mission
Publish-Canvas: foundation
Publish-Version-From: v1.0
Publish-Version-To: v2.0
```

- **Subject** is human-readable. Label is double-quoted as-is.
- **Trailers** are the machine contract. Phase 4 (MINOR
  propagation) reads them via ``git interpret-trailers``. The
  subject is allowed to break under exotic labels; the trailers
  must not.

Query publish history with:

```bash
git -C .plot/<project_id> log --grep "^Publish-Node-Id:"
```

---

## `published/` directory semantics

- The server **only writes** to ``published/``. It never modifies
  or deletes existing files.
- Successive publishes of the same node accumulate as
  ``-v2.0.md`` / ``-v3.0.md`` / etc. The full per-node history
  lives in this folder and in git.
- Users editing files inside ``published/`` is allowed —
  git tracks the change — but the **SSOT remains
  ``canvas.json``**, not the published MD. Manual edits inside
  ``published/`` will be overwritten on the next publish of the
  same node + version pair (which by always-bump rule should not
  recur).

---

## Recovery from a misclick (manual; Phase 3 limitation)

If you didn't mean to publish, undo by hand:

1. Identify the offending commit:

   ```bash
   git -C .plot/<project_id> log --oneline -3
   ```

   The most recent ``publish: …`` commit is the one to revert.

2. Revert it:

   ```bash
   git -C .plot/<project_id> revert HEAD --no-edit
   ```

   This restores the bumped ``canvas.json`` field back to its
   prior value **and** removes the MD file (the revert reverses
   both the ``add`` of the MD and the canvas mutation).

3. Verify in the Inspector:

   Refresh the viewer; the version badge should read the pre-
   publish version, and the ``published/`` folder should no
   longer contain the ``-vN.0.md`` file.

If step 3 still shows the new version, the revert may have left
the file on disk; ``rm`` it manually:

```bash
rm .plot/<project_id>/<canvas>/published/<kind>-<slug>-<version>.md
```

### v0.18.x follow-up

An automated **Unpublish** button on the Inspector is queued as a
follow-up in [`NEXT_SESSION.md`](./NEXT_SESSION.md). It will
encapsulate steps 1–3 above into one user action.

---

## What publish does NOT do

- Does **not** propagate to ancestor nodes (Phase 4's job).
- Does **not** trigger any other node's version to change.
- Does **not** push to a remote git (the project's git repo is
  local-only; remote sync is a future ROADMAP item).
- Does **not** create a git tag (tags stay reserved for the
  user-named ``세션 기록…`` session-bookmark flow).
- Does **not** auto-fire on save. Publish is an explicit user
  gesture; auto-publish is rejected by D-2026-05-16-E ("user
  controls every line" principle from PHILOSOPHY).
