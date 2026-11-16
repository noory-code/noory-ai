# Plainly

Plainly is one Claude Code output style. While the plugin is enabled it puts a set of writing rules
into the session's system prompt, where Claude Code keeps them for every turn. The plugin is a
single markdown file plus its eval cases — no hook, no code that runs at prompt time.

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
established technical terms and permits short noun phrases for buttons and titles; a table cell
that explains something is written as a sentence. Korean builds a sentence around its verb where
English builds it around nouns, so the section asks the writer to rebuild a noun-centered sentence
rather than swap its words, especially when reporting after reading English code, logs, or command
output. It names a few words people do not say, with what to write instead, and forbids dropping
particles, endings, or verbs to save characters. Sentences longer than 15 space-separated units
prompt another look; this is an editing cue, not a grammar rule or a hard limit.

A final silent check compares actors, objects, actions, conditions, certainty, and missing or added
facts with the source. In particular, an unmeasured effect must not become an assumed improvement.
These instructions guide generation; they are not a separate verifier or a guarantee of accuracy.
Readers writing another language skip this section. Tests check the style's structure and stated
rules. Actual Claude responses must be reviewed separately to assess writing quality.

## Turning it on and off

The style declares `force-for-plugin: true`, so enabling the plugin applies it; no `outputStyle`
setting is needed. While the plugin is enabled, Claude Code uses this style in place of whatever
`outputStyle` names, so using another output style means disabling the plugin:

```text
/plugin disable plainly@noory-ai
```

A change applies to the next session. Claude Code disables output styles in safe mode, and Plainly
does nothing there.

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
claude -p --plugin-dir plainly --debug-file log.txt
grep "Using forced plugin output style" log.txt
```

## Evals

`evals/` holds cases for `claude plugin eval`. Each case is a `prompt.md` and one or more
`graders/*.md`; nothing in the folder runs. The command asks every case with the plugin enabled
and again without it, and reports the score difference.

| Case | What it checks |
|---|---|
| `style-active` | The session names Plainly as its output style. It fails in both arms if the style stops loading. |
| `work-report`, `two-axes`, `live-test`, `explain-to-colleague` | Korean answers carry none of the shapes the Korean section removes: em dashes, "재측정", "축", "실기"/"실측", chained "의", and a noun followed by "진행하다"/"수행하다"/"실시하다". |

The graders are regular expressions, so a run costs only the Claude sessions it starts: five cases,
three runs each by default, in two arms. They check the shape of a sentence, not whether it kept the
meaning; read the answers for that. Run from the repository root:

```text
claude plugin eval plainly --trust-plugin
```

`--trust-plugin` answers the first-run prompt that asks whether you trust this plugin directory.
Results go to `plainly/evals/results/`, which git ignores.
