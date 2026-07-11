# Changelog

## 0.14.0 — 2026-07-12

Self-service lifecycle skills so mechanical Stage flows are executed, not
re-derived from hook source each session:

- New `stage-archive` skill and `stage/scripts/archive_work.py` one-shot helper.
  Archiving a completed/rejected item is now a single validated, idempotent
  command (`archive_work.py W-… | --all-completed`) that moves the item and its
  retrospective into `past/work/archive/`, records the terminal status in
  `archive/index.md`, and drops the present-flow rows.
- Clarified the archive contract: archiving passes exactly ONE gate — a per-path
  archive intent. `.stage/` is excluded from `is_source_path`, so the
  registration and commit gates never fire on it and NO new work item is needed
  to archive. New `hooks/tests/test_archive_gate.py` locks this, guarding against
  the false "two gates" belief that once spawned a spurious archive work item.
- New `stage-work` skill: plan the work, confirm scope with the human, then
  register the item and its `active.md` row before touching governed files.
- New `stage-handoff` skill: route open work between LLM windows by `venue`, make
  each item self-carrying, and point the human at the window with open work.
- `stage-retrospective` now delegates archiving to `stage-archive` (SSOT) instead
  of carrying its own archive-intent block.
- Fix: a shell redirection after `git commit` (`2>&1`, `> out`, a piped `| tail`)
  was read as a commit pathspec and produced false registration-gate denials on
  ordinary commit invocations. `git_commit_pathspec_files` now stops argument
  scanning at the first redirection; real `-- path` pathspecs are still caught.

## 0.13.0 — 2026-07-12

Work-item routing for multi-agent projects:

- New optional `venue` frontmatter field on work items names the execution
  surface that should carry out the work — the routing hint a human reads to
  open the right window when more than one agent or session works a project.
  Added to `templates/project-stage/present/work/items/_template.md` and
  surfaced as a `Venue` column in `present/work/active.md`.
- Field is advisory: no hook gates on `venue`, and the frontmatter parser
  already ignores/defaults unknown or absent keys — existing work items and
  `.stage/` instances stay valid with no migration.
- Values are project-defined, like `kind`. `operations/artifacts.md` documents
  the field; `past/canon/vocabulary.md` gains a `Venue` term plus a
  clearly-marked two-surface example `kind -> venue` routing table the project
  replaces. The harness fixes no venue names.

## 0.12.1 — 2026-07-12

Documentation-accuracy pass (no runtime behavior change):

- PostToolUse hook coverage synced across docs: root `README.md`'s Hooks
  section, the project-injected `templates/project-stage/operations/hooks.md`
  (plus its delete-gate wording), and both `docs/BLUEPRINT.md` hook diagrams
  (§10, §15) now include the `PostToolUse` hook shipped in `hooks/hooks.json`
  since 0.12.0.
- Evergreen violation removed from `hooks/README.md`: a past-review-round
  citation ("Codex round-10 review, Low") is dropped from the doc body —
  history belongs in CHANGELOG/commit records, not doc bodies.
- `docs/IMPLEMENTATION_AUDIT.md`: P3's stale "Gap" status is closed (it
  conflicted with P26's own claim of having resolved it), and the conclusion
  now matches the scope actually listed in the 구현된 범위 table instead of
  undercounting it.
- `README.md`/`skills/README.md` skill descriptions had drifted between the
  two files; `skills/README.md` is now the sole canonical wording and
  `README.md` links to it instead of restating.

## 0.12.0 — 2026-07-11

The two items the re-review debate deliberately split out
(`.discuss/stage-review-debate-2026-07-11.md` §분리 항목), each through its
own codex review rounds. **Codex hosts must re-trust the plugin's hooks
(TUI `/hooks`) after upgrading — the hook set changed.**

- Shell WRITE extraction joins delete extraction on the shared command-group
  scaffolding: output redirects and cp/mv/tee/`sed -i` targets are anchored
  at the tracked effective cwd (a preceding `cd` rebases them, fail closed),
  `--` ends option parsing, and redirect classification is quote-aware —
  quoted/escaped `<`/`>` carry sentinels through tokenization, so
  `echo "> src/app.py"` is an argument, `cp x 'src>backup.py'` keeps its
  full destination, a redirect inside a DOUBLE-quoted command substitution
  (`echo "$(printf x > rogue.py)"`) is still gated, and a single-quoted
  literal (`echo '$(...)'`) is not.
- Intent consumption is two-phase (measured: both hosts deliver PostToolUse;
  Codex 0.144.0 includes `tool_response`/`tool_use_id`, also for failing
  commands): the promotion gate's rename reservation is held through tool
  execution and PostToolUse completes it, so a tool crash or a rejected
  permission prompt after the allow no longer burns the authorization. A
  claim whose post never arrives is restored to a pending intent after ten
  minutes (measured from reservation, stamped at claim time); posts consume
  only their OWN claim (tool_use_id/session correlation), and a re-planted
  intent wins over a stale claim — one authorization never becomes two.
- hooks.json: new PostToolUse hook; both tool-use matchers widen to `*` so
  the `extra_write_tools` settings seam (0.11.0) actually fires for names
  the static matcher cannot know. Unknown tools still return the early
  allow.

