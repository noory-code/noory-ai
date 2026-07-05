---
name: rag-reindex
description: Re-chunk and re-extract entities from only the changed files, then load them into the vector/graph. Example utterances "rag reindex", "rag update", "rag-reindex", "reflect the changed documents", "refresh the index".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.2.0"
---

# rag-reindex — reindex the changes

## What

After walking `sources` in `.noory/rag/settings.json`, it processes only the files changed against the manifest (added / changed / removed). **Chunking and entity/relation extraction are performed directly by the current Claude session**, and the results are passed to the MCP tool `rag_upsert_chunks`.

## Steps

1. **Precondition check**: call `rag_get_settings`. On an error ("settings not found"), guide the user to `/rag:init-rag`, then stop.

2. **Diff lookup**: call `rag_diff_files()` → `{ added, changed, removed }`.
   - If all three are empty, print "No changes. Index is up to date." and exit.

3. **Handle deletions**: call `rag_delete_file(path)` for each item in `removed`.

4. **Handle additions/changes**: iterate the `added + changed` list. For each file:

   a. Read the file content with the Read tool (for a PDF, the MCP extracts it). If it's too large, process it partially.
      - If it's an **image file** (png/jpg/jpeg/gif/webp): open the image with Read and **generate descriptive text of what it contains** — the composition/relations of a diagram, the items/figures of a chart, the UI/text of a screenshot, the characters of a scanned document, etc. — writing out the **searchable content** as prose. Treat this description as that file's "body" and apply b·c·d below to it just like text. Mark the generated chunks with `meta.source_type = "image"` to indicate their image origin (used by the search output). (rag has zero external keys — description generation is done directly by the current session.)

   b. **Chunking (Claude itself)**: split by semantic units. Guidelines:
      - Markdown: prefer H2/H3 heading boundaries; keep code blocks and tables whole
      - Plain text/PDF: paragraph boundaries, topic-shift points
      - Target 400 tokens per chunk, 800 tokens max, 100 tokens min
      - If there is a heading, preserve it in `meta.section`

   c. **Entity extraction (Claude itself)**: identify the following from the chunk text
      - libraries · services · tools · systems (type: `library`)
      - core concepts · patterns · terms (type: `concept`)
      - people · teams · organizations (type: `actor`)
      - files/modules/endpoints (type: `module`)
      Each entity: `id` (kebab-case stable identifier), `name` (original notation), `type`, `chunk_indices` (array of the chunk indices where it appeared).

   d. **Relation extraction (Claude itself)**: for entity pairs that co-occur in the same chunk or are explicitly connected in the body, make `{src_id, dst_id, type, weight}`. `type` examples: `USES`, `DEPENDS_ON`, `EXTENDS`, `RELATED_TO`. `weight` is the occurrence count or confidence.

   d2. **Contradiction handling (conflict = user's judgment)**: if you find **contradicting facts** (conflicting values / definitions / states) across chunks for the same entity, **do not automatically pick one**. Present both bits of evidence to the user and ask "which is the truth", and reflect only the confirmed fact in the index (exclude the rest or mark it as 'dissent'). This is a point where human judgment intervenes — do not silently overwrite.

   e. **Store**: `rag_upsert_chunks(file=<rel_path>, chunks=[…], entities=[…], relations=[…])`.

5. **Progress log**: report progress in one line every 5–10 files ("12/45 indexed, …").

6. **Summary output**:
   ```
   ✅ reindex complete
      added:   N1
      changed: N2
      removed: N3
      total chunks: …, entities: …  (result of the rag_stats call)
   ```

## When there's too much at once

If it exceeds 100 files, confirm with the user "Split into batches (recommended)? Or process all at once?" If batches are chosen, process 50 at a time with intermediate reporting.

## Error handling

- If one file fails during processing, continue with the rest. Report the failure list at the end.
- If `rag_upsert_chunks` returns a schema error → expose exactly which field is the problem, then skip that file.
