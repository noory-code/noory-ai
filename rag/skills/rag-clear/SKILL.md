---
name: rag-clear
description: Destructive reset/wipe that clears the rag index·graph·cache. settings.json is preserved (optionally delete it if desired). Example utterances "clear rag", "reset rag", "delete rag index", "rag-clear", "start over from scratch", "wipe rag". (The non-deleting first-time setup·start is `init-rag`.)
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-clear — index reset

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## ⚠️ Destructive action

Deletes `.noory/rag/vec.db`, `.noory/rag/graph/`, `.noory/rag/manifest.json`, `.noory/rag/cache/`. `.noory/rag/raw/` and `.noory/rag/settings.json` are preserved by default.

## Steps

1. **Show current state**: print the `rag_stats()` result in one line → the user knows what they are losing.

2. **First confirmation**: the host question tool
   - Options:
     - Delete index only (default, preserve settings/raw) — **recommended**
     - Delete index + all raw/ material
     - Delete settings.json too (full reset)
     - Cancel

3. **Second confirmation**: if "delete all" or "full reset" was chosen in the first, confirm once more with "Really delete? This cannot be undone."

4. **Execute deletion** (Bash):
   ```bash
   rm -f  .noory/rag/vec.db .noory/rag/manifest.json
   rm -rf .noory/rag/graph .noory/rag/cache
   ```
   For "delete all", add:
   ```bash
   rm -rf .noory/rag/raw && mkdir -p .noory/rag/raw && touch .noory/rag/raw/.gitkeep
   ```
   For "full reset", add:
   ```bash
   rm -f .noory/rag/settings.json
   ```

5. **Print result**:
   ```
   ✅ rag-clear complete
      Deleted: vec.db, graph/, manifest.json, cache/
      Preserved: settings.json, raw/
   Next step: `/rag:rag-reindex` (or, if you also emptied raw/, place the material again and reindex).
   ```

## Safety guards

- If `rag_stats()` is all 0, print "Already empty. Leaving it as is." and exit.
- Since the MCP server may hold a handle on vec.db, ideally the MCP side auto-handles the case where `_State.reset()` must be called before deletion, but in v0.1 the user's re-invocation shortly after auto-reopens with a new handle.
