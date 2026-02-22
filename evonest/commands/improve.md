---
description: Run evonest improve — pick a proposal and execute it (no Observe/Plan phases).
argument-hint: "[project path] [proposal filename]"
---

Run **evonest improve** on the target project using the `evonest_improve` MCP tool.

Use the current working directory as the project path unless the user specifies otherwise.

Call `evonest_improve` with:
- `project`: absolute path to the target project
- `proposal_id`: bare filename of the proposal to execute (e.g. `proposal-0004-20260222-103000.md`).
  If the user did not specify one, omit it — evonest will auto-select by priority (high first) then age (oldest first).

After the tool returns, summarize:
- Which proposal was executed
- Which files were changed
- Whether the changes were committed or a PR was opened
- If no proposals exist, suggest running `/evonest:analyze` first
