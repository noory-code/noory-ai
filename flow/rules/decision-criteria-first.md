# Four-way triage before asking (Decision Criteria First)

A gate that, before the AI asks the user for a decision, **triages what is blocked into four categories**. Work-type / language / framework agnostic. Enforced by default (`gate-enforcement-default-on`) — bypass only on explicit user expression (skip / move on / bypass / skip it).

## Gate (right before every question — whether the `AskUserQuestion` tool or a text "shall I ...?")

**(0) Decision attribution first**: reversible details with the same outcome ("how" — execution order, commit timing, file splitting, where to codify) are **decided by the AI (don't ask)**. The user's share is only outcome-affecting matters ("what" — direction, criteria, correctness, irreversible). Only then drop into the four-way triage below.

| Triage | Signal | Response |
|---|---|---|
| **(d) Insufficient data** | No basis for the judgment (code/doc/state) | **Self-collect first** — obtain it, don't ask. Ask only when impossible |
| **(c) Ambiguous application** | Criteria exist but their application to the current situation is unclear | Try to derive from the ultimate purpose → if derivable, report in one line "Y because X" and proceed (`purpose-anchoring`) |
| **(b) Criteria conflict** | Multiple criteria collide | State the conflict point + request a priority |
| **(a) No criteria** | No judgment criteria at all | Ask for criteria (4-element question below) |

> Order (d)→(c)→(b)→(a): self-collect data first, derive from purpose, and only if it still fails, ask. **In most cases the question disappears at (d)(c).**

❌ **Forbidden**: "pick between plan A and plan B" without the four-way triage (offloading the decision burden, whether by tool or text) / presenting options up front, a context-free menu, or forcing a single plan. If presenting options is unavoidable, self-consult at least 1 alternative first (`debate-redteam`).

## (d) Self-collection sources

Code/files → Read/Grep/Glob · state/history → git & investigation tools · purpose/criteria → task SSOT (`_initiative`/`_epic`/`_story`/`A-NNN.md`). Ask "tell me X" only when self-gathering is impossible (external info, context/preferences only the user knows).

## (c) Purpose derivation

Procedure = the `purpose-anchoring` 3-step gate. If derived, proceed after the 1-line report — no question. An interpretation check ("I read it this way — correct?") also counts as (c), not option-forcing.

## (b)(a) Question form — 4 elements

1. Context/background — work intent + current situation (1–3 lines)
2. Why a user decision is needed (1 line)
3. Ask for a criterion ((a)) or conflict priority ((b))
4. 2–3 examples to aid understanding — don't force choices; allow "or a different criterion"

Use the `AskUserQuestion` tool only when ① the decision is inherently the user's ② choices are concrete and mutually exclusive (2–4) ③ the criterion is already clear — otherwise prefer the 4-element text question. (Prevents option-menu offloading when stuck; not a ban on questions at a formal Alignment gate.)

## When it applies · boundaries

- Applies: Alignment/Assumption Gate questions in any Planning Phase · decision branches during Action execution · the urge to ask during retrospective/issue handling.
- `no-node-without-purpose` (hook Rule 9) injects purpose at design time — a precondition of this gate.
- `no-auto-proceed` boundary: this rule removes unnecessary questions; plan approval and big-decision checkpoints are kept.
