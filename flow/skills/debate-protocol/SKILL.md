---
name: debate-protocol
description: |
  Debate protocol. A 3-phase structured debate procedure for design/structure improvement.
  Use in the following situations: (1) design/structure improvement debate, (2) architecture decision validation,
  (3) pre-validation of structural changes. Separates discovery from validation and guarantees RT attack strength.
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Debate Protocol

A 3-phase structured debate procedure used for design/structure improvement.

## Agent Teams mapping

This protocol's artifact/approval flow corresponds to the Agent Teams collaboration features as follows (confirmed design G — feedback loop):

| This protocol's element | Agent Teams mapping |
|-----------------|------------------|
| Phase A/B/C artifact recorded to SSOT immediately | shared task list |
| Phase B user approval (proposal confirmation) | plan approval |
| Splitting RT into a separate reviewing teammate | mailbox collaboration (RT teammate ↔ proposer teammate) |

> Whether to run RT in the same session as a one-person-two-roles act (Method Acting) or to split it into a separate teammate is chosen based on the work scale and environment. Either way, the RT attack-strength guarantee (`debate-redteam`) applies identically.

---

## 3-phase structure

```
Phase A: Discovery      — find problems and note solution ideas
Phase B: Proposal       — confirm the integrated solution
Phase C: Validation     — improve via Method Acting (or a separate teammate), alternating RT/defense roles
```

---

## Phase A: Discovery

**Purpose**: find every possible problem.
**Exit condition**: end when there are 3 consecutive rounds with no new problems, or when the user says "that's enough".
**No round limit.**

### Rules
- **Focus on discovery**: concentrate on "what is the problem".
- Solution ideas that naturally come to mind when a problem is found may be recorded in the **notes column** (full discussion happens in Phase B).
- Assign a P{N} number to each problem.
- **Evidence** (file, line, logic) is mandatory for each problem.
- **Severity** classification: 🔴 Bug (wrong behavior) / 🟡 Gap (missing) / 🟢 Smell (improvable)

### Artifact format

```markdown
## Phase A: discovery list

| # | Severity | Problem | Evidence | Impact | Solution idea (note) |
|---|:------:|------|------|------|-------------------|
| P1 | 🔴 | ... | ... | ... | ... |
| P2 | 🟡 | ... | ... | ... | (none) |
```

---

## Phase B: Proposal (deriving the improvement)

**Purpose**: **derive an integrated improvement through debate** for the discovered problems. Do not confirm a single candidate without criticism.

**Structure**: B.1 Draft (derive candidates) → B.2 Debate (compare candidates) → B.3 Synthesis (confirm the integrated proposal)

> **Phase B vs Phase C role separation**:
> - **Phase B debate**: "which of several candidates is better" — **horizontal comparison** (trade-offs between alternatives)
> - **Phase C debate**: "does the confirmed proposal have gaps/weaknesses" — **vertical strength** (RT attack/defense on a single proposal)

### Handling bulk problems (prerequisite)

If P{N} exceeds 20, group before entering B.1:
1. **Grouping**: bundle by severity (🔴→🟡→🟢) or by category (domain).
2. **Group-level Story/Action mapping**: the group (category), not the individual P{N}, corresponds to an execution unit.
3. **Out-of-scope declaration**: classify problems not addressed in the current Epic as "00-common" or "next Epic".

---

### B.1: Draft (derive candidates)

**Purpose**: **derive multiple improvement candidates** for each category (or discovery group).

**Rules**:
- 1–3 candidates per category (a single obvious proposal may be 1 — but it must pass the B.2 self-review)
- Each candidate is a specifiable unit (execution unit/file/order)
- **No self-censorship** — raise it as a candidate first, then debate in B.2
- Candidate ID: `{category}-{letter}` (e.g. `C1-A`, `C1-B`)

**Artifact format**:
```markdown
#### B.1 candidate derivation

| Category | Candidate ID | Proposal summary | Key trade-off |
|---------|---------|--------|-----------------|
| C1 | C1-A | ... | ... |
| C1 | C1-B | ... | ... |
| C2 | C2-A | ... | (single candidate — self-review needed) |
```

---

