---
name: rag-remove-source
description: Remove an indexing source — take it out of settings and clean up the chunks/entity mentions belonging to that source. Example utterances "rag remove source docs/legacy", "rag-remove-source notes/", "drop wiki/ from rag".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-remove-source — remove a source

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## Steps

1. **Prerequisite check**: `rag_get_settings`.

2. **Path matching**: extract the path from the user's utterance. Check whether the same path exists in settings.sources.
   - If not, show the possible candidates, then end.
   - If several, pick the closest one, then confirm with the user.

3. **Assess the impact scope**:
   - Confirm the currently matched file list via `rag_diff_files(source_path=<the one>)` (or prefix-match from the manifest).
   - Confirm with the host question tool: "N files are indexed from this source. Delete them all?"

4. **Delete loop**: call `rag_delete_file(path)` for each matched file.

5. **Update settings**: `rag_set_settings` with the settings minus that sources entry.

6. **Orphan-entity cleanup (optional)**: use `rag_list_entities()` to check whether any entity now has 0 mentions. If so, show it to the user and, if the user agrees, lightly run the `rag_rebalance_prep`/`commit` flow or just leave it.

7. **Result summary**:
   ```
   ✅ Source removed: <path>
      Files deleted: N
      Current stats: …
   ```

## Safeguards

- `.noory/rag/raw/` is the default source, so confirm once more when removing it. (If raw/ is dropped from sources, material the user placed directly is no longer indexed — check that this is the intent.)
- A bulk deletion that wipes everything at once (100+ files) requires two user confirmations.
