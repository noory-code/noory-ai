---
name: rag-evaluate
description: Batch-evaluate rag index quality with pre-registered probes — search results + the active AI session's diagnosis and tuning suggestions. Example utterances "evaluate rag", "run the probes", "check whether indexing went well", "rag-evaluate", "measure search quality".
user-invocable: true
metadata:
  type: read
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-evaluate — evaluate index quality with registered probes

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

Automatically throws every pre-registered question in `.noory/rag/probes.json` at the index and reports the **search results + the active AI session's diagnosis** to the user. The deterministic part (search) is handled by the MCP server; interpretation/judgment (where it is weak, what to adjust) is handled by the **active AI session** — the consistent design of this plugin.

> This skill is the **measurement stage** before the user hand-tunes the indexing policy. Per the CLAUDE.md `honesty` principle, it does not auto-tune — the user reviews the active AI session's suggestions and applies them directly via `rag_set_settings`.

## Steps

1. **Precondition check**:
   - Call `rag_get_probes` → if the result is empty:
     ```
     📭 There are no probes, so nothing can be evaluated.
     Register 3-5 frequently asked questions first with `/rag:rag-probe-add`.
     ```
     then stop.
   - Call `rag_stats` → if `chunks == 0`:
     ```
     ⚠️ The index is empty. Run `/rag:rag-reindex` first.
     ```
     then stop.

2. **Batch evaluation**: call `rag_evaluate(k=5)`. A top-5 hybrid search is run at once against every registered probe.

3. **Print the results as a table** (one-line summary per probe):
   ```
   🔬 Evaluation results (k=5, expand_depth=N)

   | Probe | Query | Top1 dist | Unique files | Top matches |
   |-------|-------|-----------|--------------|----------|
   | auth-flow | How does auth flow? | 0.28 | 3 | docs/auth.md (idx 2), README.md (idx 0) |
   | payment-state | Payment state diagram | 0.71 | 1 | docs/legacy.md (idx 4) |
   ```
   - The lower `min_distance` is, the stronger the semantic match (on the E5 embedding scale, ≤ 0.3 = strong, ≥ 0.5 = weak).
   - `unique_files` = 1 means it relies on a single file → a signal of insufficient diversity.

4. **the active AI session's diagnosis**: classify the results into the following 4 categories and comment.
   - 🟢 **Good** (top1_distance ≤ 0.35 & unique_files ≥ 2)
   - 🟡 **An answer, but weak** (0.35 < top1_distance ≤ 0.55) → suggest reviewing chunk size / sources
   - 🔴 **Insufficient recall** (top1_distance > 0.55) → the relevant material may not be in the index → suggest adding sources
   - ⚫ **Noise match** (the text seems unrelated to the query topic, regardless of top1 distance) → show the user which file was matched incorrectly and suggest adding an exclude

5. **Tuning suggestions** (optional, entered if the user wants):
   - If there are 🟡/🔴 items, present options via the host question tool, "Which adjustment shall we try?":
     - add sources (can suggest candidate relevant material)
     - change chunking.target_tokens (e.g. 400 → 600, when short chunks are breaking semantic units)
     - increase graph.expand_depth (when concept-relation-based search is weak)
   - If the user picks one, read the current settings with `rag_get_settings`, merge the new value, and call `rag_set_settings`.
   - After the change, note "reindexing may be needed" + confirm whether to call `/rag:rag-reindex`.

6. **Re-evaluation flow**: after tuning + reindexing, if the user wants, call `/rag:rag-evaluate` again. Including a before/after table comparison.

## Diagnosis-comment guide (for Claude)

- The distance thresholds (0.35 / 0.55) are empirical for E5-small. If you switch to a different embedding model, the thresholds need recalibration — state that explicitly to the user then.
- In every evaluation result, **state the parts you cannot be confident about** (CLAUDE.md `honesty`). Like "Top1 dist 0.40 — borderline, so user judgment is needed".
- No auto-tuning. Always `rag_set_settings` only after user confirmation.

## Output format example

```
🔬 rag evaluation results
   probes: 5 | chunks: 1240 | embedding: intfloat/multilingual-e5-small

| Probe | Query | Top1 | Files | Diagnosis |
|-------|-------|------|-------|------|
| auth-flow | auth flow | 0.28 | 3 | 🟢 Good |
| payment-state | Payment state diagram | 0.71 | 1 | 🔴 Insufficient material |
| ...

💡 Diagnosis summary
   • 🟢 3 | 🟡 1 | 🔴 1
   • payment-state: the payment-related docs seem to be absent from sources.
     If a `docs/payment/` folder exists, adding it to sources is recommended.

Next step: shall we tune? (yes/no)
```

## Error handling

- `rag_evaluate` returns `no probes registered` → fall back to the step 1 guidance.
- Index empty (`rag_stats` chunks=0) → guide to `/rag:rag-reindex`.
- `RAG_PROJECT_ROOT not set` → restart Claude Code + `/rag:rag-help`.
