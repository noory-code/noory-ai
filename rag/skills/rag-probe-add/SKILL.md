---
name: rag-probe-add
description: Add a rag evaluation probe (pre-registered question) — register a frequently asked question in `.noory/rag/probes.json`. Utterance examples "add a probe", "register a rag evaluation question", "I get this question a lot, register it", "rag-probe-add".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-probe-add — register an evaluation question

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

Register a question the user frequently gets (or will get) in `.noory/rag/probes.json`. The registered probes become the golden set that `/rag:rag-evaluate` runs all at once to measure index quality.

> A probe does **not** affect indexing/retrieval. It is purely evaluation material. Being inside `.noory/rag/` it is auto-gitignored + excluded from share-guide — safe as personal material.

## Steps

1. **Check current probes**: call `rag_get_probes`.
   - If the result is empty, proceed as-is.
   - If there are already N, show them in a table and enter add mode.

2. **Take user input**: take the following 3 fields via the host question tool or natural-language conversation.
   - `query` (required): the actual question sentence (e.g., "What is the project's authentication flow?")
   - `id` (optional): if left blank, Claude auto-generates a kebab-case slug from the query (e.g., "auth-flow"). If duplicate, a suffix like `-2`.
   - `note` (optional): a one-line memo (e.g., "frequently asked during new-hire onboarding")

3. **ID auto-generation rule**: follow the `[A-Za-z0-9][A-Za-z0-9_-]*` pattern. A query → 1-3 English core keywords in kebab. Example: "state diagram of the payment module" → `payment-state-diagram`.

4. **Update call**: merge the existing probes list + the new entry and replace the whole thing via `rag_set_probes`.
   - Show any duplicate-ID error to the user and request an ID change.

5. **Confirmation output**:
   ```
   ✅ probe added: <id>
      query: <text>
      note: <text or "(none)">
   Total N now. Check with `/rag:rag-probe-list`, batch-evaluate with `/rag:rag-evaluate`.
   ```

## Example usage

```
User: "I get this question a lot — register 'What is the project's authentication flow?' as a probe"
Claude: rag_get_probes → confirms empty
        ID auto-generated: "auth-flow"
        rag_set_probes([{id:"auth-flow", query:"What is the project's authentication flow?"}])
        ✅ probe added: auth-flow ...
```

## Error handling

- `rag_set_probes` returns invalid → output exactly which field (id format / empty query / duplicate) is the problem, then re-request.
- `RAG_PROJECT_ROOT not set` error → guide to restart Claude Code + `/rag:rag-help`.
- probes.json is corrupted so `rag_get_probes` returns invalid → get the user's consent to back up and reset, then call `rag_set_probes` with an empty list.
