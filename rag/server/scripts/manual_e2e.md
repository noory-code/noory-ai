# Manual end-to-end test

A checklist for a human to run once through the **Claude Code → MCP** end-to-end flow that the automated tests (`pytest`) do not cover.

## Prerequisites

```bash
brew install uv       # macOS (Windows/Linux: see the install table in rag/README.md)
# start in an empty folder (any path works; /tmp/rag-e2e is just the example used below)
mkdir -p /tmp/rag-e2e && cd /tmp/rag-e2e
```

Run Claude Code:

```text
/plugin marketplace add noory-code/noory-ai
/plugin marketplace update noory-ai
/plugin install rag@noory-ai
```

## Scenarios

1. **Initialization**
   - Run: `/rag:init-rag`
   - Expect: `.noory/rag/raw/`, `.noory/rag/settings.json`, and a `.noory/rag/` line added to the root `.gitignore`

2. **Status check**
   - Run: `/rag:rag-status`
   - Expect: all counts 0, embedding model · dim shown

3. **Place test material**
   ```bash
   cat > .noory/rag/raw/note.md <<'EOF'
   # Authentication flow

   ## OAuth callback
   Firebase Auth's OAuth flow works as follows.

   ## Token storage
   The token is stored in Riverpod's authProvider.
   EOF
   ```

4. **First indexing**
   - Run: `/rag:rag-reindex`
   - Expect: 1 file / N chunks added. Claude reports the chunk · entity split.

5. **Search**
   - Run: `/rag:rag-search "how does the authentication flow work?"`
   - Expect: cites `note.md` + presents the Firebase Auth / Riverpod / authProvider entities.

6. **Re-check status**
   - Run: `/rag:rag-status`
   - Expect: chunks > 0, entities > 0.

7. **Graph exploration**
   - Run: `/rag:rag-explore Riverpod`
   - Expect: the Riverpod node and its related 1–2-hop neighbors shown.

8. **Add source → partial indexing**
   ```bash
   mkdir -p docs && echo "# Services" > docs/services.md
   ```
   - Run: `/rag:rag-add-source docs/`
   - Expect: the new file is indexed.

9. **Reindex after a change**
   ```bash
   echo "extra content" >> .noory/rag/raw/note.md
   ```
   - Run: `/rag:rag-reindex`
   - Expect: changed=1, reprocessed.

10. **Rebalancing**
    - Run: `/rag:rag-rebalance`
    - Expect: community detection + summary generation (with little material, there may be no alias candidates).

11. **Snapshot export → import**
    - Run: `/rag:rag-export /tmp/rag-snap.tar.gz`
    - In a separate empty folder: `/rag:init-rag` → `/rag:rag-import /tmp/rag-snap.tar.gz`
    - Expect: the statistics match the original.

12. **Reset**
    - Run: `/rag:rag-clear`
    - Expect: after the two confirmation prompts, only the index is deleted — `settings.json` and `raw/` are preserved.

## Pass criteria

- All 12 scenarios complete without errors and without manual intervention beyond the prompts shown.
- Search results cite information that actually exists in the material.
- `.noory/rag/` does not appear in git status (the gitignore effect).
