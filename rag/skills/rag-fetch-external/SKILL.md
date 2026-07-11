---
name: rag-fetch-external
description: Scrape external documents (Confluence, Google Drive, Notion, etc.) via installed official connectors and put them into the local index. rag does not hold external keys/connectors — it only uses them. Example utterances "put the Confluence doc into rag", "index the Notion page", "fetch and index the Drive doc", "rag-fetch-external", "pull in external docs".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.3.0"
---

# rag-fetch-external — fetch external documents and index them

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

## What

rag **does not hold** external service keys/connectors (zero-external-key identity). Instead, the active AI session uses the **official connectors** the user installed (e.g. Atlassian/Confluence, Google Drive, Notion MCP connectors) to scrape documents, saves them as markdown under `.noory/rag/raw/external/<source>/`, then runs them through the existing indexing pipeline (`rag-reindex`). It **separates fetching (the connector's job) from search (rag's job)**.

## Prerequisite: confirm the official connector is installed

When the user names a target service (Confluence/Drive/Notion, etc.), confirm **whether that service's official connector is connected to this session** (whether the corresponding MCP tool exists).
- If not: guide with "This task needs the <service> official connector. Install and authenticate it, then call me again." then stop. **rag does not authenticate on the user's behalf.**
- If yes, proceed to the steps below.

## Steps

1. **Confirm scope**: confirm with the user which space/folder/page to fetch (e.g. a specific Confluence space, Drive folder, Notion DB). Recommend narrowing if too broad.
2. **Scrape (via connector)**: query documents and extract bodies with the installed connector's MCP tools. (The **current session**, not the rag server, calls the connector.)
3. **Save locally**: save each document to `.noory/rag/raw/external/<source>/<slug>.md`.
   - `<source>` = the service identifier (e.g. `confluence`, `gdrive`, `notion`).
   - **Preserve the original source in the file front matter** (for tracing the original from search results):
     ```
     <!-- source: <original URL or identifier> | fetched: <YYYY-MM-DD> -->
     ```
   - This way, the `rel_path` (`external/confluence/…`) in search results identifies the external origin and the front matter finds the original.
4. **Index**: call the `/rag:rag-reindex` flow to index the saved content.
5. **Output summary**.

## Output format

```
✅ rag-fetch-external: fetched N docs from <source> and indexed them
   • saved: .noory/rag/raw/external/<source>/
   • original source: preserved in each file's front matter
   • index: chunks +M (rag-reindex)
```

## Cautions

- rag **does not install/authenticate connectors** — the user does that with the official plugin. This skill only **uses** an already-connected connector.
- Since documents may be personal/sensitive, remind that `.noory/rag/` is gitignored by default (excluded from sharing).
- If bulky, follow the `rag-reindex` batch guide.
