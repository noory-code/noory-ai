---
description: Run evonest analyze — scan the project and save all improvement opportunities as proposals (no code changes).
argument-hint: "[project path] [--all-personas] [--observe-mode quick|deep|auto]"
---

Run **evonest analyze** on the target project using the `evonest_analyze` MCP tool.

Determine the project path:
- If the user specifies a path, use that.
- If the user says "evonest" or no path given and cwd is inside the noory-ai monorepo, use the absolute path of the `evonest/` package directory.
- If the user says "distill", use the absolute path of the `distill/` package directory.
- Never use the monorepo root as the project path.

Call `evonest_analyze` with:
- `project`: absolute path to the target project (use the user's specified path, or ask if unclear)
- `all_personas`: true if the user said `--all-personas`
- `observe_mode`: "quick", "deep", or "auto" based on the user's flag (default: "auto")

After the tool returns, summarize the result:
- How many proposals were saved
- Where to find them (`.evonest/proposals/`)
- Suggest running `/evonest:improve` to execute a proposal
