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

## How it works

`hooks/hooks.json` wires a `UserPromptSubmit` command hook to
`hooks/metang_hook.py`. The script reads the hook JSON from stdin (content
unused) and returns the rule via `hookSpecificOutput.additionalContext`, which
Claude Code adds to context before the model responds. The rule text lives in
that one script — its single source.

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
