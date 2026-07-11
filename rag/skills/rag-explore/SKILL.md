---
name: rag-explore
description: N-hop graph exploration around a specific entity — reports what is connected to what as a visual/table. Example utterances "explore around entity X", "rag-explore Riverpod", "explore around Notifier", "show me X's relations".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-explore — graph exploration

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## Steps

1. **Prerequisite check**: `rag_get_settings`.

2. **Seed extraction**: capture the entity name (or id) from the user's utterance. If absent, get it via the host question tool.

3. **Graph call**: `rag_search_graph(entity=<seed>, depth=2)`.
   - If the result is empty, search candidates with `rag_list_entities(q=<seed>)`. Let the user pick among the candidates.

4. **Expansion-depth negotiation**: if there are too many nodes (50+), re-call with depth=1. If too few (2 or fewer), try depth=3.

5. **Output**:
   ```
   🔎 rag-explore: Riverpod (depth=2)

   Nodes (12)
     • Riverpod (library)
     • Notifier (concept)
     • Provider (concept)
     • StateNotifier (concept)
     ...

   Edges (18)
     Riverpod —[USES]→ Provider
     Riverpod —[USES]→ Notifier
     Notifier —[EXTENDS]→ StateNotifier
     ...

   Community grouping (if any)
     #4: Riverpod, Provider, Notifier, StateNotifier  ("Flutter state-management tools")
     #7: ...
   ```

6. **Next-action suggestion**: 1 line
   - deeper: `rag-explore <entity> depth=N`
   - to see the body: `/rag:rag-search <entity>`

## Error handling

- If the seed entity does not exist, present 5 candidates to the user as a table → selection.
</content>