## 0.11.0 — 2026-07-11

Ten agreed items from the v0.10.0 full re-review debate (Claude self-review ↔
Codex, five rounds, joint sign-off — `.discuss/stage-review-debate-2026-07-11.md`
§R5), in the agreed priority order, plus two mid-batch review rounds.

Gates:

- `extra_write_tools` in `.stage/settings.json`: registered host/MCP
  file-writing tool names are classified before the unknown-name early allow,
  putting them behind the registration/promotion/hierarchy/governance gates
  (content payloads project into the hierarchy gate and dereference symlinks
  like `Write`); a mistyped registration marks settings untrusted. Unregistered
  names remain ungated — now documented in §Limits and the host contract.
- Archive transitions keep their evidence: a present item archives only from
  exactly `completed|rejected` (`archived` is maintenance of archive-located
  records), a rejected item requires its completed retrospective
  (`retrospective_ref`) — rejection reasons are learning assets — and the
  archive-index row (Final status = the state the `archived` overwrite erases)
  lands in the same archive intent.
- The promotion gate validates LAST, so a call denied by any other gate no
  longer burns the pending intent (atomic rename reservation); the remaining
  pre-time window and the one-command re-issue are documented.
- File deletions are gated like writes: `rm`/`del`/`erase`/`Remove-Item`/`ri`
  operands (cwd-anchored, `--`-aware, fail closed across possible anchors) run
  the registration/promotion pipeline. The cwd tracker also follows a cd into
  a directory the same command creates (`mkdir s && cd s && …`) — closing a
  pre-existing delete-gate bypass.

Audit (new findings — existing projects may see new errors; run the audit
after upgrading and close them):

- ARCHIVE001–004: archived items indexed with a terminal Final status,
  completed transitions keep closed gates, every archived item keeps a
  completed retrospective, index rows point at real records.
- BACKLOG008/009, ROADMAP001/002, PROPOSAL001/002: each future family's index
  matches its records in both directions (roadmap theme rows are exempt).
- RETRO002 / DECISION002: reverse links — a completed item's
  `retrospective_ref` is the one binding retrospective, and a recorded
  decision must be linked back from its work item's `decision_refs`.
- BACKLOG007: backlog parent chains must not cycle (same contract as WORK018).
- SCHEMA001 (warning): `.stage/settings.json` `schema_version` missing or
  different from the plugin's contract version (`STAGE_SCHEMA_VERSION`,
  independent of the release version; new harnesses are stamped, preserved
  settings are never overwritten).

Infrastructure:

- Cross-platform CI (`.github/workflows/stage.yml`): both suites, an
  init→audit `--strict` smoke, and the real hook entrypoint on
  ubuntu/macos/windows × python 3.9/3.12.
- One frontmatter→WorkItem constructor with an explicit missing-field policy
  (gate: safe progress / audit: empty), both policies pinned.
- stage-retrospective SKILL archives the index row in the same intent.

## 0.10.0 — 2026-07-11

- P31 record-graph audit: `scripts/stage_records.py` scans every frontmattered
  W/R/DE/B/state record once into typed nodes and reference edges (topology
  documented in one table), and every audit link check reads that graph —
  per-check globbing/re-parsing and cross-method side channels are gone. The
  finding surface (codes, messages, paths, order) is unchanged, held by an
  ordered kitchen-sink pin test plus the per-code suite.

## 0.9.0 — 2026-07-11

- P33 module split: `hooks/stage_guard.py` (3,010 lines) is now a thin
  entrypoint — payload plumbing, tool-gate orchestration, event handlers, and
  facade re-exports (597 lines) — over six sibling modules: `stage_paths`
  (path canonicalization + governance), `stage_shell` (shell tokenization,
  cwd tracking, the `.stage` delete gate, write-path extraction), `stage_git`
  (git invocation parsing), `stage_work` (work-item graph + edit projections),
  `stage_runtime` (`.runtime/` intent slots, session summaries, ack pruning),
  and `stage_context` (SessionStart context assembly). Every module
  self-bootstraps `sys.path`, and `stage_guard` re-exports all
  consumer-referenced symbols, so direct execution (`hooks.json`),
  `import stage_guard`, and file-path loading are unchanged. Behavior is
  identical: both test suites pass on python 3.9 and current, guarded by the
  facade coverage pin (`hooks/tests/test_facade.py`).
- Dead code dropped (no caller anywhere): `_contains_stage`, `git_subcommand`,
  `open_items_for_paths`, `latest_session_summary`.
- Codex hosts: the plugin's hook script set changed — re-approve hook trust
  (TUI `/hooks`) after upgrading.

## 0.8.0 — 2026-07-11

- External-review gate (`operations/review.md`, routed in `index.md`): findings
  from an external review (codex, another agent, a human) are not accepted
  uncritically. The gate anchors on the work's purpose and `past/canon` truth,
  rebuts findings that do not serve the goal, sends the rebuttal back for a
  counter-review, and processes only the survivors — recording what was
  accepted and rebutted. Rebuttal is goal-alignment verification, not
  contrarian nitpicking; when rounds stop converging the remaining edges are
  documented best-effort rather than chased. Injected into every project Stage
  creates.

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
