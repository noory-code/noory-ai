# noory-ai

Plugin collection for Claude Code and Codex — MCP servers, lifecycle hooks, and skill packs.

## Packages

Add the marketplace once per host:

| Host | Marketplace command |
|---|---|
| Claude Code | `/plugin marketplace add noory-code/noory-ai` |
| Codex | `codex plugin marketplace add noory-code/noory-ai` |

### [Evonest](evonest/) — Autonomous Code Evolution

Runs 20 specialist personas against your codebase (security auditor, chaos engineer, performance analyst, etc.) and lets adaptive selection determine which approaches work best for your project.

- **Observe → Plan → Execute → Verify** cycle with auto-revert on failure
- Git stash before every change; lock file prevents concurrent runs
- Adaptive persona weights — successful personas run more often over time
- Direct commit or PR mode (`code_output: "pr"`)

**Install:** Claude Code: `/plugin install evonest@noory-ai` · Codex: `codex plugin add evonest@noory-ai`

### [Novel AI](https://github.com/noory-code/novel-ai) — Novel's Open Plugin Stack

Mashbill, Solera, Proof, and Distill live in the public `noory-code/novel-ai`
repository. It is an independent repository, not a submodule of `noory-ai`.
For coordinated local development, clone `noory-ai` and `novel-ai` as sibling
directories under the same workspace.

Public architecture, concepts, specifications, and migration guidance are maintained in
[`novel-ai/docs/`](https://github.com/noory-code/novel-ai/tree/main/docs). Start with
[`novel-ai/docs/index.md`](https://github.com/noory-code/novel-ai/blob/main/docs/index.md).

| Plugin | Responsibility |
|---|---|
| Mashbill | Visual thinking canvas and Novel artifact publisher |
| Solera | Work planning, deterministic gates, and execution order |
| Proof | Append-only decisions referenced by stable ID |
| Distill | Durable knowledge extraction and recall |

**Install:**

```text
/plugin marketplace add noory-code/novel-ai
/plugin install mashbill@novel-ai
/plugin install solera@novel-ai
/plugin install proof@novel-ai
/plugin install distill@novel-ai
```

### [Flutter Cask](flutter-cask/) — Flutter Package Guide Skills

Curated reference skills for Flutter development. Each skill gives Claude Code or Codex immediate access to usage patterns, best practices, and code examples for the most common Flutter packages.

- 32 skills across state management, routing, Firebase, UI, testing, and more
- No Python dependencies — pure skill pack
- Covers riverpod, go-router, freezed, hive, admob, and 27 more

**Install:** Claude Code: `/plugin install flutter-cask@noory-ai` · Codex: `codex plugin add flutter-cask@noory-ai`

### [Plainly](plainly/) — Clear Response Styles

Five Claude Code output styles that put a chosen writing style into the session's system prompt.
Carries fixed honesty, language-quality, and register rules, and keeps Claude Code's default
coding instructions in place. No hook and no code that runs at prompt time.

**Install:** Claude Code: `/plugin install plainly@noory-ai` (Claude Code only)

### [RAG](rag/) — Local GraphRAG Plugin

Per-project vector + graph (GraphRAG) hybrid search. Runs fully locally with no external API key.

- Local embeddings (`intfloat/multilingual-e5-small`) + sqlite-vec + Kuzu graph store
- Chunks and extracts entities from files placed under `.noory/rag/raw/`
- Built-in evaluation flow via user-registered probe questions

**Install:** Claude Code: `/plugin install rag@noory-ai` · Codex: `codex plugin add rag@noory-ai`

### [Pencil M3 Flutter](pencil_m3_flutter/) — Flutter Material Design 3 Automation

Connects the Pencil app with Claude Code or Codex to initialize a per-app Material Design 3 library, generate seed-color-based Flutter theme code, and produce screen design prompts.

- `pmf-init` — scaffold the app's design guide, seed color, logo, and project design skill
- `pmf-change-seed-color` / `pmf-change-logo` — update theme or logo in place
- Requires the Pencil MCP server

**Install:** Claude Code: `/plugin install pencil-m3-flutter@noory-ai` · Codex: `codex plugin add pencil-m3-flutter@noory-ai`

### [Stage](stage/) — Durable Execution Harness

Portable `.stage/` harness for LLM-led long-running projects. Stage separates artifact status, context ownership, decision gates, verification, and retrospectives.

- Global artifact time: `past` / `present` / `future`
- Local work lifecycle: `before` / `during` / `after` / `retrospective`
- Plain Markdown templates for Codex, Claude, Windows, Linux, and macOS

**Install:** Claude Code: `/plugin install stage@noory-ai` · Codex: `codex plugin add stage@noory-ai`

## Development

Clone Novel AI separately when working across both repositories:

```bash
git clone https://github.com/noory-code/noory-ai.git
git clone https://github.com/noory-code/novel-ai.git
```

Each package is independent — work inside the relevant subdirectory. Claude Code reads
[CLAUDE.md](CLAUDE.md); Codex starts from [AGENTS.md](AGENTS.md), which routes to the same SSOT.

## License

Each package is MIT licensed. See individual `pyproject.toml` or host plugin manifest for details.
