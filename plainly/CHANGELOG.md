# Changelog

## Unreleased

## 0.5.0 — 2026-09-05

- Ship the styles as Claude Code output styles and delete the hook. The styles now reach the model
  through Claude Code's own loader: `output-styles/*.md` land in the session's system prompt, and
  Claude Code reminds itself each turn that the style is active. A hook could only append text
  after the user's message, where it carried less weight and repeated itself in every turn of the
  transcript. Choosing a style moves to `/output-style` and the host's own `outputStyle` setting,
  so `hooks/`, `src/plainly/`, `scripts/configure.py`, and the `plainly-configure` skill are gone
  along with `.plainly/settings.json` and the `NOORY_STYLE_*` environment overrides.

- Keep Claude Code's default coding instructions in place. Any output style that does not declare
  `keep-coding-instructions: true` removes them from the system prompt, and Plainly governs how a
  sentence reads rather than how code gets written. An unknown frontmatter key is discarded without
  a warning, so a misspelling of that key would load fine and drop the instructions in silence; the
  tests assert the exact spelling in all five files.

- Compose the shipped styles from single sources instead of repeating the fixed rules five times.
  `styles/` owns the baseline, the four deltas, and the fixed rules; `scripts/build_styles.py`
  joins them into the committed `output-styles/*.md`, which Claude Code reads as static files.
  `--check` fails when a source edit never reached the shipped files, and the test suite runs it.

- Drop Codex support. Codex has no output-style equivalent, so `.codex-plugin/plugin.json` and the
  Codex marketplace entry are gone rather than listing a plugin that would do nothing there. The
  release command now releases whichever host manifests a plugin ships.

- Rewrite the Korean rule that keeps an action in the predicate. The old check looked for the
  suffixes `-것`/`-함`/`-음`/`-화`/`-성` and runs of three nouns, so a sentence whose action
  sat in an ordinary noun — 이사, 방식 — passed untouched. That is exactly the shape a
  literal translation from English produces, because English packs the action into a noun and
  Korean carries it in the predicate. The rule now asks what the sentence says is being done,
  then names the two places that answer hides: an action noun that takes 되다/이다 while the real
  verb disappears, and a relative clause pushed under an empty head noun. Its examples are whole
  sentences from real answers instead of phrases. The tests assert the new wording on every
  style-resolution path and fail if either narrow trigger returns.

## 0.4.2 — 2026-08-19

- Rewrite the fixed Korean guidance with explicit subjects and literal verbs. The guidance no
  longer describes actions as trapped inside nouns, tells the writer to pull them out, uses a
  physical metaphor for a field of work, or leaves the actor implicit. Every style-resolution
  path is tested against both the required wording and the phrases that must not return.

- Write the Korean-writing guidance in Korean, and state it as rules with a check instead of a
  before-and-after list. Explaining in English how to write Korean asks the reader to build an
  English sentence and swap Korean words into it, which is the habit the section exists to break.
  Four rules replace the three examples: put the action in the predicate, do not coin a Sino-Korean
  name for an English term, attach the counter word when counting, and split a sentence that piles
  up modifying clauses. Each carries a check the reader can actually run — "find the predicate" in
  place of "read it aloud" — and its own before-and-after pair. The last line says the rules
  generalize, because a list of banned phrases only ever catches the phrase that produced it.

- Read a user-wide default from `<home>/.plainly/settings.json` when a project pins nothing, so a
  chosen style no longer has to be repeated in every repository. A project's own settings still
  win. This scope names a built-in profile only: a style file here would read from outside every
  project it applies to, which is the read that project settings are confined against, and a
  `style_file` key is reported and ignored rather than obeyed.
- Apply the style to every sentence written for a person — replies, documents, commit messages,
  comments, records — instead of conversation alone. The block said "communication only", so a
  document written in the same turn read as exempt and the rules stopped at what was spoken. The
  wording also draws the boundary the other way: the style governs how a sentence reads, never what
  a file must contain, so a project's own document rules stay separate and neither side repeats the
  other.
