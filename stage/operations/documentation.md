# Documentation

This document owns what a Stage body must contain and must leave out. How a sentence reads — word
choice, word order, naming, length — is not decided here.

Work cards follow the scale-specific body contract in `docs/SCHEMA_V5.md`. Its requirement that
each scale's `Purpose` contain exactly one sentence is structural cardinality, not a prose-style
length rule.

## Readers

Every Stage body is read by someone who did not write it: the operator supervising the work, and
the agent that executes or reviews it.

Write for a vocational high-school student who has studied programming or business and has never
opened this codebase. They know what a file, a table, a list, a command, and a test are. They do
not know this project's names, its history, or which line of code a body is about.

## Rules

- Bodies declare only durable current truth.
- Motivation and history live in decisions, commits, pull requests, and retrospectives.
- Section names describe the essence, not past confusion.
- Avoid self-invalidating meta narration.
- Write at that reader's level. A body that needs another file open to carry its meaning has
  failed. Principle names, record IDs, and paths are the exception: the principle catalog and the
  file system own those meanings.
