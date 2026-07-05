---
name: retro-processing
description: Retrospective-processing work type — accumulated retrospective set → identify recurring patterns → improvement proposals → review → apply. Auto-apply forbidden (human-controlled).
---

# retro-processing (retrospective processing)

A work type that periodically processes the retrospectives that accumulate with every task (Φ5). It finds **recurring patterns** in the retrospective set, derives improvement proposals from them, and — **after review** — applies them to procedures, rules, and playbooks. It does not fix things automatically — a human triggers it and review is the gate.

## Scope

- Work that gathers accumulated retrospectives (Action/Story/Epic) and converts them into improvements
- The point at which the same pattern (recurring Problem / recurring Try) appears across several retrospectives and a procedure improvement is needed
- Not applicable: writing a one-off retrospective during an individual task (that belongs to each work type's retrospective stage) / code changes (→ `feature`/`bug`/`refactor`)

## Procedure

1. **Collect the retrospective set** — gather `archives/retro-*.md` (the unapplied-retrospective queue — one flat file per entry scale, `flow-archive`) / output: retrospective set (source list)
2. **Identify recurring patterns** — classify the Problems/Trys that recur across multiple retrospectives together with their frequency / output: pattern list (pattern + occurrence count + source)
3. **Derive improvement proposals** — a concrete improvement for each recurring pattern (which procedure/rule/playbook, and how) / output: improvement-proposal list (target + change + supporting pattern)
   - **Principle+reason over prohibition**: the default form of an improvement proposal is not adding a new prohibition ("don't do X") but **describing why it should be done, with the reason**, or **tightening existing guidance**. Stacking prohibitions one line at a time bloats rules and skills and prevents generalization. A prohibition (MUST NOT) belongs only to hard constraints where the act itself is a failure. Canonical source (SSOT) = `meta-rule-procedure §Constraint expression — principle+reason over prohibition`.
4. **Review** — review whether the proposal solves the essence and has no side effects (a mandatory gate before applying) / output: review result (adopt / defer / reject + reason)
5. **Apply** — apply the adopted proposals to their targets (procedure/rule/playbook) / output: applied change + traceability (which pattern → which change)
6. **Condense after applying** — in the changed area, **clean up the now-dead parts within the same cycle** (block bloat). The check targets are the 4 kinds in `ssot-vocabulary §pruning criteria` (duplicate definition / dead origin / synonym variant / dead cross-ref) / output: condensation result (removed/merged items + changed area)
   - **Timing**: right after apply (⑤). Run the 4-kind dead-code check on the body added by the retrospective apply plus the existing area adjacent to it.
   - **Check flow**: apply the 4 kinds in `ssot-vocabulary §pruning criteria` to the changed area → on finding dead content, merge/remove/fix cross-refs.
     - **Duplicate definition** found → keep one SSOT + convert copies into references
     - **Dead origin** found → condense the origin citation (for a retrospective already absorbed, keep only the citation and remove the body)
     - **Synonym variant** found → unify the wording (converge on one expression)
     - **Dead cross-ref** found → update or remove the reference
   - **Re-recording duty**: include the condensation result in procedure ⑦'s record log (trace the apply → condense → record chain).
   - **Boundary**: only the *changed area + adjacent area* are in scope. Not a full rules/skills scan (that is a separate periodic task). Keep the "clean up at the same time as adding" principle.
   - **Auto-cleanup vs report — Hard Gate**: simple dead code (e.g. dead cross-ref) is cleaned up automatically. Ambiguous meaning (wording unification / merge judgment required) is reported to the reviewer for a decision. Bypassing via the AI's own judgment is forbidden (`gate-enforcement-default-on`).
7. **Record** — leave the processing result in the retrospective-processing log (trace applied + condensed + deferred parts) / output: processing log
8. **Empty the queue** — **actually remove** the applied parts from the archive queue (`git rm`/edit + commit). The queue = only the unapplied parts remain.
   - **Zero deferred (everything applied)**: delete the `archives/retro-*.md` file entirely.
   - **Deferred parts remain**: remove the applied/already-applied parts (Try + related retrospective body) from the queue and **shrink the queue to hold only the deferred Trys**. The full pre-apply retrospective (Keep/Problem, etc.) is preserved by git history, so it is not kept in the queue.
   - ❌ **Attaching a header only and leaving the applied body in the queue is forbidden** — the queue is not emptied, so the next processing run treats the same applied parts as a candidate again (origin: 0.13.1 retro-processing's own retrospective — misread as "delete only the fully-applied queue", so a header was attached but the body remained).
   - Content remaining in `archives/` = only the still-unapplied parts (the deferred queue). Apply traceability is preserved by the processing log (procedure ⑦) / output: queue holding only the deferred parts (+ file deletion when everything is applied)

> **Backlog routing (convention)**: among the 5-kind classification, **backlog** items — especially **plugin core / upstream improvements** (`retro-evolution` M5: installed users cannot modify directly, only propose upstream) — are not immediate-apply (⑤) targets; instead they are **registered as tickets on the internal board designated by the project (issue tracker / project board)** (a single queue for follow-up work). The publish action = the `flow-upstream-publish` skill (a detailed ticket's 5 elements — problem / recurring source / target asset / proposal / done criteria). The board location and access rights are **supplied by the project** — with no permission, registration is deferred + the user is notified (the convention stays). A project-local backlog (things about that project's playbook/memory) is not a board target (the project handles it itself). ⚠️ The board-coordinates SSOT = the `upstream_board` in the project's `settings.json`. Because it is an internal-only tool (private↔private), an **internal default board is baked into the plugin** (`config-defaults.json`; `flow-config`/`flow-upgrade` seed it into settings, overridable) — the publish/processing skills read it from settings (the skill body does not hold the board name directly).

> The concrete authoring procedure for an improvement target (procedure/rule/playbook) is delegated to the corresponding meta procedure (`meta-*-procedure`). This playbook defines only the generic retrospective→improvement flow.

## AC format

Specify each improvement proposal with 5 fields.

- **Given** — the recurring pattern (occurrence count + source retrospectives)
- **When** — the improvement proposal is applied
- **Then** — the structure in which the pattern will not recur (procedure/rule/playbook change)
- **Verification method** — review consensus + post-apply traceability (a pattern→change mapping exists)
- **Success/failure criteria** — review adopted + apply traceable = PASS / applied without review, or a change with no supporting pattern = FAIL

> "Works fine / seems OK" style unmeasurable ACs are forbidden.

Example (domain-agnostic — a recurring-omission pattern):

- **Given** — a "verification step omitted" Problem recurs across 3 retrospectives
- **When** — add a verification Hard Gate to that procedure (improvement proposal)
- **Then** — the missing verification is structurally blocked
- **Verification method** — proposal adopted in review + confirm the gate is applied in the procedure (grep)
- **Success/failure criteria** — review adopted + gate applied = PASS / applied without review = FAIL

## Hard Gate

> **HARD GATE**: applying without review (procedure ④) is forbidden (auto-apply forbidden)
> On non-compliance: procedure ⑤ (apply) is blocked — a proposal must pass review before it can be applied. Automating retrospective→improvement is deliberately left out (Φ5 control).
> Bypass: only on the user's explicit phrasing (skip / move on / bypass / skip over)

> **HARD GATE**: deriving an improvement proposal without a recurring-pattern basis (procedure ②) is forbidden
> On non-compliance: procedure ③ is blocked — it must be grounded in a recurring pattern (sources ≥2), not a one-off opinion.
> Bypass: only on the user's explicit phrasing

> **HARD GATE**: proceeding to record (⑦) without condensation (⑥) after apply (⑤) is forbidden — a duty to clean up dead code every cycle so that retrospective applies do not accumulate as bloat
> On non-compliance: procedure ⑦ (record) is blocked — the condensation stage must apply the 4 kinds in `ssot-vocabulary §pruning criteria` to the changed area.
> Bypass: only on the user's explicit phrasing (consistent with `gate-enforcement-default-on`)

## Feedback-loop locations

1. **Procedure ④ (review)** — the core loop. Present the proposal (verify) → check side effects/essence (feedback) → revise the proposal → re-review
2. **Procedure ② (identify recurring patterns)** — the pattern-frequency confirmation loop (defer if occurrences < 2)
3. **Procedure ⑥ (condense after apply)** — apply the 4 kinds in `ssot-vocabulary §pruning criteria` to the changed area → on finding dead code, clean up (simple = automatic / ambiguous meaning = decide after reporting) → block bloat before record (⑦)

> This playbook is itself the work type that "turns retrospectives into improvements". Retrospectives from other work types become the input (procedure ①) of this playbook.

## Review/evaluation points

- **Review**: procedure ④ (improvement-proposal review — essence solved / side effects / priority). Delegate when the project supplies a review teammate. **RT running default-on** (strength/independence = README §7 + RT strength matrix). RT essence attack: whether the essence is solved, side effects, auto-apply risk.
- **Evaluation**: apply traceability of the adopted proposal (pattern→change mapping) + passing the review gate = the output-evaluation criteria.
- `flow-procedure-story` §7-2 review/evaluation Hard Gate enforces execution of the points above.

## Violation handling

- An apply without review / an improvement proposal with no supporting pattern = blocked or sent back for completion
- A bypass is allowed only on the user's explicit phrasing + a duty to record it in the retrospective's Problem section
