---
name: rag-status
description: Report the current rag index status — file/chunk/entity/relation/community counts, embedding model, disk usage. Example utterances "rag status", "rag-status", "rag stats", "index status".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.1.0"
---

# rag-status — index status report

## Steps

1. **Prerequisite check**: call `rag_get_settings`. If `settings not found`, output "Not initialized yet. Run `/rag:init-rag` first." then exit.

2. **Collect stats**:
   - Call `rag_stats()` → counts / embedding info
   - Bash `du -sh .noory/rag/` for disk usage
   - Read `.noory/rag/manifest.json` if possible to extract the indexed file count and last modified time (mtime)

3. **Output format**:
   ```
   📊 rag status — <project root display>

   index
     files:       N
     chunks:      N
     entities:    N
     relations:   N
     mentions:    N
     communities: N

   embedding
     model:  intfloat/multilingual-e5-small
     dim:    384

   storage
     disk:   ~XYZ KB / MB
     vec.db: present/absent (sqlite-vec)
     graph/: present/absent (Kuzu)

   source policy (sources):
     - .noory/rag/raw/ (**/*.md, **/*.mdx, **/*.txt, **/*.pdf)
     - docs/ (...)

   last indexing (manifest.json mtime):  YYYY-MM-DD HH:MM
   ```

4. **Recommendations**: attach only the applicable items below in 1–3 lines
   - `chunks == 0` → "Put source material in `.noory/rag/raw/` and run `/rag:rag-reindex`."
   - `communities == 0` but `entities > 5` → "Never rebalanced → `/rag:rag-rebalance` recommended."
   - manifest mtime older than 7 days → "The material may have changed. `/rag:rag-reindex` recommended."

## Error handling

- The MCP server itself cannot run → guide uv installation + debug command `python -m rag_mcp --probe`.
