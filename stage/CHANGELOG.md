# Changelog

## 0.7.0 — 2026-07-10

- Hardening from the full-audit design proposals (P28-P35):
  relative_to_workspace resolves existing symlink parents + `..` so a symlink
  into `.stage/past` can no longer dodge the promotion gate; recursive-delete
  detection adds `find .stage -delete`/`-exec rm`; SessionStart injects all
  handoffs tied on the newest mtime; the audit verifies operations/artifacts.md
  and RECORD_LOCATIONS stay in lock-step (CATALOG001); vague operation-doc
  thresholds are replaced with explicit conditions; the instruction inventory
  documents its selected-backlog relevance signal. P31 (record-graph audit) and
  P33 (module split) are deliberately deferred — see docs/IMPLEMENTATION_AUDIT.md.
- Final-entry identity for exact-path gates (Codex round-12 review, 5 findings):
  an entry-canonical form (parents resolved, leaf kept as named) now backs
  `promotes`/intent/archive matching, so a grant for one leaf never covers a
  sibling symlink aliasing the same target; patch projection matches headers
  the same way targets are selected (symlinked work-item leaves cannot slip a
  `parent:` change past the hierarchy gate); the OS-script suffix check is a
  per-form conjunction (`.stage/run.sh -> outside.txt` is still an `.sh` entry
  inside `.stage`); governance prefixes match on both canonical and lexical
  forms (an escaping `exclude_paths` symlink keeps excluding); and a symlinked
  `.stage/settings.json` stays classified stage-internal, so the malformed-
  governance gate cannot deny its own repair. Second pass: find's pre-path
  traversal options (`-H/-L/-P`, BSD `-E/-X/-x/-s/-d/-f`, GNU `-O/-D`) no
  longer hide the start paths from the whole-tree deletion check, and the
  registration/scope matchers include the entry-canonical form so `alias/link`
  (alias -> src) is governed — and authorizable — as the entry `src/link`.
  Third pass: `find -- .stage` (end-of-options separator) is scanned past, and
  a recursive delete rooted at an ANCESTOR of `.stage` (`rm -rf .`,
  `find . -delete` — filtered or not, since the hook cannot evaluate find
  expressions) is denied as deleting the Stage tree. Fourth pass: the resolved
  (leaf-dereferenced) form participates only in fail-closed directions —
  find's `-H/-L/-follow` modes traverse a symlink root, so the link-only
  exemption is dropped there; configured governance exclusions win on the
  entry/lexical forms only (deleting `src/link -> generated/file` acts on the
  governed entry, structural `.stage`/`.git` exclusions still win on any
  form); and scope matching drops the target's leaf-deref form so two leaves
  aliasing one file never cross-authorize. Fifth pass: clustered BSD find
  flags (`find -Lx .stage -delete`) are scanned past (and carry follow mode);
  a preceding `cd` rebases relative delete operands (`cd build &&
  find . -delete` cleans build, not the workspace); and ancestor deletes cover
  the workspace's logical `.stage` entry, so removing the workspace cannot
  silently detach an externally symlinked harness. Sixth pass: the workspace's
  own `.stage` symlink entry is never link-exempt (removing it detaches the
  harness); GNU `find -delete` roots at the implicit `.`; a failed `cd`
  (missing directory) keeps the previous anchor; scope authorization uses the
  entry-canonical form alone (a lexical collapse like `alias/../other/x`
  cannot smuggle authorization); canonical classification is authoritative in
  the delete gate, so a foreign `.stage` basename outside the project
  (`cd build && rm -rf .stage`) is no longer denied by spelling; and find's
  follow mode honors the LAST `-H/-L/-P`. Seventh pass: the cwd tracker keeps
  a SET of possible anchors — a conditionally executed cd (`false && cd build
  ; rm -rf .stage`) adds its state instead of replacing the workspace anchor,
  and any anchor hitting the Stage tree denies; structural exclusions join
  configured ones in winning on entry/lexical forms only, so deleting a
  governed entry whose leaf points into `.git` still requires registration.
  Eighth pass: a pipeline-local cd (`cd build | rm -rf .stage`) keeps the
  caller anchor; bare `cd`/`cd -`/`popd` track HOME and the previous anchor
  set instead of acting as no-ops; and declaration parsing (scope, promotes,
  intent paths) keeps `..` intact so a spelling through a symlink
  (`scope: alias/../other`) canonicalizes to its real entry instead of a
  mis-anchored lexical collapse. Ninth pass: shell control operators are
  tokenized as their own tokens even without whitespace (`true;find .stage
  -delete`) and across newlines/background `&`; a cd through a missing
  intermediate (`cd build/missing/..`) fails like the real shell instead of
  collapsing to `build`; `pushd`/`popd` track a directory stack and `cd -`
  tracks OLDPWD; and find's follow-mode scan skips `-exec` program arguments so
  a `-P` handed to the exec'd program cannot cancel `-L`. Tenth pass: the
  tokenizer runs on the whole command (multiline quotes and backslash
  continuations survive), drops heredoc bodies, and turns unquoted newlines
  into separators; the write scan and cwd conditional both recognize `&`
  (background); the cwd model keeps a failed-cd branch, swaps on bare `pushd`,
  fails a multi-operand `cd`, and treats `cd build & …` as a subshell; the find
  grouper keeps an escaped `\;` exec terminator inside the find group; `find --`
  accepts dash-led roots; and a file-valued symlink scope no longer
  cross-authorizes the distinct target it points at (only directory scopes
  dereference). Eleventh pass: heredoc-body removal is quote-aware (a quoted
  `'<<EOF'` is literal text, not a heredoc); the find `-exec … \;` terminator
  is only honored inside an actual `find` group; and redirections
  (`cd build >/dev/null`) are stripped before counting cd operands. Twelfth
  pass: quoted/escaped `;`/`&`/`|` and fd-redirection `&` (`2>&1`) carry
  sentinels so they never read as separators; `<<` inside `$(( ))` arithmetic
  is not a heredoc; heredoc delimiters keep punctuation (`END-MARKER`) and a
  missing delimiter no longer swallows the rest of the command; and `pushd -n`
  edits only the stack without moving the tracked cwd. Thirteenth pass: a
  failed cd/pushd no longer advances OLDPWD or pushes a phantom stack entry;
  attached `&>`/`&>>` redirections are stripped; leading wrappers (`command`,
  `nohup`, …) and PowerShell cwd verbs (`Set-Location`) are normalized; bare
  `(( … ))` arithmetic suppresses heredoc detection; `cd -- -foo` honors the
  end-of-options marker; heredoc delimiters accept backslash/split quoting
  (`<<\EOF`); and the whole-tree delete gate fires for a strict-ancestor delete
  only when a `.stage` exists (a pre-init workspace is not over-denied).
  Fourteenth pass: the cwd tracker follows bash `cd -L` logical semantics (`..`
  pops a segment lexically so `cd link ; cd ..` returns to link's logical
  parent); a cd into a directory without execute permission fails; `pushd
  +N/-N` rotate the directory stack; PowerShell backtick-escaped separators are
  literals; and a heredoc terminator matches exactly (`<<`) or strips only
  leading tabs (`<<-`), so a space-indented delimiter line stays body.
  Fifteenth pass (representative subset — the rest documented as best-effort):
  a redirection glued to a cd operand (`cd build>/dev/null`) is split off; an
  unknown cd option (`cd -Z`) fails closed; and a CONTENT write (Write/Edit)
  that follows a symlink is governed and scope-matched by the resolved target,
  so a write through `.git/link.py -> src/app.py` or `aliases/link.py` cannot
  modify the governed source outside a work item's scope. Rarely-hand-typed
  shell forms (`cd -P`, `pushd +N`, `nohup cd`, find-predicate-spelled options)
  are left as documented best-effort — see hooks/README.md.
