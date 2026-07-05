---
name: rag-search
description: Semantic · graph hybrid search over indexed material. Example utterances "rag search …", "find X in my material", "rag-search auth flow", "tell me X via rag".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.2.0"
---

# rag-search — hybrid search

## What

Takes a natural-language query, gets vector top-k + graph-expansion results via `rag_search`, and Claude (the current session) synthesizes those results into an answer tailored to the user's query.

## Steps

1. **Extract the user query**: if a slash argument is present, use it; otherwise take it via AskUserQuestion.

2. **Search call**: call `rag_search(query=<query>, k=8)`.
   - `chunks`: top K by ascending distance
   - `entities`: entities linked to the chunks
   - `subgraph`: N-hop expansion around the entities

3. **Re-ranking · refinement (Claude itself)**:
   - Beyond distance, quickly judge whether the chunk body semantically matches the query and adjust the priority
   - Exclude duplicate/noise chunks (e.g. short headings)
   - Narrow to within 5 chunks to cite in the answer

4. **Answer synthesis**:
   - **Conclusion 1-2 sentences**: the core answer to the query
   - **Evidence**: quote the chunk body verbatim or briefly. The source is in `rel_path:chunk_idx` form (e.g. `docs/auth.md:3`). If the chunk `meta.source_type == "image"`, prefix the source with 🖼 to indicate it came from a picture (e.g. `🖼 diagrams/auth-flow.png:1`).
   - **Related concepts**: up to 3 meaningful neighbors from `subgraph.nodes` — "Related: [Riverpod] [Notifier] [Provider]"
   - **State it if uncertain**: if not in the material, "That information is not in the index. Recommend adding material to `.noory/rag/raw/` then running `/rag:rag-reindex`."

5. **If the results are thin**: if chunks is 0 or all distances are above a threshold (e.g. 0.8), reinforce with graph-only exploration. `rag_search_graph` takes an **entity seed (name), not a free-text query**, so secure the seed first:
   - If step 2's result has `entities`, use the most relevant entity name among them as the seed: `rag_search_graph(entity=<entity name>, depth=2)`.
   - If `entities` is empty, find candidate entities with `rag_list_entities(q=<key term extracted from the query>)`, and if matched, call `rag_search_graph(entity=<candidate name>, depth=2)` with that name.
   - If there is no entity to use as a seed at all, skip the graph step and give the "no related entity in the index" notice + recommend adding material / `rag-reindex`.

## Output format (example)

```
✅ rag-search: "How does the project's authentication flow work?"

Conclusion
  • It receives the OAuth flow via Firebase Auth, and the backend stores the token in Riverpod's authProvider.

Evidence
  1. docs/auth/architecture.md:2 — "…"
  2. docs/auth/firebase.md:5 — "…"
  3. 🖼 diagrams/auth-flow.png:1 — "…(quoted from the image description)"

Related concepts: Riverpod · OAuth · authProvider

(index stats: chunks 318 / entities 87)
```

## Options

- `k`: default 8. If the user's utterance has an expression like "top N", extract and apply it.
- `expand_depth`: default settings value (2). If the graph expansion is too broad, narrow to depth=1.

## Feedback prompt (Clear Feedback)

Append one line at the end of the answer: "Was this result correct? Leave 👍/👎 via `/rag:rag-feedback` and the next search will improve." When the user judges, `rag-feedback` reflects it into the ranking per material (rel_path) unit.
