# Plainly

Plainly is one Claude Code output style. Selecting it puts a set of writing rules into the
session's system prompt, where Claude Code keeps them for every turn. The plugin is a single
markdown file — no hook, no code that runs at prompt time.

## What the rules cover

They govern how a sentence reads, never what a file must contain, and they apply to everything
written for a person: replies, documents, commit messages, comments, records.

| Rule | What it asks for |
|---|---|
| Honesty | No guess stated as fact. Unverified claims marked as unverified. |
| Language | Compose in the reader's language instead of translating an English sentence across. |
| Vocabulary | Say what a name does before using it. One new name per sentence. |
| Brevity | Shorten by cutting repetition, never by cutting a step. |
| Register | Address the reader in the polite register of a language that marks one. |

The language rule carries one per-language section, for Korean, which is itself written in Korean:
explaining in English how to write Korean invites the very habit it warns against, building an
English sentence and swapping Korean words into it. It states four rules — put the action in the
predicate, do not coin a Sino-Korean name for an English term, attach the counter word when
counting, split a sentence that piles up modifying clauses — each with a check and a
before-and-after pair. A reader writing another language skips it.

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
