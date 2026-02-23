---
description: Run evonest evolve — full cycle (Observe → Plan → Execute → Verify → commit/PR).
argument-hint: "[project path] [--cycles N] [--cautious] [--all-personas]"
---

Run **evonest evolve** on the target project using the `evonest_evolve` MCP tool.

Determine the project path:
- If the user specifies a path, use that.
- If the user says "evonest" or no path given and cwd is inside the noory-ai monorepo, use the absolute path of the `evonest/` package directory.
- If the user says "distill", use the absolute path of the `distill/` package directory.
- Never use the monorepo root as the project path.

Call `evonest_evolve` with:
- `project`: absolute path to the target project
- `cycles`: number of cycles (default: from config, usually 1)
- `cautious`: true if the user said `--cautious` (pause after Plan for review)
- `all_personas`: true if the user said `--all-personas`
- `observe_mode`: "quick", "deep", or "auto" (default: "auto")

**Cautious mode flow**:
1. Call `evonest_evolve` with `cautious=true`
2. Show the plan summary to the user and ask: "Proceed? [y/N]"
3. If yes: call `evonest_evolve` again with `resume=true`
4. If no: call `evonest_evolve` with `resume=false` to cancel

After the tool returns, summarize:
- How many cycles succeeded
- Which files were changed
- Commit message or PR link
