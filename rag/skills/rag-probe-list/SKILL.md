---
name: rag-probe-list
description: List the registered rag evaluation questions (probes) — print every entry in `.noory/rag/probes.json` as a table. Utterance examples "probe list", "show the rag evaluation questions", "which questions are registered", "rag-probe-list".
user-invocable: true
metadata:
  type: read
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-probe-list — view registered probes

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

Show all of the user's evaluation questions registered in `.noory/rag/probes.json` as a table. Let the user see "which questions have I registered so far" at a glance.

## Steps

1. Call `rag_get_probes`.
2. If the result is empty, print the guidance and exit:
   ```
   📭 No probes registered.
   Register frequently asked questions with `/rag:rag-probe-add`.
   ```
3. If there are entries, print as a table:
   ```
   📋 Registered probes (N)

   | ID | Query | Note |
   |----|-------|------|
   | auth-flow | What is the project's authentication flow? | onboarding |
   | payment-state | State diagram of the payment module | (none) |

   Available actions:
   • `/rag:rag-evaluate` — batch-evaluate all
   • `/rag:rag-probe-add` — add a new question
   • `/rag:rag-probe-remove <id>` — remove
   ```

## Error handling

- probes.json corrupted → output "The probes file is corrupted. Start over with `/rag:rag-probe-add`." along with the raw error.
- `RAG_PROJECT_ROOT not set` → guide to restart Claude Code.
