# Plainly

Plainly is one Claude Code output style. Selecting it puts a set of writing rules into the
session's system prompt, where Claude Code keeps them for every turn. The plugin is a single
markdown file — no hook, no code that runs at prompt time.

## What the rules cover

They govern how a sentence reads, never what a file must contain, and they apply to everything
written for a person: replies, documents, commit messages, comments, records.

| Rule | What it asks for |
|---|---|
| Honesty | Mark uncertainty where the claim appears; use conditional wording for hypotheses. |
| Meaning | Preserve facts, quantities, conditions, and uncertainty when rewriting. |
| Language | Compose in the reader's language instead of translating an English sentence across. |
| Vocabulary | Explain unfamiliar terms using the reader's stated knowledge as context. |
| Brevity | Preserve needed information while matching the requested length and format. |
| Register | Address the reader in the polite register of a language that marks one. |

The Korean section gives three steps in Korean: express actions and states directly, choose familiar
words that preserve the meaning, and split long sentences without dropping conditions. It keeps
established technical terms and permits short noun phrases for buttons, titles, and table labels.
Sentences longer than 15 space-separated units prompt another look; this is an editing cue, not a
grammar rule or a hard limit.

A final silent check compares actors, objects, actions, conditions, certainty, and missing or added
facts with the source. In particular, an unmeasured effect must not become an assumed improvement.
These instructions guide generation; they are not a separate verifier or a guarantee of accuracy.
Readers writing another language skip this section. Tests check the style's structure and stated
rules. Actual Claude responses must be reviewed separately to assess writing quality.

## Selecting it

Pick it with `/output-style`, or name it in `.claude/settings.json`:

```json
{ "outputStyle": "plainly:Plainly" }
```

A project's own `.claude/settings.json` overrides the user-wide one. Claude Code owns this
setting; Plainly neither reads nor writes it. A new choice applies to the next session.

Claude Code disables output styles in safe mode, and Plainly does nothing there.

## Coding instructions

Claude Code removes its default coding instructions from the system prompt for any output style
that does not ask to keep them. Plainly governs how a sentence reads and says nothing about how
code is written, so the style declares `keep-coding-instructions: true`.

An unknown key in a style file's frontmatter is discarded without a warning, so a misspelling of
that key would load fine and drop the instructions in silence. The test suite asserts the exact
spelling.

## Install

```text
/plugin marketplace add noory-code/noory-ai
/plugin install plainly
```

Claude Code only. Codex has no output-style equivalent.

## Development

`output-styles/plainly.md` is the whole plugin. Edit it directly; nothing is generated.

Run the tests from the `plainly/` package directory:

```text
python3 -m unittest discover -s tests -q
```

To see the style load without releasing the plugin:

```text
claude -p --plugin-dir plainly \
       --settings '{"outputStyle":"plainly:Plainly"}' \
       --debug-file log.txt
grep "output styles from plugin plainly" log.txt
```
