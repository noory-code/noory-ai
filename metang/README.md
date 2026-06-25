# metang

A Claude Code plugin that injects **answer & question discipline** into every
user turn, so the model explains clearly and stops asking questions it could
answer itself.

It exists because the same guidance, written into memory or a CLAUDE.md rule,
gets buried in long conversations and stops being followed. A `UserPromptSubmit`
hook re-injects it on **every** turn instead, right before the model answers.

## What it enforces

**Explaining**
- Don't dump raw names/identifiers (file, repo, function, command). Abstract:
  say what happened and what it means as one graspable whole.
- Don't dodge with empty placeholders either (`A`, `B`, "the object"). Point at
  real things, but at a level that carries meaning.
- Pitch the abstraction to what the listener will *do* with it; surface exact
  names only when they must act on them.
- Keep it short — over-unpacking is its own failure.

**Asking**
- When a decision arises, first judge "must I actually ask this?" — asking is
  not the default.
- Never ask about task order or how to proceed; decide it.
- Ask **only** when (1) the criterion for the choice is missing, or (2) the
  criterion is known but the data to decide is missing.
- Anything hard to reverse or outward-facing still gets confirmed, regardless.

**Scope** — this governs the *answer the user reads*, not the model's private
reasoning. Thinking stays free.

## Configuration

Use the **`/metang:config`** command — it edits `.metang.json` for you:

```
/metang:config status            # show current state
/metang:config explain off       # drop the explaining section
/metang:config explain on
/metang:config ask off           # drop the asking section
/metang:config ask on
/metang:config gate off          # turn off the Stop-hook answer-check
/metang:config gate on
/metang:config explain <text>    # replace the explaining rules
/metang:config ask <text>        # replace the asking rules
/metang:config init              # seed the current defaults as an editable starting point
/metang:config reset             # back to built-in defaults
```

Add `global` (e.g. `/metang:config explain off global`) to target
`~/.metang.json` instead of the project. The hook reads the file **every turn**,
so changes apply on the next message — no restart needed. To silence metang
entirely, disable the plugin in Claude Code (that switch already exists).

The file it manages, if you prefer editing by hand:

```json
{
  "explainEnabled": true,
  "askEnabled": true,
  "explainRules": "- your own explaining rules, replacing the defaults",
  "askRules": "- your own asking rules, replacing the defaults",
  "gateEnabled": true,
  "gateModel": "haiku"
}
```

- `explainEnabled` / `askEnabled: false` — drop that section from the reminder.
- `explainRules` / `askRules` — replace the bullets in that section. Omit a key
  to keep its defaults. The scope line (answer-only, not reasoning) always stays.
- `gateEnabled: false` — turn off the Stop-hook answer-check (the start-of-turn
  reminder stays). `gateModel` — which model judges the answer (default `haiku`).
- The project `.metang.json` overrides `~/.metang.json`; with no file, defaults apply.

## How it works

`hooks/hooks.json` wires a `UserPromptSubmit` command hook to
`hooks/metang_hook.py`. The script reads the hook JSON from stdin (content
unused) and returns the rule via `hookSpecificOutput.additionalContext`, which
Claude Code adds to context before the model responds. The rule text lives in
that one script — its single source.

The same file also wires a `Stop` hook to `hooks/metang_gate.py`, which runs
when the turn is about to end. It pulls the answer just written from the
transcript and asks a cheap model (`claude -p`, the user's own auth — no API
key) whether it followed the discipline; a clear violation blocks the stop with
a short reason so the model rewrites, anything borderline passes. It **fails
open** — any error allows the turn through — and never loops (one bounce per
turn). This catches what the start-of-turn reminder misses once it has drifted
out of the model's recent context. Toggle with `gateEnabled` / `gateModel`.

## Install

Local (development):

```
/install-plugin /absolute/path/to/noory-ai/metang
```

From the marketplace, once published to `noory-ai`:

```
/plugin   →  enable  metang@noory-ai
```

Hooks load at session start, so enable it, then start a new session.

> Enable it through **one** channel only. Wiring the same hook in
> `settings.json` *and* enabling the plugin injects the rule twice per turn.

## License

MIT
