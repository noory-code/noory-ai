---
name: rag-import
description: Apply a snapshot tarball sent by a colleague to the current project's `.noory/rag/`. Auto-verifies compatibility. Example utterances "load the rag snapshot …", "rag-import ~/foo.tar.gz", "get the team index".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-import — snapshot restore

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## Steps

1. **Input path**: extract the tarball path from the user's utterance. If absent, the host question tool. Confirm it exists.

2. **Pre-backup notice**: if the current `.noory/rag/` is not empty, confirm "The existing index will be backed up to `.noory/rag.bak-<ts>/` then replaced. Proceed?".

3. **Call**: `rag_import(in_path=<path>, mode="replace")`.
   - If the response is `ok=false`, show the error message (embedding model/dimension/version mismatch, etc.) to the user as-is. Coping guidance:
     - dim mismatch: set settings.embedding.dim to the snapshot dimension, or import in a new project
     - model mismatch: the snapshot was made with a different embedding model, so it is incompatible
     - plugin_version major mismatch: the plugin version gap is too large

4. **Result output**:
   ```
   ✅ rag-import complete
      from:        <in_path>
      embedding:   <model> (dim <N>)
      restored stats: files M, chunks N, entities P, ...
      backup:      .noory/rag.bak-<ts>/ (deletable if not needed)
   ```

5. **Next-step suggestion**: "To reflect changes, run `/rag:rag-reindex` (if the source material changed after the snapshot)."

## Safeguards

- v0.1 supports only `mode="replace"`. merge is under review for v0.1.1 — if the user requests merge, guide them with a refusal message.
- Backup is automatic. Always back up unless the user explicitly says "without backup".
</content>
