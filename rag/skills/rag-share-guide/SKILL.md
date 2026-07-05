---
name: rag-share-guide
description: Guide to the three patterns for sharing a rag index/materials with a team. Example utterances "how to share rag", "share the index with my team", "how do I give it to someone else?", "rag-share-guide".
user-invocable: true
metadata:
  type: action
  version: v1.0.0
  plugin_version: "0.1.0"
---

# rag-share-guide — team sharing guide

Show the following body to the user as-is.

---

## Core principle

`.noory/rag/` is **gitignored by default**. It is not shared automatically. All sharing is explicit opt-in.

## Three patterns

### Option 1: commit only the materials on a personal work branch *(lightest)*

When you want to temporarily show your materials to a colleague — keep main clean.

```bash
git checkout -b <me>/rag-data
git add -f .noory/rag/raw/        # bypass gitignore
git commit -m "share rag corpus"
git push -u origin <me>/rag-data
```

Your colleague:
```bash
git fetch && git checkout <me>/rag-data
# raw/ is added to their project
/rag:rag-reindex             # the embeddings/graph are rebuilt on their own machine
```

Pro: the index is deterministic per machine, so it matches / Con: the first reindex takes time.

### Option 2: selective commit (`git add -f`) *(permanent team materials)*

Domain materials that every team member should have, like company architecture / service specs.

```bash
git add -f .noory/rag/raw/architecture.pdf
git add -f .noory/rag/raw/services/*.md
git commit -m "team rag corpus: architecture + services"
```

Team members pull, then `/rag:rag-reindex`. If the embedding model and chunking policy are the same, the results nearly match.

### Option 3: snapshot export/import *(large built corpus)*

When `raw/` is too big or awkward to put in git (internal docs, license issues, saving build time).

```text
Me:  /rag:rag-export ~/Downloads/team-rag-2026-05-22.tar.gz
     → upload to S3 / Google Drive / GitHub Release / internal file server

Colleague: after receiving, `/rag:rag-import ~/Downloads/team-rag-2026-05-22.tar.gz`
     → automatic validation of the embedding model/dim/version; the existing .noory/rag/ is backed up to .noory/rag.bak-<ts>/
```

Pro: no first reindex needed / Con: depends on one external store + version management being outside git.

## Recommendation matrix

| Scenario | Recommendation |
|---|---|
| Personal notes, occasionally shown to the team | Option 1 |
| Company-standard docs, needed by every new hire | Option 2 |
| Corpus of 1000+ files, reindex 30 min+ | Option 3 |
| `.noory/rag/raw/` is internal confidential material | Option 3 (git private repo) |

## Not recommended: vec.db / graph/ via Git LFS

Not recommended due to binary merge conflicts and LFS quota cost. If you really must, use Option 3 instead.

## Frequently asked problems

- **My colleague gets a dim mismatch on `import`.** → The two people's `settings.embedding.dim`/`model` differ. Match one side's settings to the other and retry.
- **The PDF I `git add -f`'d is large — is it OK without LFS?** → Under 50MB is usually OK. If larger, use LFS or Option 3.
- **I want to share only part of the materials.** → Option 2's `git add -f` lets you select per file.

## See also

- Quick start: `/rag:rag-help`
- Index status: `/rag:rag-status`
- Snapshot header structure: the "Snapshot format" section of `rag/README.md`
