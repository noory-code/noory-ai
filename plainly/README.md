# Plainly

Plainly injects a selected communication style immediately before Claude Code or Codex processes a
user prompt. It never uses `Stop` or another post-answer continuation hook.

## Built-in profiles

| Profile | Behavior |
|---|---|
| `brief` | Answer and essential details with minimal wording |
| `plain` | Clear everyday language with enough context (default) |
| `guided` | Plain-language, step-by-step explanations |
| `professional` | Concise, precise, neutral workplace language |

Ask the AI to show, select, or reset styles. The `plainly-configure` skill applies the change at
user scope by default; say "this project only" to use project scope.

## Resolution order

Plainly reads the first valid source on every `UserPromptSubmit` event:

1. `NOORY_STYLE_FILE`
2. `NOORY_STYLE_PROFILE`
3. `<project>/.noory/plainly/settings.json`
4. `~/.noory/plainly/settings.json`
5. Built-in `plain`

An external style must be a non-empty UTF-8 file no larger than 8,192 bytes. Relative paths in
`NOORY_STYLE_FILE` resolve from the hook payload's working directory. Relative paths in project
settings resolve from the project root; relative paths in user settings resolve from the user
settings directory. The project CLI stores in-project style files as portable relative paths.
Project settings reject absolute paths, `..` traversal, and symbolic links that resolve outside the
project root. Environment and user settings remain user-controlled and may reference external
files. Style text is scoped to wording, tone, structure, and detail; it cannot authorize tools or
override higher-priority instructions.

## Trust boundary

Project settings and their referenced style files become model-visible developer context on every
prompt. Use project-scoped Plainly configuration only in repositories you trust and review changes
to `.noory/plainly/` like other instruction files. Plainly fences style text with explicit
sentinels, neutralizes sentinel text inside the file, and tells the model to ignore task, tool,
permission, and higher-priority instructions found there. Project settings also cannot read a style
file that resolves outside the project root. These controls reduce accidental scope leakage but do
not make an untrusted repository safe.

Manual configuration is also available:

```text
python3 scripts/configure.py list
python3 scripts/configure.py show --project-root <workspace>
python3 scripts/configure.py set-profile brief --scope user --project-root <workspace>
python3 scripts/configure.py set-file <style.md> --scope project --project-root <workspace>
python3 scripts/configure.py reset --scope project --project-root <workspace>
```

Changes take effect on the next user prompt because the hook resolves the style for every turn.
`SessionStart` with source `compact` restores the same style after context compaction.

## Install

Claude Code:

```text
/plugin marketplace add noory-code/noory-ai
/plugin install plainly
```

Codex:

```text
codex plugin marketplace add noory-code/noory-ai
codex plugin add plainly@noory-ai
```

Codex requires one-time review and trust for the bundled command hook through `/hooks`.
Both hosts invoke `python3`; Windows environments without that command need a compatible Python 3
launcher or command adapter.

## Development

```text
python3 -m unittest discover -s tests -q
```
