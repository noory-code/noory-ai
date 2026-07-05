---
name: rag-feedback
description: Record 👍/👎 feedback on the most recent search results to improve the quality of future searches. Example utterances "this result was good", "rag feedback positive", "that last search was bad", "rag-feedback 👎", "this isn't it".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.2.0"
---

# rag-feedback — record search-result feedback

## What

Records via `rag_record_feedback` whether the most recent `rag-search` result was good or not. Feedback accumulates in `.noory/rag/feedback.json` (personal — not shared) and, from the next search on, is **reflected in ranking at the material (file) level** — material that was good rises, material that was not sinks. (Not embedding retraining — it is a per-`rel_path` bonus/penalty, so it survives reindexing.)

## Steps

1. **Identify the target**: capture the **query** of the most recent search and the target **evidence file (rel_path)** for the feedback.
   - If the user points at a specific piece of evidence ("evidence #2 was right"), use that `rel_path`.
   - For an overall assessment, apply it to each of the top evidence items' `rel_path`.
2. **Extract the verdict**: good/bad from the utterance.
   - Positive ("was good / correct / helpful") → `good`
   - Negative ("meh / wrong / no / irrelevant") → `bad`
3. **Record**: for each (query, rel_path), `rag_record_feedback(query=<query>, rel_path=<file>, verdict=<good|bad>)`.
4. **Confirmation output**:
   ```
   ✅ Feedback recorded: <rel_path> ← good/bad
   It will be reflected from the next search on. Aggregation is `/rag:rag-feedback-report`.
   ```

## Notes
- If there is no recent-search context, confirm which query/material the feedback is about before proceeding.
- Feedback is personal material (`.noory/rag/`, gitignored by default) — it is not shared.
