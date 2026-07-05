---
name: rag-feedback-report
description: Aggregates accumulated search feedback to report what is searched most, which sources match well, and weak spots (sources with many 👎), and proposes improvements. Example utterances "rag feedback report", "search feedback stats", "what's not matching well", "rag-feedback-report".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.2.0"
---

# rag-feedback-report — feedback aggregation · weak-spot report

## What

Takes the feedback accumulated via `rag_get_feedback` and the net boost per source (rel_path), and produces a report on **what is searched frequently and which sources match well / poorly**. The **diagnosis stage** of the self-improvement loop — Claude pinpoints weak spots and proposes the next action (source augmentation · reindexing).

## Steps

1. **Aggregation query**: `rag_get_feedback()` → `{feedback:[…], boosts:{rel_path:net}, count}`.
   - If empty, guide "No feedback yet. After searching, leave feedback via `/rag:rag-feedback`." then finish.
2. **Aggregation (Claude itself)**:
   - **Frequently searched queries**: top query frequencies.
   - **Well-matching sources**: rel_paths with the highest positive net boost.
   - **Weak-spot sources**: rel_paths with negative net boost — sources that show up in search but the user said were wrong.
3. **Diagnosis · proposal (Claude itself)**: infer why the weak-spot sources don't match (content stale / chunking too large / topic mismatch) + propose an action — source augmentation (`rag-add-source` · `rag-fetch-external`), reindexing (`rag-reindex`), and if contradictory, let the user judge at reindex time.
4. **Output**:
   ```
   📊 Feedback report (N total)
   Frequently searched: "…" ×k
   Well-matching sources: <rel_path> (+net)
   Weak-spot sources:     <rel_path> (-net) — [inferred cause] → [proposal]
   ```

## Note
- The report goes only as far as diagnosis · proposal. The actual reindexing · augmentation is done via the corresponding skill after user confirmation.
