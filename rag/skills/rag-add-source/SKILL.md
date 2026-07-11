---
name: rag-add-source
description: Add an indexing source — add it to settings.json `sources` and immediately do a partial index. Utterance examples "rag add source docs/", "rag-add-source notes/", "register wiki/ in rag".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-add-source — add a source

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## Steps

1. **Precondition check**: call `rag_get_settings`. If absent, guide to `/rag:init-rag` and stop.

2. **Path parsing**: extract the path (or a single file) from the user's utterance.
   - Absolute path or a relative path from the project root
   - For a directory, `recursive: true`; for a single file, `recursive` is ignored
   - Existence check: Bash `test -e <path>`. If absent, confirm with the user → create it / stop.

3. **include/exclude**: default is `["**/*.md", "**/*.mdx", "**/*.txt", "**/*.pdf", "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.webp"]`.
   If the user gives a hint like "code too", "ts/js", "py", expand accordingly.
   Confirm once with the host question tool:
   - Markdown·text·PDF·image (default)
   - Include code too (`**/*.py`, `**/*.ts`, …)
   - User-specified

4. **Duplicate check**: if the same path already exists in the current settings.sources, ask whether to update that entry before proceeding.

5. **Update settings**: take the `rag_get_settings` result, add/update the new entry in the sources array → `rag_set_settings(settings)`.

6. **Partial indexing**: call `rag_diff_files(source_path=<the path>)`. Process only the resulting added/changed (same method as `/rag:rag-reindex` step 4).

7. **Result summary**:
   ```
   ✅ Source added: <path>
      include: ...
      Newly indexed: N files / N chunks
   ```

## Error handling

- If the path leaves the project root, reject it (e.g., `../etc/`). Safety reason.
- If a glob pattern is too broad and matches 1000+ files, warn the user and confirm whether to proceed.
