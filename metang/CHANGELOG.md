# Changelog

All notable changes to the metang plugin are documented here.

## [1.0.1] - 2026-06-23

### Fixed
- Removed the `hooks` field from the manifest. The standard `hooks/hooks.json`
  is loaded automatically, so referencing it in the manifest caused a
  "Duplicate hooks file detected" load error.

## [1.0.0] - 2026-06-23

### Added
- Initial release. A `UserPromptSubmit` hook (`hooks/metang_hook.py`) that
  injects an answer & question discipline reminder on every user turn:
  - **Explaining** — abstract to the right level (no raw name/identifier dumps,
    no empty `A`/`B` placeholders), pitch the abstraction to what the listener
    will do, and keep it short.
  - **Asking** — judge "must I actually ask this?" first; never ask about task
    order; ask only when the choice criterion or the data to decide is missing;
    confirm anything hard to reverse or outward-facing regardless.
  - **Scope** — governs the answer the user reads, not the model's private
    reasoning.