### B.2: Debate (compare candidates)

**Purpose**: state the trade-offs between candidates and select the stronger proposal. **Horizontal comparison** debate.

**Rules**:
- Even if only 1 candidate was derived, do a **"why is there no other alternative"** self-review once (record the self-review result)
- Standard comparison axes: **effectiveness / cost / risk / consistency / extensibility / regression impact**
- End by consensus or user judgment
- **Select 1 proposal per category** (a mix is allowed — but state it)

**Artifact format**:
```markdown
#### B.2 candidate comparison debate

##### C1 debate
| Comparison axis | C1-A | C1-B | Winner |
|--------|------|------|------|
| Effectiveness | ... | ... | A |
| Cost | ... | ... | B |
| Risk | ... | ... | A |
| Consistency | ... | ... | A |
**Selection**: C1-A (or C1-A + C1-B mix: ...)
**Rationale**: ...
```

---

### B.3: Synthesis (confirm the integrated proposal)

**Purpose**: confirm the integrated improvement from the B.2 debate result + map execution units.

**Rules**:
- Include a resolution direction for every category/P{N} (out-of-scope declaration is allowed)
- **One coherent integrated proposal**. State trade-offs when categories conflict
- Map execution units (Action/file) — final decomposition after Phase C validation

**Artifact format**:
```markdown
#### B.3 integrated proposal

| Category | Selected proposal | Resolution direction | Execution unit | Note |
|---------|----------|----------|----------|------|
| C1 | C1-A | ... | A-001 | ... |
| C2 | C2-A | ... | A-002 | ... |

#### Design decision summary
1. [Decision 1]: selected proposal A in C1. Reason: superior in effectiveness/consistency in the B.2 comparison.
2. [Decision 2]: ...
```

---

### MUST NOT (Phase B)

- ❌ Derive only 1 B.1 candidate + skip the B.2 debate (even for a single candidate, "why is there no other alternative" self-review once is mandatory)
- ❌ Enter B.3 without a B.2 debate artifact
- ❌ Ignore some P{N}/categories in the B.3 integrated proposal (if out of scope, state "out of scope")
- ❌ Miss recording B.1/B.2/B.3 to SSOT before entering Phase C (→ plugin rules/)

---

## Phase C: Validation

**Purpose**: elevate the proposed improvement in a better direction.
**End**: over once the topics to discuss are exhausted.

### Execution mechanism — Method Acting (one person, two roles) or a separate teammate

Phase C proceeds by **alternating RT/defense roles**. Choose between the same session's one-person-two-roles act (Method Acting) or a separate reviewing teammate (mailbox collaboration).

**Role-switching principles:**
- On entering the RT role: **fully immerse** in the `debate-redteam` SKILL.md persona. Attack at maximum strength without considering whether it can be defended.
- On entering the defense role: defend **sincerely** as the proposer. Believe the RT's attack is wrong and build the argument.
- On switching roles, **consciously block** the previous role's thinking.
- The user monitors attack quality. "Weak" → orders "dig deeper".

### Round structure (depth-first per topic)

**1 topic = 1 round.** When that topic's debate ends, record it and move to the next topic.

```
Topic 1 → [RT] attack → [defense] rebuttal → [RT] counter-rebuttal → ... → conclusion → record
Topic 2 → [RT] attack → [defense] rebuttal → [RT] counter-rebuttal → ... → conclusion → record
...
Topics exhausted → Phase C ends
```

**Do not count the number of exchanges.** End when one side's arguments are completely exhausted or when both sides agree on a better alternative.

### RT/defense rules

> **Details**: see `debate-redteam` SKILL.md

Key points only:
- **No opposition for opposition's sake** — an attack is made "because there is a better way"
- **A rebuttal without an alternative is void** — pointing out a problem + presenting an alternative is mandatory
- **No compromise** — not a concession but the discovery of a better way
- **Every exchange's output is an improvement** — not win/lose
- **Attack priority**: validity (1) → responsibility (2) → consistency (3) → methodology (4)

### User questions

During debate, **ambiguous points may be asked of the user**.
- When SSOT confirmation is needed but there is no certainty
- When business intent/requirements are unclear
- When a trade-off between alternatives depends on subjective judgment

