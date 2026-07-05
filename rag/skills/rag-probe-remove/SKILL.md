---
name: rag-probe-remove
description: Remove a rag evaluation question (probe) — delete an item by ID from `.noory/rag/probes.json`. Example utterances "remove probe", "delete the auth-flow probe", "drop this question", "rag-probe-remove".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.1.2"
---

# rag-probe-remove — remove an evaluation question

## What

Remove one (or several) of the registered probes from `.noory/rag/probes.json`.

## Steps

1. **Grasp user intent**:
   - If the user specifies an ID ("delete the auth-flow probe"), use it as-is.
   - If not specified, show the list via `rag_get_probes` and receive a multiSelect choice via AskUserQuestion.

2. **Existence check**: confirm the given ID actually exists in the `rag_get_probes` result. If not:
   ```
   ⚠️ probe id "<x>" is not registered. Current list:
   <table>
   ```
   then finish.

3. **Update call**: full replace via `rag_set_probes` with a new list that excludes the given IDs from the existing list.

4. **Confirmation output**:
   ```
   🗑️ probe removed: <id>
   N total remaining.
   ```

## Error handling

- probes.json corrupted → notify the user and finish (no arbitrary overwrite).
- `RAG_PROJECT_ROOT unset` → guide a Claude Code restart.
