# Plainly

Plainly injects a selected communication style immediately before Claude Code or Codex processes a
user prompt. It never uses `Stop` or another post-answer continuation hook.

## Built-in profiles

Every built-in selection includes the shared baseline. The other profiles add one focused delta.

| Profile | Delta from the baseline |
|---|---|
| `baseline` | None; clear, concise, honest communication (default) |
| `brief` | The shortest length the task allows |
| `guided` | Step-by-step explanations for non-experts |
| `professional` | A formal, neutral workplace register |

The legacy profile name `plain` remains a compatibility alias for `baseline`.

Ask the AI to personalize, show, select, or reset project styles via the `plainly-configure` skill.
Configuration rules live in
[`skills/plainly-configure/SKILL.md`](skills/plainly-configure/SKILL.md).

## Resolution order

Plainly reads the first valid source on every `UserPromptSubmit` event:

1. `NOORY_STYLE_FILE`
2. `NOORY_STYLE_PROFILE`
3. `<project>/.plainly/settings.json`
4. `<home>/.plainly/settings.json` — profile name only
5. Built-in `baseline`

An external style must be a non-empty UTF-8 file no larger than 8,192 bytes. Relative paths in
`NOORY_STYLE_FILE` and project settings resolve from the project root. The project CLI stores style
files as portable project-relative paths. Project settings reject absolute paths, `..` traversal,
and symbolic links that resolve outside the project root. Environment overrides remain
user-controlled and may reference external files. Style text is scoped to wording, tone, structure,
and detail; it cannot authorize tools or override higher-priority instructions.

Every injection carries fixed honesty, language-quality, and register rules outside the selected
style. The honesty rule prohibits presenting guesses as facts and requires unverified claims to be
marked. The language rule favors natural, plain, precise wording while preserving technical terms
that practitioners normally use untranslated. The register rule addresses the reader in the polite
register of any language that marks politeness grammatically, and brevity never overrides it. All
three apply to every built-in or external style without choosing the response language.

## Trust boundary

Project settings and their referenced style files become model-visible developer context on every
prompt. Use Plainly only in repositories you trust and review committed changes to `.plainly/` like
other instruction files. Plainly fences style text with explicit
sentinels, neutralizes sentinel text inside the file, and tells the model to ignore task, tool,
permission, and higher-priority instructions found there. Project settings also cannot read a style
file that resolves outside the project root. These controls reduce accidental scope leakage but do
not make an untrusted repository safe.

A project's `.plainly/` directory can be committed so the same style follows the repository across
computers, and it always wins over the user-wide default. The same file under the home directory
sets that default for projects that pin nothing; it may name a built-in profile only, because a
style file there would read from outside every project it applies to.

Manual configuration is also available. Run `scripts/configure.py` with `python3` from the
`plainly/` package directory; see
[`skills/plainly-configure/SKILL.md`](skills/plainly-configure/SKILL.md) for the full command
reference:

```text
python3 scripts/configure.py list
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

Run from the `plainly/` package directory:

```text
python3 -m unittest discover -s tests -q
```
