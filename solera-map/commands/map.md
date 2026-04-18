---
description: Open the Solera Map viewer for the current project in your browser.
---

Invoke the solera-map MCP tool `open_map` with the **absolute path of the current working directory**.

The tool:
- Validates that the path contains a Solera workspace (looks for `workspace/concepts/` or `workspace/identity/`).
- Opens `http://127.0.0.1:{port}/?project_path={path}` in the default browser.
- Returns the opened URL to report back.

If `open_map` returns an error (e.g., "No Solera workspace found"), tell the user which directory was checked and suggest running `solera-init` first.

Do not open the browser yourself — always route through the MCP tool so port resolution and workspace validation stay consistent.
