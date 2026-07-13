# Stage Skills

Stage provides lifecycle entry skills including:

- `stage-init`: creates or repairs `.stage/`.
- `stage-migrate`: performs the one-shot schema-v3 to schema-v4 migration and pre-commit abort.
- `stage-audit`: audits the `.stage/` structure and work status.
- `stage-decision`: applies the principle-based decision gates.
- `stage-retrospective`: performs the mandatory post-work retrospective.
- `stage-discuss`: runs asynchronous file-based discussions between different LLM sessions.

These skills operate on Markdown and plain files, so they work on Codex, Claude, Windows, Linux, and macOS.
