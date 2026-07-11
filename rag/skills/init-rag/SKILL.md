---
name: init-rag
description: rag plugin initial setup (configure · start) — auto-creates the `.noory/rag/` directory, the `raw/` material store, `settings.json`, and the project `.gitignore`. A setup task that does not erase existing data. Example utterances "rag setup", "start rag", "rag config", "init-rag", "set up rag", "attach rag to the project". (For the initialization/reset that erases the index, use `rag-clear`.)
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# init-rag — rag initial setup

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

Creates a RAG index workspace (`.noory/rag/`) at the root of the project you are currently working on, and writes the default folder where the user will place material (`.noory/rag/raw/`) and the indexing policy (`settings.json`). If it is already set up, it says so and exits.

> The MCP server resolves the project root through the shared host contract. Behavior is identical on macOS, Linux, and Windows.

## Steps

1. **Status check**: call the MCP tool `rag_get_settings`.
   - On a normal response, print "Already initialized. Current settings: …" and exit (then guide to `/rag:rag-status`).
   - On a `settings not found` error, proceed to the next step.

2. **Source-candidate scan**: from the project root, glob for the following candidates and present only the ones that exist to the user.
   - `docs/`, `documentation/`, `notes/`, `wiki/`, `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md`
   - If any are found, use the host question tool to choose among `[candidates to add (multiSelect), use only .noory/rag/raw/]`.

3. **Write settings**: call `rag_set_settings`. Default payload:
   ```json
   {
     "sources": [
       { "path": ".noory/rag/raw/", "recursive": true,
         "include": ["**/*.md", "**/*.mdx", "**/*.txt", "**/*.pdf",
                     "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.webp"] }
     ],
     "embedding": { "provider": "local", "model": "intfloat/multilingual-e5-small", "dim": 384 },
     "chunking": { "target_tokens": 400, "max_tokens": 800, "min_tokens": 100 },
     "graph":    { "expand_depth": 2, "community_algo": "leiden" }
   }
   ```
   The candidates selected in step 2 are added to the `sources` array (same include pattern).

4. **gitignore guidance**: `rag_set_settings` builds even the `.noory/rag/` layout, but confirm with the user and add `.noory/rag/` to the project `.gitignore` via Edit.

5. **Material-store guidance output** (must include the following two sentences):
   - "Feel free to place PDFs · notes · external downloads in `.noory/rag/raw/` (subfolders OK)."
   - "💡 RAG is only as strong as the quality of the indexed material. Adding your company wiki · service specs · architecture docs · API references together greatly improves search quality."
   - "ℹ️ For usage, `/rag:rag-help`; for sharing, `/rag:rag-share-guide`."

6. **First-indexing offer**: via the host question tool, "Run the first `rag-reindex` now?" — on Yes, invoke the `/rag:rag-reindex` flow as-is.

## Output format

```
✅ rag initialization complete
   • settings: <path>
   • sources: <summary of the registered patterns>
   • embedding: intfloat/multilingual-e5-small (dim 384)
Next steps:
   1) Organize material in `.noory/rag/raw/`
   2) Run `/rag:rag-reindex`
   3) (recommended) Register 3–5 frequently asked questions with `/rag:rag-probe-add` →
      measure + tune index quality with `/rag:rag-evaluate`
```

## Error handling

- `rag_set_settings` returns schema invalid → show the user exactly which field is the problem and stop.
- `rag_set_settings` reports an unresolved project root → restart the active host. If it persists, reinstall `rag@noory-ai` with that host's plugin command from the shared contract.
- If the MCP server itself does not come up because `uv` is not installed, give per-OS install guidance:
  - macOS: `brew install uv`
  - Windows (PowerShell): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` or `winget install --id=astral-sh.uv -e`
  - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
