# Changelog

## 0.1.2 — 2026-07-12

- Replace the stale hardcoded manifest-version assertion with a semantic-version contract while
  continuing to require Claude Code/Codex version parity.

## 0.1.1 — 2026-07-12

- Remove the duplicated `configure.py` command list and scope-selection rule from README.md; both
  now point to `skills/plainly-configure/SKILL.md` as the single canonical reference.
- Clarify the working directory assumed by README.md's manual-configuration and test-suite command
  examples.

## 0.1.0 — 2026-07-11

- Add Claude Code and Codex plugin manifests with one shared hook definition.
- Inject the selected style through `UserPromptSubmit` before each AI turn and restore it after
  compaction without post-answer continuation hooks.
- Add `brief`, `plain`, `guided`, and `professional` built-in profiles.
- Support environment, project, user, and external-file configuration with deterministic priority.
- Add the `plainly-configure` skill and cross-platform standard-library test suite.
- Isolate Windows tests from the real user profile and decode hook stdin as UTF-8.
- Fence external style text with collision-safe sentinels and document the project trust boundary.
- Read at most 8,193 bytes from an external file and store in-project style paths portably.
- Pin malformed JSON, non-UTF-8, relative-path, and adversarial-sentinel behavior with tests.
- Serialize project-relative paths with POSIX separators on every host and reject project settings
  that escape the project root through absolute paths, traversal, or symbolic links.
- Treat malformed UTF-8 hook input as an empty payload without blocking or stderr noise.
