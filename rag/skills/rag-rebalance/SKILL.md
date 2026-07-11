---
name: rag-rebalance
description: Index quality cleanup — alias merge · community re-detection · community summary generation. Utterance examples "rag rebalancing", "rag-rebalance", "graph cleanup", "entity duplicate cleanup", "rag quality cleanup".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-rebalance — index quality cleanup

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

Indexing is incremental, so over time ① the same concept gets duplicated under different IDs, ② the community (cluster) composition goes stale, or ③ community summaries end up empty. This skill has **MCP find the candidates, the active AI session produce the decisions/summaries, and then commit the result**.

## Steps

1. **Prerequisite check**: Call `rag_get_settings`. If absent, guide to `/rag:init-rag`.

2. **prep**: Call `rag_rebalance_prep()`.
   Response:
   - `alias_candidates`: `[{ keep_id, drop_id, name }, ...]`
   - `communities`: `[{ community_id, member_ids, needs_summary }, ...]`

3. **Alias decision (the active AI session)**: for each alias candidate
   - Look at both entities' context (if needed, check the surroundings with `rag_search_graph(<name>, depth=1)`); if they are really the same concept, decide to merge.
   - If they mean something different, refuse the merge.
   - Collect the results into a `merges: [{ keep_id, drop_id }, ...]` array.
   For a large number of candidates (20+), ask the user once which way to go — auto merge / user confirmation.

4. **Community summary (the active AI session)**: for each community with `needs_summary=true`
   - Look at the member entity names and write a short 1-line topic label (e.g. "Flutter state management tools").
   - Collect them into a `summaries: [{ community_id, summary }, ...]` array.

5. **commit**: Call `rag_rebalance_commit(merges=[...], summaries=[...])`.

6. **Print the result summary**:
   ```
   ✅ rebalance complete
      merged: N  (drop_id → keep_id shown as a compact table)
      summaries: M  (community_id → label table)
      current stats: …  (rag_stats)
   ```

## Conservative defaults

An alias merge irreversibly reduces data. Therefore:
- If there are 5 or fewer candidates, auto merge
- If there are 6 or more, show the user a table and confirm
- If the user enters "all", merge in bulk; if "skip", commit only the summaries with no merge

## Error handling

- A merge request with the same `keep_id == drop_id` is ignored by MCP.
- If the prep result is all empty, print "Nothing to clean up." and exit.
