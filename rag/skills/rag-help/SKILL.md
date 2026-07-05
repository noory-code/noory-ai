---
name: rag-help
description: Full usage guide for the rag plugin — one-line concept, quick start, index of 17 skills, FAQ, troubleshooting, Windows/macOS install. Example utterances "rag usage", "rag help", "how do I use rag?", "rag-help".
user-invocable: true
metadata:
  type: action
  version: v1.1.0
  plugin_version: "0.1.4"
---

# rag-help — rag usage

Show the following body to the user as-is. If the project already has an index (`.noory/rag/` exists), call `rag_stats` first and prepend a one-line current status.

---

## One-line concept

rag is a plugin that indexes the **current project's domain material** (PDFs · notes · docs) locally along two axes — **vector + graph** — and provides semantic search only when explicitly invoked. **0 external API keys**; all data is self-contained in `.noory/rag/`. **First-class support on both macOS · Windows.**

## Install

```text
/plugin marketplace add noory-code/noory-ai
/plugin marketplace update noory-ai
/plugin install rag@noory-ai
```

### Prerequisite: `uv` (Python package manager)

| OS | Install command |
|---|---|
| **macOS** | `brew install uv` |
| **Windows (PowerShell)** | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` (or `winget install --id=astral-sh.uv -e`) |
| **Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

Python 3.11+ is managed automatically by uv. ~500MB of disk is needed (dependencies + a ~120MB embedding-model download).

### Recommended: MCP timeout env

The first dependency install, the embedding-model download, and bulk indexing can make MCP calls take a long time. The following values are recommended under `env` in the project's `.claude/settings.json`.

```json
{
  "env": {
    "MCP_TIMEOUT": "60000",
    "MCP_TOOL_TIMEOUT": "120000"
  }
}
```

This timeout is a Claude/MCP client setting. The `env` in `rag/.mcp.json` serves a different purpose — it passes `RAG_PROJECT_ROOT` to the MCP server process.

## Quick start (4 + 2 steps)

The basic 4-step flow:

1. `/rag:init-rag` — interactive initialization. Creates `.noory/rag/raw/` and `settings.json`, and auto-updates the project `.gitignore`.
2. Freely place PDFs · notes · external material in `.noory/rag/raw/`. Subfolders OK.
3. `/rag:rag-reindex` — Claude extracts chunks · entities and loads them.
4. `/rag:rag-search "what I want to know"` — an answer with results + source citations.

To go all the way to quality measurement · tuning, +2 steps (recommended):

5. `/rag:rag-probe-add` — register 3–5 frequently asked questions (e.g. "the project's authentication flow", "the payment module's state diagram").
6. `/rag:rag-evaluate` — batch-measure index quality with the registered questions + Claude's diagnosis (which material is lacking, whether chunking needs adjusting).

## 20 skills

### Index lifecycle
| Skill | One line |
|---|---|
| `/rag:init-rag` | initial setup — create `.noory/rag/`, settings.json, gitignore |
| `/rag:rag-reindex` | reindex the changed portion |
| `/rag:rag-rebalance` | alias merge · community re-detection · summary generation |
| `/rag:rag-clear` | reset the index (confirmation prompt) |

### Search · exploration
| Skill | One line |
|---|---|
| `/rag:rag-search "…"` | hybrid search + answer synthesis |
| `/rag:rag-explore <entity>` | N-hop graph exploration around an entity |
| `/rag:rag-status` | index state · statistics |

### Feedback
| Skill | One line |
|---|---|
| `/rag:rag-feedback` | record 👍/👎 feedback on the latest search results |
| `/rag:rag-feedback-report` | aggregate feedback — top queries, well-matching sources, weak spots |

### Source management
| Skill | One line |
|---|---|
| `/rag:rag-add-source <path>` | add a source |
| `/rag:rag-fetch-external` | fetch documents via an installed official connector (Confluence · Drive · Notion) and index them |
| `/rag:rag-remove-source <path>` | remove a source |

### Evaluation · tuning (probes)
| Skill | One line |
|---|---|
| `/rag:rag-probe-add` | register an evaluation question in advance (personal material, not shared) |
| `/rag:rag-probe-list` | list the registered questions |
| `/rag:rag-probe-remove <id>` | remove a question |
| `/rag:rag-evaluate` | batch-run the registered questions + Claude diagnosis · tuning suggestions |

### Backup · sharing
| Skill | One line |
|---|---|
| `/rag:rag-export <out>` | create a snapshot tarball |
| `/rag:rag-import <in>` | apply a snapshot (auto compatibility check) |
| `/rag:rag-share-guide` | guide on how to share with the team (materials + settings only; personal probes auto-excluded) |

### Help
| Skill | One line |
|---|---|
| `/rag:rag-help` | this help |

## FAQ

**Q. It says `uv` is missing.**
A. Install it with the per-OS command in the "Prerequisite" table above, then restart Claude Code. The MCP server auto-installs dependencies on the first call.

**Q. The embedding-model download takes a long time.**
A. On the first indexing · search, it downloads about 120MB (`intfloat/multilingual-e5-small`). After that it loads instantly from the local cache (`~/.cache/huggingface`).

**Q. Search over Korean material does not work well.**
A. The default model supports 100 languages including Korean, but the result varies with the amount of material and chunking quality. Add more material, tidy it up with `/rag:rag-rebalance`, then check which questions are weak with `/rag:rag-evaluate`.

**Q. What are probes and why are they managed separately?**
A. Probes are the questions you get asked most often (e.g. the go-to questions in new-hire onboarding). They **do not affect indexing · search**; they are used only by `/rag:rag-evaluate`, which batch-runs them to measure "can the current index answer these questions". Being personal material, they live separately from settings as `.noory/rag/probes.json`, and are auto-excluded from `rag-share-guide`.

**Q. I want to share the index with a teammate.**
A. See `/rag:rag-share-guide`. Three patterns (personal branch / selective `git add -f` / `rag-export` snapshot). Personal probes are not shared in any of them.

**Q. Does `.noory/rag/` get committed to git?**
A. `init-rag` adds it to the project `.gitignore` automatically. By default it is a private area.

**Q. How does PDF indexing work?**
A. Text is extracted with `pypdf`, then chunked · embedded the same as ordinary markdown/text. Scans (image-based PDFs that need OCR) are unsupported.

**Q. Does it work well on Windows?**
A. Yes. The code uses only `pathlib` + `os.environ` (0 OS-specific branches), and every native dependency (sqlite-vec, kuzu, numpy, leidenalg, etc.) provides a win_amd64 wheel. The project root is also passed explicitly via the `RAG_PROJECT_ROOT` env (wired from `${CLAUDE_PROJECT_DIR}` on Claude Code, `${CODEX_PROJECT_DIR}` on Codex), so it is unaffected by cwd differences. For long-running MCP work, setting `MCP_TIMEOUT=60000`, `MCP_TOOL_TIMEOUT=120000` in `.claude/settings.json` is recommended.

## Troubleshooting

- **Index is empty?** → check with `/rag:rag-status` → if 0, `/rag:rag-reindex`.
- **Search results are inaccurate?** → measure which probe is weak with `/rag:rag-evaluate` → add material or adjust chunking → reindex.
- **DB corrupted?** → `/rag:rag-clear` then `/rag:rag-reindex` (the raw/ material is preserved as-is).
- **The MCP server doesn't come up?** → run `uv run python -m rag_mcp --probe` directly in the plugin directory → check stderr.
- **A "RAG_PROJECT_ROOT not set" error appears?** → Claude Code failed to inject the env. Restart Claude Code and try again. If it still happens, reinstall the plugin (`/plugin update rag@noory-ai`).
- **MCP calls time out?** → add `MCP_TIMEOUT=60000`, `MCP_TOOL_TIMEOUT=120000` to `env` in the project's `.claude/settings.json` and restart Claude Code. The `RAG_*` env in `.mcp.json` is for passing server paths, not the place to fix a timeout problem.
- **The first call is too slow?** → the embedding-model download + Python dependency install happen at once. 1–3 minutes is normal.

## References

- Plugin README: [rag/README.md](../../README.md)
- Changelog: [rag/CHANGELOG.md](../../CHANGELOG.md)
- Repo guide: [CLAUDE.md](../../../CLAUDE.md)
- Manual end-to-end test: `rag/server/scripts/manual_e2e.md`