- Over-engineering audit (review-gate lens on the accepted findings): removed
  the `pushd +N/-N` indexed stack rotation (contradicted the round-15 decision
  to leave it best-effort) and dropped `nohup`/`nice`/`time`/`stdbuf` from the
  cd-wrapper set (they cannot run the `cd` builtin, so peeling them was
  fail-open — now their `cd` is a no-op that keeps the caller anchor).

## 0.6.0 — 2026-07-10

- Security/correctness fixes from a full adversarial audit (10 findings):
  lexical `..`/`.` normalization closes registration/promotion/delete bypass;
  multi-target registration requires every path covered (not any); recursive
  delete detection is tokenized (rm -R/--recursive, rmdir /s, Remove-Item
  -Recurse); git commit pathspec is registration-checked; hierarchy is judged
  on the patch's post-state; legacy session-summary migration never drops a
  handoff; audit gains bidirectional lineage (WORK023/BACKLOG006), orphan
  decision/retrospective validation (DECISION001/RETRO001), template file-type
  (TEMPLATE003), and exact routing-row matching.

## 0.5.0 — 2026-07-10

- SessionStart inventories host-project instructions (CLAUDE.md, AGENTS.md,
  .cursorrules, copilot-instructions, .claude/rules and skills) and injects a
  use-and-challenge directive: apply them while planning/executing, and when
  one contradicts observed reality, register an open question with a proposed
  correction instead of silently deviating or obeying. Before/During gates and
  the stage-decision Truth Gate carry the same rule.

## 0.4.0 — 2026-07-10

- Audit: SSOT001 (duplicate record IDs across files), OWN001 (records outside
  their owning catalog location, including body-only heading IDs), ROUTE001/002
  (existing artifact locations and operations documents missing from index.md
  routing). Template index now routes the model record directories.

## 0.3.0 — 2026-07-10

- SessionStart injects the newest three open questions and up to three
  `status: selected` backlog records as bounded one-line entries.

## 0.2.0 — 2026-07-10

- Multi-session `.runtime/`: per-(work item, path) promotion intents consumed
  by atomic rename reservation, per-session Stop handoffs with skew-safe
  pruning, per-session question-gate markers, lazy migration of 0.1.0 slots.

## 0.1.0 — 2026-07-10

- Initial release: `.stage/` artifact structure, init/audit/promote-intent
  CLIs, entry skills, and one hook set enforcing registration, promotion,
  hierarchy, commit, and portability gates on Claude Code and Codex.
