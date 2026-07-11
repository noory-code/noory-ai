# rag — Local GraphRAG plugin for Claude Code and Codex

Per-project RAG. Runs **vector + graph (GraphRAG) hybrid** search locally with no external API key. First-class support on **both macOS · Windows**.

## One-line concept

The active Claude Code or Codex session chunks and extracts entities from PDFs, notes, and documents placed in `.noory/rag/raw/` → the MCP server computes local embeddings and stores everything in sqlite-vec + Kuzu → it provides semantic search only when explicitly invoked. **A built-in evaluation flow lets you register the questions users frequently ask (probes) to measure and tune index quality.**

```mermaid
flowchart LR
  raw[.noory/rag/raw material] --> skill[rag-reindex skill]
  skill --> agent[Active AI session<br/>chunk · entity extraction]
  agent --> mcp[rag MCP server]
  mcp --> vec[(sqlite-vec<br/>vec.db)]
  mcp --> graph[(Kuzu<br/>graph/)]
  query[rag-search / rag-evaluate] --> mcp
  mcp --> result[search · evaluation result]
```

- **Embedding**: local `intfloat/multilingual-e5-small` (Korean OK, 384 dimensions, ~120MB download on first use)
- **Image-content search**: Claude turns screenshots/diagrams/scanned documents into descriptive text and indexes them identically to text material (not visual similarity — search the *meaning inside* the picture)
- **Importing external documents**: use installed official connectors (Confluence · Drive · Notion) to scrape documents into local storage and index them — rag holds no keys, it only uses them (`/rag:rag-fetch-external`)
- **Vector DB**: `sqlite-vec` → `.noory/rag/vec.db`
- **Graph DB**: embedded `Kuzu` → `.noory/rag/graph/`
- **No automation**: operates only when the user invokes a slash skill
- **Share policy**: `.noory/rag/` is gitignored by default. Sharing is explicit opt-in (`/rag:rag-share-guide`). Personal evaluation questions (`probes.json`) are automatically excluded from sharing.
- **OS compatibility**: the code uses only stdlib (`pathlib` / `os.environ`), and every native dependency has a win_amd64 wheel.

## Install

### Claude Code

```text
/plugin marketplace add noory-code/noory-ai
/plugin marketplace update noory-ai
/plugin install rag@noory-ai
```

### Codex

```text
codex plugin marketplace add noory-code/noory-ai
codex plugin add rag@noory-ai
```

### Prerequisite: `uv` (Python package manager)

