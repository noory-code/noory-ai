---
name: flow-verify-commit
description: |
  After Action implementation completes, run verify → code review (R2) → atomic commit → status update → retrospective (R3). The core skill of the action-finish Phase.
  Use in the following situations: (1) after implementation completes, "verify it", "commit it", (2) at the point an Action implementation completes,
  (3) "verify + review + commit", (4) when a retrospective needs to be written.
  Use this skill for verify/review/commit/retrospective **right after Action implementation**. The overall progress and wrap-up of a work item is orchestrated by the `flow` entrypoint, which calls this skill at the action-finish stage.
user-invocable: true
metadata:
  type: procedure
  version: v1.1.0
---

# Flow Verify & Commit

The procedure a teammate performs after finishing implementation: verify → code review (R2) → atomic commit → status update → retrospective (R3). It is not tied to task type or tools; the verification commands and delegation areas are filled in by the playbook the project supplies.

## Agent Teams mapping

Each step of this procedure maps to Agent Teams components (`flow` skill §"Agent Teams mapping model" SSOT):

| Procedure step | Agent Teams mapping |
|---|---|
| Static analysis / test / quality gate | hooks (quality gate — TaskCompleted) |
| R2 code review | plan approval (main↔user) or independent review agent (mailbox) |
| Retrospective RT (R3) placeholder block | hooks (quality gate — TaskCompleted) |
| Status update | shared task list (⬜/🔄/✅) |

## Preconditions

- A teammate (Layer developer, etc.) has finished implementation
- The implemented code is not yet committed

---

## Resolution procedure

### Step 1: Run static analysis

Run the **verification command (playbook-supplied)** the project provides. The playbook defines the per-language/framework static-analysis commands and target paths (both implementation code and test code).

> 🚨 **No missing verification-target paths**: if you check only the implementation code and drop the test-code paths, compile/type errors on the test side are missed and discovered after commit. The playbook's verification command must include both the implementation and test paths.

> **Quality-gate adapter (optional)**: if the project has declared checks via `checks` (free-form names + `required`; legacy `commands` accepted) in `.flow/settings.json`, run `uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/hooks/quality_gate_cli.py" run` at the verification step to invoke/record the declared checks (`hook_audit.jsonl` → aggregated by audit_report) and **block on a required failure** (minimal failure behavior — non-zero exit). If `checks` is undeclared, no-op (pass). This is a thin adapter that standardizes the "playbook verification command" above via a settings declaration — it is a calling convention at the verification step, not a hook deny.

**Judgment**:
- 0 errors → proceed to Step 2
- errors occur → fix the errors, then re-run
  - fix missing imports, type mismatches, etc. immediately
  - report serious structural problems to the user

