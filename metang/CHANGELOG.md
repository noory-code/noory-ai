# Changelog

All notable changes to the metang plugin are documented here.

## [1.4.1] - 2026-06-25

### Fixed
- **Off-by-one targeting.** A `Stop` hook can fire just before the finished
  reply is flushed to the transcript, so the gate read the *previous* turn's
  answer and judged the wrong reply (flagging a jargon dump one turn late, or
  faulting a fresh reply for something the earlier turn did). The gate now
  judges only an assistant reply that sits **after** the latest user message,
  and briefly polls (≤2s) for it to flush; if it never appears it skips (fails
  open) rather than judge a stale turn.
- **Judge scope.** The verdict now grades only *how* a reply is written
  (clarity, length, jargon, needless questions), not whether its topic is
  expected — a user-steered subject change is no longer mistaken for dodging.

### Added
- `gateDebug` config (default `false`) — one diagnostic line per fire to
  `<tempdir>/metang_gate.log`.

## [1.4.0] - 2026-06-25

### Added
- **Answer gate (`Stop` hook).** The reminder is injected at the *start* of a
  turn; on a long, tool-heavy turn it drifts far from where the final answer is
  written and loses pull. A new `Stop` hook (`hooks/metang_gate.py`) closes the
  loop: when the turn is about to end it reads the answer just produced and asks
  a cheap model (`claude -p` under the user's own subscription auth — no API key)
  whether it obeyed the discipline. A clear violation blocks the stop with a
  one-line reason, so the model rewrites in plain language; a pass ends the turn.
- Config keys `gateEnabled` (default `true`) and `gateModel` (default `"haiku"`),
  with `/metang:config gate on|off`.

### Notes
- **Fails open.** Any judge error, missing CLI, timeout, or malformed transcript
  lets the turn through — the gate never traps the conversation.
- One bounce per turn (never loops); a recursion sentinel keeps the judge from
  judging its own output; `stdin` is closed so the judge reads only its prompt.
  Adds ~3-4s at a turn's end when it runs.

## [1.3.0] - 2026-06-23

### Added
- Per-section toggles: `explainEnabled` / `askEnabled` in `.metang.json`, with
  `/metang:config explain on|off` and `ask on|off`. Turning one off drops just
  that section from the reminder; the other stays.

### Removed
- The whole-plugin `enabled` flag (and `/metang:config on|off`). It duplicated
  Claude Code's own plugin enable/disable — use that to silence metang entirely.

## [1.2.0] - 2026-06-23

### Added
- `/metang:config` slash command — a real interface for the config instead of
  hand-editing JSON: `on` / `off` / `status` / `init` / `reset` /
  `explain <text>` / `ask <text>`, with an optional `global` target. The hook
  reads the config every turn, so changes apply on the next message.
- `init` seeds `.metang.json` with the current built-in defaults as an editable
  starting point, sourced live from the hook via a new `--dump-defaults` mode
  (the hook script stays the single source of the default rule text).

## [1.1.0] - 2026-06-23

### Added
- Optional `.metang.json` config (project root overriding `~/.metang.json`):
  - `enabled: false` mutes the reminder without uninstalling.
  - `explainRules` / `askRules` replace the default bullets in either section.
  - No config file → built-in defaults, unchanged behavior.

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
