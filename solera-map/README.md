# solera-map

> Mindmap-style visual layer for [Solera](../solera/) projects. Four canvases — **Service** (persona-centric, upstream of Plan), **Plan** (sketch), **Build** (radial WBS), **Live** (accumulated value) — over the same Solera data.

## Status

v0.1.0 — Service canvas + Living-axis entity reads + propose-from-narrative endpoint shipped. See [CHANGELOG.md](CHANGELOG.md).

## Install

This package ships as a Claude Code plugin. Once registered in a marketplace:

```
/plugin install solera-map
```

After install, open the viewer for a project:

```
/map
```

## Architecture

- **Python** (uv-managed) MCP stdio server + local HTTP server in a single process
- **Browser** React + ReactFlow frontend (prebuilt static files under `viewer/dist/`)
- **Data** `.md` files under `.solera/` remain SSOT; two solera-map-only files add Concept-to-Concept edges (`concept-graph.json`) and layout metadata (`_views/map-layout.json`)

## Build & Run

```bash
uv sync
uv run python -m solera_map    # starts MCP + HTTP server
uv run pytest                  # run tests
uv run mypy src/               # type check
uv run ruff check src/ tests/  # lint
```

Viewer build (when viewer/ is populated):

```bash
cd viewer
pnpm install
pnpm build         # produces viewer/dist/ (committed)
```

## Relation to Solera

`solera-map` does **not** duplicate Solera data or skills. It reads the same `.solera/` files (or `workspace/` if the project has not yet migrated — supported as a deprecation fallback through solera-map v0.1.x) and delegates semantic operations (Concept create, Story kickoff, etc.) back to existing Solera skills via MCP.

Concept structure (SSOT: [solera/skills/solera-write-concept/assets/concept-template.md](../solera/skills/solera-write-concept/assets/concept-template.md)) is reused verbatim:

- `# Intent` — the north star
- `# Current Design` — what the human is sketching (Plan content)
- `# Current Shape` — what has actually been produced (Live content)
- `# Horizon` — future hypotheses
- `# Contributions` — Story log

## License

MIT — see [LICENSE](LICENSE).