- Add a fixed vocabulary rule: a name a project uses among itself means nothing to the reader, so
  say what it does before using it, and introduce at most one new name per sentence. Identifiers,
  paths, and commands stay exempt because the reader can open them.
- Add a fixed brevity rule: shorten by cutting repetition, never by cutting a step.
- Carry the Korean writing guidance in the plugin instead of leaving each project to supply it.
  Nothing in that guidance was project-specific, yet a project that did not copy it lost the rules
  entirely. It is marked skippable in one line for anyone not writing Korean.
- Add the `decision` style: say what a change means and what it costs before naming a file,
  function, or command, and keep implementation detail for when it is asked for or when a risky
  decision turns on it.
- Add a fixed register rule outside the replaceable style boundary: a reply in a language that marks
  politeness grammatically addresses the reader in its polite register, and brevity is not a reason
  to drop it. No layer specified a register before, so the concision instructions alone decided it
  and Korean replies came back in plain form. The rule carries no style-level opt-out — an escape
  clause reopens the negotiation the rule exists to close, and no built-in style names a register.
- Move the honesty rule outside the replaceable style boundary so every built-in and external style
  prohibits presenting guesses as facts and requires unverified claims to be marked.

## 0.4.1 — 2026-07-25

- Make the language rule decidable and stop burying it. The 0.4.0 wording ("write as a fluent
  writer of its language would") sat inside the trailing instructions about Plainly itself and
  stated an aspiration rather than a test, so calques still shipped: a writer coining a compound
  from an English term has no moment where the old rule fires. The rule is now its own labeled
  paragraph carrying two checks a writer can run on a finished sentence — would a native speaker
  say this phrase aloud, and does the sentence still stand in English word order — each with the
  repair to apply.

## 0.4.0 — 2026-07-24

- Add a fixed language-quality rule to every hook injection, including external styles, to prevent
  English calques and needlessly difficult terminology while preserving technical terms that
  practitioners use untranslated.

## 0.3.0 — 2026-07-18

- Refactor built-in styles into one shared baseline plus focused brief, guided, and professional
  deltas while retaining `plain` as a compatibility alias.
- Add baseline guidance to mark unverified claims and distinguish facts from recommendations.
- Add an example-driven onboarding interview that selects the nearest preset or writes a validated,
  project-confined composed style when multiple preference deltas are selected.

## 0.2.0 — 2026-07-12

- Move persisted Plainly configuration to project-owned `.plainly/settings.json`.
- Remove saved user-global and `.noory/` settings; environment variables remain temporary
  overrides and missing project settings fall back to the built-in `plain` profile.
- Make the configuration CLI project-only and keep custom style paths portable and confined to the
  repository.

## 0.1.2 — 2026-07-12

- Replace the stale hardcoded manifest-version assertion with a semantic-version contract while
  continuing to require Claude Code/Codex version parity.

## 0.1.1 — 2026-07-12

- Remove the duplicated `configure.py` command list and scope-selection rule from README.md; both
  now point to `skills/plainly-configure/SKILL.md` as the single canonical reference.
- Clarify the working directory assumed by README.md's manual-configuration and test-suite command
  examples.

## 0.1.0 — 2026-07-11

- Add Claude Code and Codex plugin manifests with one shared hook definition.
- Inject the selected style through `UserPromptSubmit` before each AI turn and restore it after
  compaction without post-answer continuation hooks.
- Add `brief`, `plain`, `guided`, and `professional` built-in profiles.
- Support environment, project, user, and external-file configuration with deterministic priority.
- Add the `plainly-configure` skill and cross-platform standard-library test suite.
- Isolate Windows tests from the real user profile and decode hook stdin as UTF-8.
- Fence external style text with collision-safe sentinels and document the project trust boundary.
- Read at most 8,193 bytes from an external file and store in-project style paths portably.
- Pin malformed JSON, non-UTF-8, relative-path, and adversarial-sentinel behavior with tests.
- Serialize project-relative paths with POSIX separators on every host and reject project settings
  that escape the project root through absolute paths, traversal, or symbolic links.
- Treat malformed UTF-8 hook input as an empty payload without blocking or stderr noise.
