---
description: Open the Solera Map viewer for the current project in your browser.
---

Launch the solera-map viewer for the current Solera project. The command starts the local HTTP server (if not already running) and opens a browser tab to the Plan / Build / Live canvases.

Usage:

```
/map
```

Implementation:

1. Resolve the target project path (current workspace root).
2. Ensure the solera-map MCP server is running — if not, start it.
3. Open `http://localhost:{port}/?project={path}` in the default browser.

The viewer reads:
- `{project}/workspace/concepts/` — Concept files (Living axis)
- `{project}/workspace/stories/` — Story files (Time-bound axis)
- `{project}/workspace/milestones/` — Milestone files
- `{project}/workspace/releases/` — Release snapshots (❄️)
- `{project}/workspace/concept-graph.json` — Concept↔Concept edges (new)
- `{project}/workspace/_views/map-layout.json` — visual metadata (new)
