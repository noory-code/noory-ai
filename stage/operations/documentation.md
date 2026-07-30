# Documentation

This document owns the writing rules.

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
- Say what a thing is before using its name. A term taken from the code carries its meaning on
  first use; only after that does it stand alone.
- Introduce at most one new term per sentence.
- Brevity comes from cutting repetition, never from cutting a step. State the fact, why it is a
  problem, and what it causes.
- Do not assemble a word by translating an English term piece by piece. If nobody says the result
  out loud, it is not the word: say what the thing does, or keep the form practitioners use. This
  applies to every language a body is written in.
