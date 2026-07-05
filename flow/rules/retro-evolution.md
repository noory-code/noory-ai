# retro-evolution — retrospective → evolution loop (accumulation + independent reflection)

**The rule that forces retrospectives not to evaporate but to accumulate and be preserved, and forces their reflection (asset evolution) to happen independently of the flow unit (Epic/Story/Action) (retro-processing), under human control.**

> Procedure SSOT: `flow-retrospective` Part 3 + `playbooks/retro-processing.md`. This rule = the enforcement signal + cross-ref (see the procedure for the classification taxonomy / stage details — no body duplication).

## MUST

- **M1 classification**: tag every retrospective Try with the 5-way classification (rule / skill / playbook / memory / backlog — taxonomy: `flow-retrospective` Part 3-1). Classification time = writing the retrospective + retro-processing step ② (pattern identification).
- **M2 independent reflection**: reflection (asset evolution) is never auto-coupled to Epic/Story/Action entry — the flow only **accumulates** retrospectives. Reflection = a separate, human-triggered `retro-processing` run with a review gate (whoever triggers + reviews is the owner; no role identification).
- **M3 accumulate/preserve**: at archive time, retrospectives are extracted and consolidated to `archives/retro-{unit-name}.md` (flat, one per unit, no folders) = the **unreflected queue** for independent reflection. After reflecting into main, delete that `retro-*.md` (empty the queue — retro-processing step ⑦). Not an automatic asset update — see `flow-archive`.
- **M4 measurement**: evolution metrics (Try→asset reflection rate / same-mistake repeat frequency / updates per reflection / essential consistency) are measured at retro-processing time (`flow-retrospective` Part 3-5).
- **M5 ownership routing** for a Try's update target:

| Target | Route |
|---|---|
| Plugin core (skills/rules/hooks) | upstream proposal only (installed artifacts are never modified directly) |
| dogfood (the plugin's own repo) | direct update |
| playbook / memory | project-owned (project `.flow/playbooks/` override / project memory — Φ1 delegation) |

## MUST NOT

- Letting retrospectives evaporate / auto-coupling reflection to flow entry (bypassing human control)
- Omitting the 5-way Try classification
- Duplicating the procedure body into this rule

## Enforcement

- **TaskCompleted hook**: no retrospective written → completion blocked (guarantees accumulation)
- **retro-processing Hard Gate**: no reflection without review (no automatic reflection)
- **Bypass**: only an explicit user expression (per `gate-enforcement-default-on`) — never by the AI's own judgment

> ⚠️ **M2 boundary**: "carrying every improvement from the immediately preceding task forward into the current task" is personal work completeness — owned by the `flow-procedure-action` exhaustive (carry-forward) sweep, not retrospective reflection.

## Related SSOT

`flow-retrospective` Part 3 (procedure) · `playbooks/retro-processing.md` (independent-reflection work type) · `flow-archive` (archive-time extraction = reflection input) · `flow-procedure-action` sweep (M2 boundary) · `gate-enforcement-default-on` (meta rule)