After asking, continue the debate once the user's answer is received. Do not fill ambiguity with guesses.

### Exit conditions

Per-topic debate ends **only when one of the following** occurs:

1. **Arguments exhausted**: one side's rebuttal arguments become completely 0 (accept what is 100% correct)
2. **Alternative agreement**: both sides agree on a new approach better than the original
3. **Better improvement found**: a supplement to the original proposal emerges during debate and both sides confirm it

**Prohibited**: ending based on the number of exchanges. "We did N rounds, so it's enough" is not an exit reason.

Consecutive "defense concedes" on a key attack (priority 1–2) → review regressing to Phase B.

---

## User role

- Phase A exit judgment: the user says "that's enough" or automatic (3 consecutive rounds with no discovery)
- Phase B approval: the user confirms the proposal, then enters Phase C
- Phase C: the user confirms each topic's conclusion. On non-agreement, the user judges.

---

## SSOT recording (mandatory)

Debate artifacts are **recorded to the SSOT file immediately on confirmation**. If they stay only in chat, they evaporate.

### Recording location

| Scale | Location |
|------|------|
| Default | the `## Debate record` section inside the work SSOT file (`_story`, etc.) of that Story directory |
| Large (P{N} > 15 or many rounds expected) | put a separate debate file (`_debate`, etc.) in the same directory and link it from the work SSOT file |

### Recording timing

| Phase | Timing | What to record |
|-------|------|-----------|
| Phase A | at each round's end (3 consecutive rounds with no new problem, or user "enough") | discovery list table (P1~P{N}) |
| Phase B | on integrated-proposal confirmation (user approval) | proposal table + design decision summary |
| Phase C | **right after each topic's conclusion** (per topic, not batched after the end) | that topic's round table + conclusion + agreement content |

### Progress rules

- No Phase's artifact ends in chat only.
- **Reflect the previous Phase's record to SSOT before entering the next Phase** (Hard Gate).
- Update the file immediately when an artifact is updated (e.g. reinforce the table when Phase A adds a discovery round).
- When a discovery/proposal/agreement is judged void, do not delete it from the table — mark it with **strikethrough + reason** (preserve history).

### MUST NOT

- ❌ Miss the SSOT record after a Phase ends → plugin rules/
- ❌ Report Phase B/C results in chat only and not reflect them in the work SSOT file
- ❌ Write the previous Phase's record retroactively after entering the next Phase (evaporation risk)

---

## Debate record format

```markdown
## Debate record

### Phase A: Discovery
| # | Severity | Problem | Evidence | Impact | Solution idea (note) |
|---|:------:|------|------|------|-------------------|
| P1 | ... | ... | ... | ... | ... |

### Phase B: Proposal
| P# | Resolution direction | Execution unit |
|----|----------|----------|
| P1 | ... | Story N |

### Phase C: Validation (per-topic record)

#### Topic 1 — [1-line summary]
| Exchange | RT | Defense |
|:----:|------|------|
| 1 | [attack summary] | [rebuttal summary] |
| 2 | [counter-rebuttal summary] | [counter-counter-rebuttal summary] |
| 3 | [ruling] | [confirmation] |
**Conclusion**: [alternative agreement / original reinforced / RT concedes / defense concedes / user judgment]
**Agreement content**: ...

#### Topic 2 — [1-line summary]
...

### Final conclusion
(confirmed improvement + overall agreement reflected)
```

---

## Verification

- [ ] Did Phase A focus on discovery? (solution ideas only in the notes column)
- [ ] Does the Phase B proposal cover every P{N}?
- [ ] Did Phase C reference `debate-redteam` and perform the RT role?
- [ ] Did each topic end via an **exit condition (arguments exhausted / alternative agreement / improvement found)**? (no ending based on exchange count — consistent with the body's exit conditions)
- [ ] Did the RT not concede easily? (check attack power on 2 consecutive concessions)
- [ ] Was an alternative derived **without compromise**?
- [ ] Did you consider **not only text but also Hook/structural mechanisms** as improvement means?
- [ ] Did both sides present an **improvement direction rather than defending the existing system**?