| OS | Install command |
|---|---|
| **macOS** | `brew install uv` |
| **Windows (PowerShell)** | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` (or `winget install --id=astral-sh.uv -e`) |
| **Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

- Python 3.11+ is managed automatically by uv
- About 500MB of disk (dependencies + embedding model)

### Recommended: MCP timeout env

rag has MCP operations that can take a while, such as the first dependency install, embedding-model download, and bulk indexing. Set a generous timeout in the `env` of your Claude Code project settings (`.claude/settings.json`).

```json
{
  "env": {
    "MCP_TIMEOUT": "60000",
    "MCP_TOOL_TIMEOUT": "120000"
  }
}
```

These values are Claude/MCP client timeout settings. The `env` in `rag/.mcp.json` serves a different purpose — it passes `RAG_PROJECT_ROOT` to the MCP server process.

## Quick start

Up to a basic search (4 steps):

```text
/rag:init-rag           # creates .noory/rag/ + raw/ + settings.json, auto-updates .gitignore
# (place PDFs/notes/material directly in .noory/rag/raw/)
/rag:rag-reindex        # Claude chunks and extracts entities, then stores
/rag:rag-search "What is the project's authentication flow?"
```

Up to quality measurement/tuning (+2 steps, recommended):

```text
/rag:rag-probe-add      # register 3-5 frequently asked questions (e.g. "auth flow", "payment state diagram")
/rag:rag-evaluate       # batch-run the registered questions + Claude diagnoses weaknesses · proposes tuning
```

Detailed usage: `/rag:rag-help`. Team sharing: `/rag:rag-share-guide`.

## The 20 skills

| Skill | One line |
|---|---|
| `/rag:init-rag` | initial setup |
| `/rag:rag-reindex` | reindex the delta |
| `/rag:rag-rebalance` | tidy aliases · communities |
| `/rag:rag-search` | hybrid search |
| `/rag:rag-status` | status report |
| `/rag:rag-add-source` | add a source |
| `/rag:rag-fetch-external` | fetch and index documents via an external connector |
| `/rag:rag-feedback` | record 👍/👎 feedback on search results |
| `/rag:rag-feedback-report` | aggregate feedback · weakness report |
| `/rag:rag-remove-source` | remove a source |
| `/rag:rag-explore` | N-hop graph exploration |
| `/rag:rag-clear` | reset the index |
| `/rag:rag-export` | create a snapshot |
| `/rag:rag-import` | restore a snapshot |
| `/rag:rag-help` | usage guide |
| `/rag:rag-share-guide` | team-sharing guide |
| `/rag:rag-probe-add` | register a pre-set question for evaluation |
| `/rag:rag-probe-list` | list registered questions |
| `/rag:rag-probe-remove` | remove a question |
| `/rag:rag-evaluate` | evaluate index quality with registered questions |

## Architecture

```
rag/
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .codex-plugin/plugin.json    # Codex manifest (preserves workspace cwd for the MCP server)
├── .mcp.json                # MCP server registration (uv run)
├── server/
│   ├── pyproject.toml
│   ├── src/rag_mcp/
│   │   ├── domain/          # models + ports (0 dependencies)
│   │   ├── application/     # use cases (indexing/search/rebalancing)
│   │   ├── infrastructure/  # adapters (sqlite-vec / Kuzu / sentence-transformers / FS)
│   │   ├── container.py     # DI wiring
│   │   ├── server.py        # MCP interface adapter
│   │   └── __main__.py      # python -m rag_mcp [--probe]
│   └── tests/               # 134 tests (unit + integration simulation + protocol + probe/evaluate + feedback)
└── skills/                  # 20 user-invocable skills
```

Design principles: Clean Architecture, SOLID (DIP), SSOT (domain model), YAGNI, KISS, Fail-Fast.

## The `.noory/rag/` directory created at the usage site

```
.noory/rag/                    # entirely gitignored
├── raw/                    # 🟢 the user places material directly (PDF, MD, TXT, MDX, images PNG/JPG/GIF/WebP)
├── settings.json           # source · embedding · chunking policy (shareable, share-guide target)
├── probes.json             # 🔒 personal evaluation questions (not shared)
├── feedback.json           # 🔒 personal 👍/👎 search feedback (not shared)
├── manifest.json           # file hashes (for change detection)
├── vec.db                  # sqlite-vec
├── graph/                  # Kuzu DB
└── cache/                  # temporary
```

## Snapshot format

The header (`snapshot.json`) of the tarball produced by `/rag:rag-export`:

```json
{
  "format_version": 1,
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "embedding": { "model": "intfloat/multilingual-e5-small", "dim": 384 },
  "plugin_version": "0.3.0",
  "stats": { "files": N, "chunks": N, "entities": N, "relations": N, "communities": N }
}
```

On `rag-import`, it is rejected if any one of these mismatches: `format_version`, `embedding.model`, `embedding.dim`, `plugin_version` major.

## External API key policy

**Zero.** Every LLM task (semantic chunking, entity/relation extraction, community summarization, alias adjudication, query re-ranking, **evaluation-result diagnosis**) is **performed directly by the active Claude Code or Codex session when the user invokes a skill**. The MCP server handles only deterministic, local work: file walk · hashing, local embedding computation, sqlite-vec / Kuzu storage, Leiden community detection, probe batch search.

## OS compatibility

- Operates on **both macOS · Windows** via the same code path (Linux is effectively compatible too).
- Paths/env vars use only `pathlib` + `os.environ`, with 0 platform branching.
- Claude Code passes the project root explicitly via `RAG_PROJECT_ROOT`. Codex launches with `uv run --project`, which selects the plugin environment without changing the workspace cwd, and explicitly enables the cwd contract with `RAG_PROJECT_ROOT_FROM_CWD=1`.
- For long MCP operations, the Claude settings `env` `MCP_TIMEOUT=60000`, `MCP_TOOL_TIMEOUT=120000` settings are recommended. These are separate from the `RAG_*` server env in `.mcp.json`.
- Every native dependency (sqlite-vec, kuzu, igraph, leidenalg, numpy) provides a win_amd64 wheel.

## License

MIT — see the root [LICENSE](../LICENSE).
