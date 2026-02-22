---
description: Refresh evonest identity.md — have Claude re-read the project and propose an updated identity document.
argument-hint: "[project path]"
---

Re-draft the project's `.evonest/identity.md` using the `evonest_identity_refresh` MCP tool.

Steps:
1. Call `evonest_identity_refresh` with `project` set to the target project path (use cwd if not specified).
2. The tool returns `{"current": "...", "draft": "..."}` — show both to the user side by side.
3. Ask the user: "Update identity.md with the new draft? [y/N]"
4. If yes: call `evonest_identity` with `project` and `content` set to the draft text.
5. If no: inform the user that no changes were made.
