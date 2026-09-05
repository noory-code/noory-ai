# Plainly

Plainly ships five output styles for Claude Code. Selecting one puts the style into the session's
system prompt, where Claude Code keeps it for every turn. The plugin carries no hook and no code
that runs at prompt time.

## Built-in styles

Every style includes the shared baseline. The other four add one focused delta.

| Style | Delta from the baseline |
|---|---|
| `Baseline` | None; clear, concise, honest communication |
| `Brief` | The shortest length the task allows |
| `Decision` | What a change means and what it costs, before any file or command name |
| `Guided` | Step-by-step explanations for non-experts |
| `Professional` | A formal, neutral workplace register |

## Selecting a style

Pick one with `/output-style`, or name it in `.claude/settings.json`:

```json
{ "outputStyle": "plainly:Brief" }
```

A project's own `.claude/settings.json` overrides the user-wide one. Claude Code owns this
setting; Plainly neither reads nor writes it. A new choice applies to the next session.

Claude Code disables output styles in safe mode, and Plainly does nothing there.

## Fixed rules

Every style carries the same honesty, language-quality, vocabulary, brevity, and register rules
after its own text. The honesty rule prohibits presenting guesses as facts and requires unverified
claims to be marked. The language rule favors natural, plain, precise wording while preserving
technical terms that practitioners normally use untranslated. The register rule addresses the
reader in the polite register of any language that marks politeness grammatically, and brevity
never overrides it. None of them choose the response language.

The language rule carries one per-language section, for Korean, which is itself written in Korean:
explaining in English how to write Korean invites the very habit it warns against, building an
English sentence and swapping Korean words into it. It states four rules — put the action in the
predicate, do not coin a Sino-Korean name for an English term, attach the counter word when
counting, split a sentence that piles up modifying clauses — each with a check and a
before-and-after pair. A reader writing another language skips it.

## Coding instructions

Claude Code removes its default coding instructions from the system prompt for any output style
that does not ask to keep them. Plainly governs how a sentence reads and says nothing about how
code is written, so every shipped style declares `keep-coding-instructions: true`.

An unknown key in a style file's frontmatter is discarded without a warning, so a misspelling of
that key would load fine and drop the instructions in silence. The test suite asserts the exact
spelling in all five files.

## Install

```text
/plugin marketplace add noory-code/noory-ai
/plugin install plainly
```

Claude Code only. Codex has no output-style equivalent.

## Development

`styles/` owns the sources: `baseline.md`, the four deltas, `fixed-rules.md`, and the names and
descriptions in `profiles.json`. Claude Code reads `output-styles/*.md` as static files and cannot
join those pieces at load time, so the composed files are built and committed:

```text
python3 scripts/build_styles.py
python3 scripts/build_styles.py --check
```

Edit a source, rebuild, and commit both. `--check` fails when a committed file no longer matches
its sources, and the test suite runs it.

Run the tests from the `plainly/` package directory:

```text
python3 -m unittest discover -s tests -q
```

To see the styles load without releasing the plugin:

```text
claude -p --plugin-dir plainly \
       --settings '{"outputStyle":"plainly:Brief"}' \
       --debug-file log.txt
grep "output styles from plugin plainly" log.txt
```