**Note**: informational/warning results pass; only errors block (follow the playbook's severity criteria).

---

### Step 2: Run tests (if applicable)

#### 🚨 AC verification-method cross-check (Hard Gate)

**Before running tests**, check the **"verification method" column** in the completion-criteria table of A-NNN.md.

1. Read the completion-criteria (AC) table in A-NNN.md.
2. Check whether the "verification method" column has keywords like `test` or `unit test`.
3. **If the keyword is present**: a test for that AC **must** exist.
   - If there is no test artifact → ❌ **block commit**. Warn the user: "AC-N's verification method is 'test' but there is no test."
   - If there is a test artifact → run it with the project verification command (playbook-supplied) and confirm it passes.
4. **If the keyword is absent** (code review, static analysis, etc.): running tests is optional.

**Judgment**:
- All tests pass → proceed to Step 3
- Tests fail → analyze the cause of failure, then fix
  - Existing tests broken: fix the implementation code or the test
  - New test fails: verify the implementation, then fix

**When there is no test**: skipping is allowed only if the AC cross-check passes. If the AC specifies "test" verification, skipping is banned.

---

### Step 2.5: AI code review — R2 spec

**Condition**: when there are code-file changes (may be omitted for docs/config-only changes — but running it is recommended for meta work)

> **R2 (Code Review during execution)** mechanism — delegation-area persona input + 4 essence-attack priorities + RT re-review + 2-consecutive-agreement advisory.
> **SSOT**: `../debate-redteam` §R1/R2 invocation payload standard. This Step is an SSOT citation + explicit Flow placement.

#### 🚨 Quantitative-output main cross-check (Hard Gate — extension of `../../rules/` verify-before-assert)

**Quantitative claims** contained in the implementation output — whether produced by a delegated agent or by the main directly — are not trusted as self-reports; **the main re-verifies them directly by code/full cross-check** (numbers/no-regression reported as "all done" are unconfirmed until cross-checked). Both delegated and direct are targets (`verify-before-assert` = "ground-truth before asserting — regardless of who produced it". Its § agent/subtask assertion row = subagent-report cross-verification, and the main's own output follows the same principle): if delegated, the main cross-checks the agent's output; if direct, the main cross-checks its own output (not exempt — only the cross-checking subject differs). Cross-check types:

| Quantitative claim | Main cross-check method |
|----------------|----------------|
| Number of doc fields / "N kinds·N items" count | Cross-check the actual count with `grep -c` / `ls \| wc -l` on the target file |
| "No regression / all passed" | The **main runs the relevant tests/verification commands in full, directly** |
| "0 impact / unchanged / unreferenced" | **Re-grep** the impact paths (suspect the path/scope first — a wrong path gives a false 0) |

> **The more negative the result (0 items·no regression·unchanged), the more you suspect the tool/path/scope first** (`verify-before-assert` §negative result — stale/wrong paths create false passes). In an Action with a quantitative claim, not running the cross-check = R2 incomplete (commit blocked — regardless of delegated/direct).
>
> ⚠️ **Entry-condition exception**: this gate is **independent** of Step 2.5's "when code files change" condition — even for docs/config-only changes, **run it if there is a quantitative claim (field count·count, etc.)** (quantitative claims exist for doc changes too — first row of the table above). Even if Step 2.5 is skippable, run this cross-check when there is a quantitative claim.

1. Check the list of changed files + decide the applied persona. The **delegation area (teammate assignment — project-defined)** is mapped by the playbook to a teammate/persona per changed path:

   ```bash
   git diff --name-only HEAD
   ```

   | Changed area | Applied persona (delegation area — project-defined) | Persona SSOT |
   |---------|------------------------------------|-------------|
   | Domain area | Layer developer (Domain) — playbook-assigned teammate | Project persona definition |
   | Data area | Layer developer (Data) — playbook-assigned teammate | Project persona definition |
   | Presentation area | Layer developer (Presentation) — playbook-assigned teammate | Project persona definition |
   | Test area | QA lead (veto) — playbook-assigned teammate | Project persona definition |
   | UI component area | UI designer — playbook-assigned teammate | Project persona definition |
   | Meta area (skills/rules/hooks) | Manager (Flow Manager) | `../../rules/` manager-persona SSOT |
   | Multiple areas at once | Combined input of multiple personas | Cite all relevant definitions |

2. Run the **independent review agent (R2)** — apply the **`../debate-redteam` §R2 invocation payload standard**:

   ```
   Prompt (R2 payload standard):
   "Please review the changed files [list].

   [Persona input — `../debate-redteam` §R2 standard]
   - Applied delegation area: {Domain | Data | Presentation | Test | UI | Manager}
   - Core Beliefs (3): {cite the relevant persona definition's Core Beliefs}
   - Anti-patterns (5): {cite the relevant 5 Anti-patterns}
   - Sanity Self-Questions (4): {cite the relevant persona definition}

   [4 essence-attack priorities — `../debate-redteam` §R2 standard (+ this Step's local extension: quantitative-output main cross-check)]
   1. Persona misfit: is the output consistent with the target delegation area's Core Beliefs?
   2. Anti-pattern exposure: have the 5 Anti-patterns crept into the output?
   3. Essential defect: Hard Gate / gray zone / dependency order / TDD pairing / Flow-responsibility encroachment (§R2 standard list — cite without variation). **[This Step's local extension]** quantitative-output main cross-check not run (see §Quantitative-output main cross-check Hard Gate above)
   4. Single-option alternative advisory: if the output is a single approach only, propose at least 1 alternative

   [Output format]
   - Result per each of the 4 essence-attack priorities: 1 line each
   - High-priority issues (must resolve): N (file + line + fix proposal)
   - Alternative proposals: N (optional)
   - R3 self-attack, 1 line: 'Is it enough as a justification for avoidance?'
   "
   ```

3. **Handle the first review result** (`../../rules/` gate-enforcement-default-on applied):
   - **High severity issue** → fix immediately → re-run verification → RT re-review (item 4)
   - **Low severity issue** → record in Step 5 retrospective Problem section → RT re-review (item 4)
   - **No issue** → RT re-review (item 4) (2-consecutive-agreement advisory enforced)
   - **On avoidance** → block commit + state the justification (only the user's explicit bypass expression is allowed)

4. **RT re-review (2-consecutive-agreement advisory — resolves RT weakness #3)**:
   - If the review agent said "no issue" or "fixes complete" in the first review, call once more with the same persona input
   - In the second review, **attack from a different angle** (e.g., add "gray-zone cases possibly missed in the first review" to the second prompt)
   - 2 consecutive passes → proceed to Step 3
   - New issue found in the second review → fix, then re-review (recursive)

   > 2-consecutive-agreement advisory spec: a single review by the same persona is a weakness. Reinforce confidence with 1 additional re-attack.

   > **Fallback when an independent review agent is unavailable**: if calling the independent review agent fails or the environment does not provide one — substitute AI self-review. The same payload (persona + 4 essence-attack priorities — `../debate-redteam` §R2 standard) self-check + a required 1-line result. **Self-review is also mandatory to run** (`../../rules/` gate-enforcement-default-on — zero runs, zero times banned).
   >
   > **R2 self-review permitted-objective-condition matrix SSOT**: `../flow-planning-action` § Action Planning AI Plan Review Gate R1 spec (5-case matrix — single artifact / same-pattern multiple / Asset consistency / new large body / code work). Cases 1–3 self-review OK, cases 4–5 independent review agent mandatory.

5. **Apply meta work** (skills/rules changes):
   - Manager-persona input (`../../rules/` single citation of the manager-persona SSOT)
   - Apply the 4 essence-attack priorities as-is

---

### Step 3: Atomic commit

After verification passes, perform the git commit.

#### 🚨 Full derived-artifact confirmation Hard Gate

A project with a code-generation step **must** check all derived-artifact (generated-file) changes with `git status` before committing. The playbook defines that project's derived-artifact patterns.

```bash
# Hard Gate: must run after code generation — confirm the playbook's derived-artifact patterns
git status --short
# All emitted derived files must be included in staging
```

**If violated**: a missing derived artifact causes a split commit → violates the atomic-commit principle.

```bash
# 1. Check changes
git status
git diff

# 2. Stage only the relevant files (full confirmation including derived artifacts)
git add [changed files]

# 3. Commit (work-based format)
git commit -m "[epic][story][action] work description

- implementation detail 1
- implementation detail 2"
```

**Commit-message rules**:
- Work-based (Action): `[epic-name][story-title][action-title] work description`
- General: `type: subject` (Conventional Commits)
- Details: see `../../rules/` commit rules

**Atomic-commit principle**:
- 1 commit = 1 responsibility
- An independently verifiable unit
- Include only logically related files

---

### Step 4: Update A-NNN.md status

If an Action doc exists, update it to completed status.

```markdown
# In A-NNN.md
Status: ⬜ → ✅

# Also update each Step's checkbox
- [ ] Step 1 → - [x] Step 1
```

🚨 **Immediate-update Hard Gate**:
- **Right after each Step completes** (before entering the next Step), immediately mark `[x]` with the `Edit` tool
- Batched updates **banned**
- Verify: `grep -c "\\[ \\]" [A-NNN.md]` result must match the number of incomplete Steps
- If violated: progress cannot be tracked, and omissions cannot be identified at retrospective/commit time

---

### Step 5: Retrospective handling (AI-behavior evaluation — settings-aware)

First check `retrospective.levels.action.rigor` in `.flow/settings.json`.

| action.rigor | Step 5 handling | Step 5.5 R3 |
|--------------|-------------|-------------|
| `none` | Skip writing the Action retrospective. Record only a settings note in A-NNN.md: `Action retrospective skipped (retrospective.levels.action.rigor=none)` | Skip |
| `minimal` | Write a retrospective of at least 1 line with no placeholders | Skip |
| `template` | Write a KPT or equivalently meaningful retrospective | Skip |
| `template+rt` | Write a KPT retrospective | Run |

> `none` is not "retrospective writing banned" but "exemption from the mandatory Action-level retrospective requirement." Story/Epic retrospective rigor follows each level's setting separately.

If it is not `none`, write the Action-level retrospective.

**Retrospective = AI-behavior evaluation** (not a work-result summary)

#### Evaluation items

| Item | Evaluation content |
|------|----------|
| Delegation choice | Was the correct delegation area (teammate) assigned? |
| Context understanding | Was the Action doc understood correctly? |
| Procedure adherence | Were the procedure-doc Steps followed in order? |
| Retry count | Were there unnecessary retries? |
| Inefficiency | Is there anything that can be improved? |

#### Retrospective form (except `minimal`)

```markdown
### Action retrospective: A-NNN [title]

**Keep** (what went well):
- ...

**Problem** (inefficiency):
- ...

**Try** (improvement):
- ...
```

---

### Step 5.5: Retrospective RT attack — R3 spec (when action.rigor = template+rt)

Run right after writing the Step 5 retrospective, right before commit (or right before wrap-up if Step 3 already passed). **R3 (retrospective RT attack)** mechanism — block the retrospective from passing as placeholder/platitudes.

> R3 spec source: `../debate-redteam` §R3 (runs right after the Step 5 retrospective) + resolves the "no essence attack" retrospective aspect of the 4 RT weaknesses.

**5 attack patterns** (on finding the following patterns, require a retrospective rewrite):

| # | Pattern | Example | Block reason |
|---|------|------|----------|
| 1 | "generally went well" / "same again next time" | "generally proceeded smoothly" | No concrete event/behavior — Keep is void |
| 2 | "not sure" / "nothing in particular" | "Problem: nothing in particular" | Thought avoidance — every Action has inefficiency |
| 3 | Keep/Problem/Try at the same level of abstraction | Keep "followed procedure well" → Try "follow procedure well next time too" | Try is not decomposed into a concrete action item (target/priority) |
| 4 | Problem has only external causes (tool/user/time) | "because the tool was slow / the user replied late" | Avoids evaluating one's own procedure — not an AI-behavior evaluation |
| 5 | Retrospective is a work-result summary (code/feature evaluation) | "feature X added. tests pass" | Not an AI-behavior evaluation |

**Verification checklist**:
- [ ] Keep ≥ 1 + specifies concrete behavior/event (0 mere "did well" type)
- [ ] Problem ≥ 1 + specifies procedure violation/inefficiency (0 external-cause-only)
- [ ] Try ≥ 1 + priority/target/content table (decomposed into action items)
- [ ] 0 of the 5 attack patterns above match
- [ ] Is the retrospective an "AI-behavior evaluation" (not a work-result summary)

**If it does not pass**:
- State to the user which pattern it matched (e.g., "pattern #1 (generally went well) — Keep item 1 needs rewriting")
- Require a retrospective rewrite → block commit until it passes (`no-commit-without-retro` Hook reinforced)
- Rewrite also matches the same pattern → ask the user to write the retrospective directly, or temporarily hold this Action's retrospective + hand off to a follow-up Action

**Verification command** (grep-based first-pass auto-filter — not a 100% block, only strong-pattern cases):
```bash
# grep the keywords of patterns #1, #2, #5 (roughly)
grep -iE "generally|nothing in particular|next time too|work complete|feature added" {retrospective section of A-NNN.md}
# Output present = auto-rewrite candidate. No output ≠ pass (manual 4-axis verification required)
```

---

### Step 6: Update _story.md

Reflect the Action's completion status in the Story doc (shared task list sync).

```markdown
# In _story.md's Action list
- [ ] A-001: title → - [x] A-001: title
```

---

## Checklist

- [ ] Project verification command (playbook-supplied) 0 errors?
- [ ] Tests pass? (if applicable)
- [ ] R2 code review passed? (on code change)
- [ ] Quantitative output (field count·count·no-regression) re-verified by code/full cross-check? (when a quantitative claim exists — regardless of delegated/direct)
- [ ] `git commit` complete?
- [ ] A-NNN.md status ✅ updated?
- [ ] Action retrospective policy handled? (skip note if `action.rigor=none`, R3 passed if `template+rt`)
- [ ] _story.md updated?

---

## MUST NOT

- ❌ Commit without verification
- ❌ Combine multiple Actions into one commit
- ❌ Proceed to the next Action without checking the Action retrospective policy (including whether `action.rigor=none` skip is allowed)
- ❌ Skip the status update
