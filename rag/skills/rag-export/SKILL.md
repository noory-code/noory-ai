---
name: rag-export
description: Create a rag index snapshot tarball (vec.db + graph/ + manifest + settings + compatibility header). Example utterances "make a rag snapshot", "rag-export ~/Downloads/foo.tar.gz", "rag backup".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.1.0"
---

# rag-export — making a snapshot

## Steps

1. **Prerequisite check**: `rag_get_settings`.

2. **Determine output path**: extract path from the user's utterance. If none, default to `~/Downloads/rag-snapshot-<YYYYMMDD-HHMM>.tar.gz`.
   - If only a directory is given, auto-name the file inside it with the pattern above.
   - If a file with the same name already exists, confirm whether to overwrite.

3. **Call**: `rag_export(out_path=<resolved>)`.
   - The response includes header metadata (embedding model/dim/stats).

4. **Output the result**:
   ```
   📦 Snapshot created
      file:        <out_path>
      size:        <du -h>
      embedding:   <model> (dim <N>)
      stats:       files M, chunks N, entities P, ...
   ```

5. **Share guidance**: "Send this file to a teammate and they can receive it with `/rag:rag-import <path>`. For more detailed share scenarios: `/rag:rag-share-guide`."

## Error handling

- Not enough disk space, no write permission → report clearly.
- Even if the index is empty, export is possible (an empty snapshot with header only).
