---
description: Run evonest improve — pick a proposal and execute it (no Observe/Plan phases). Use --all to batch-process every pending proposal.
argument-hint: "[project path] [proposal filename] [--all]"
---

Run **evonest improve** on the target project using the `evonest_improve` MCP tool.

The tool is **synchronous** — it blocks until the full cycle (Execute → Verify → commit) completes before returning.

Determine the project path:
- If the user specifies a path, use that.
- If the user says "evonest" or no path given and cwd is inside the noory-ai monorepo, use the absolute path of the `evonest/` package directory.
- If the user says "distill", use the absolute path of the `distill/` package directory.
- Never use the monorepo root as the project path.

Call `evonest_improve` with:
- `project`: absolute path to the target project
- `proposal_id`: bare filename of the proposal to execute (e.g. `proposal-0004-20260222-103000.md`).
  If the user did not specify one, omit it — evonest will auto-select by priority (high first) then age (oldest first).
- `all`: set to `True` if the user passed `--all` — processes every pending proposal sequentially until the queue is empty.

After the tool returns, summarize:
- Which proposal(s) were executed
- Which files were changed
- Whether the changes were committed or a PR was opened
- If no proposals exist, suggest running `/evonest:analyze` first
