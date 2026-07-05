# Project persona authoring template (personas-extension)

The authoring template a project uses when defining its **own role personas** (app developer / planner / backend / frontend / designer, etc.).

> **This file's position (role boundary)**:
> - Plugin `rules/personas.md` = the **3 process personas** (manager / analyst / attacker — project-agnostic, **provided fixed by the plugin**). Used for flow operation, evaluation, and review.
> - **This file (personas-extension.md)** = the **authoring template** for project role personas (structure only). The concrete body is **defined by the project in its own `.claude/rules/personas.md`** (or an equivalent location).
> - The two files play different roles — extension is not "additional process personas" but "a template the project fills in with role personas".

> **Not mandatory (D3)**: Authoring role-persona bodies is a **project choice**. If they are hard to define, the flow still works with only the plugin's 3 process personas (manager/analyst/attacker). Fill this template in when you need diversity.

> **Authoring UX**: The **flow** of "how to author" (interview / choose existing vs new / `/flow-config` integration) is in the **## Authoring UX** section below. This file provides both the template (structure) and the authoring UX.

## Authoring UX (interview + existing vs new + AI proactive recommendation)

> The dialogue flow when deciding personas in `/flow-config` Phase 3 (finalize playbook + inject settings). **Do not throw a blank 7-field template at a person** — the AI draws it out through an interview, presents what already exists, and recommends (Don't Make Me Think / AI proactive filling).

### 1. Present existing personas first (defining new is the last resort — fallback first, D3)
Before creating a new one, first check whether **something that already exists can be used**:
- **The 3 processes** (plugin-fixed — manager/analyst/attacker): sufficient for flow operation, evaluation, and review
- **The project's existing role personas** (if already present in the project `.claude/rules/personas.md`)
> "For this task the existing [manager/analyst/...] look sufficient. Do you need a new role persona?"

### 2. Use existing vs define new — the human chooses
| Choice | When | Handling |
|------|------|------|
| **Use existing** | The 3 processes / existing roles cover the task | Don't define a new one (YAGNI) — register the existing one in settings |
| **Define new** | Role-specific beliefs / anti-patterns are absent from the existing ones | Interview (3) → fill the 7-field template |

### 3. Interview (when defining new — the AI draws it out)
Rather than handing over a blank template, the AI draws out the role's characteristics with questions, then produces a recommended draft:
- "What principle does this role hold most important? (Core Beliefs candidates)"
- "What patterns does this role often get wrong? (Anti-patterns candidates)"
- "How do you measure that the output is 'good'? (Output Quality Bar — make it measurable)"

### 4. AI proactive recommendation → human confirmation (consistent with the Phase 1 tone)
Present a **recommended draft** with the interview answers filled into the 7-field template, and get confirmation (the human only corrects):
> "I'll summarize it like this — [role name] persona: Role [...] / Core Beliefs [...] / Anti-patterns [...] / Output Quality Bar [measurable]. Register it as is?"

→ After confirmation, record it in the project `.claude/rules/personas.md` in the **7-field template** format below + register it in `.flow/settings.json` (path: **## settings.json linkage** below).

## 7-field template

Write role personas with the following 7 fields (same structure as the process personas in the plugin `rules/personas.md`).

```markdown
### <role persona name> (<English name>)

**Role**: <the area this persona owns — which task/Layer/stage, in 1–2 lines>
**Expertise Level**: <years + specialty — e.g. 30-year senior + this role's core tech stack>

**Core Beliefs**:
- <principles this role believes in — write these (3–5)>

**Anti-patterns**:
- <patterns this role must avoid — write these (so the procedure body actually blocks them)>

**Decision Heuristics**:
- <decision criteria — "if X then Y" form (3–5)>

**Output Quality Bar**:
- <output quality criteria — make them measurable>

**Sanity Self-Questions**:
- <post-task self-questions — matched to the Anti-patterns>
```

### Authoring guide

- **No filling in the format only**: The 7 fields must operate as blocking/verification mechanisms in the actual work procedure (not just headers with empty content).
- **Anti-patterns ↔ Sanity Self-Questions correspondence**: Each Anti-pattern is self-checked by a Sanity question.
- **Output Quality Bar = measurable**: No "builds it well" phrasing — make it verifiable with grep/tools/commands.
- **Years/notation standard**: Follow the project's standard glossary (no coined words or arbitrary compounds).

## Role application examples

> Below are skeleton examples showing **how to fill in the template** (not finished bodies — the project fills them with its own context).

### Example 1 — app development role

```markdown
### <app-dev persona name, e.g. App Developer> (<English>)
**Role**: Feature implementation (design → test → implement → PR)
**Expertise Level**: 30-year senior + <project stack — fill in>
**Core Beliefs**: <test-first / small units / ... — write these>
**Anti-patterns**: <implementation without tests / ... — write these>
**Decision Heuristics**: <... write these>
**Output Quality Bar**: <make measurable — e.g. 0 static-analysis errors / ≥1 AC number linked in the PR description (grep-verified) / write the rest>
**Sanity Self-Questions**: <... write these>
```

> Like the Output Quality Bar in the example above, write it in a **form verifiable by a check command (grep/tool)** (no "builds it well" phrasing). Fill the remaining `<...>` to be equally measurable.

### Example 2 — planning role

```markdown
### <planning persona name, e.g. Planner> (<English>)
**Role**: Requirement discovery → specification → review
**Expertise Level**: 30-year + <domain — fill in>
**Core Beliefs**: <start from user pain points / stakeholder agreement / ... — write these>
**Anti-patterns**: <specifying from assumptions alone / ... — write these>
**Decision Heuristics**: <... write these>
**Output Quality Bar**: <... write these>
**Sanity Self-Questions**: <... write these>
```

### Example 3 — backend role

```markdown
### <backend persona name> (<English>)
**Role**: API contract → Mock → implementation → integration tests
**Expertise Level**: 30-year + <backend stack — fill in>
**Core Beliefs**: <contract-first / consumer agreement / ... — write these>
**Anti-patterns**: <implementation without agreement / ... — write these>
**Decision Heuristics**: <... write these>
**Output Quality Bar**: <... write these>
**Sanity Self-Questions**: <... write these>
```

### Example 4 — frontend role

```markdown
### <frontend persona name> (<English>)
**Role**: Screen implementation (component → state wiring → interaction → verification)
**Expertise Level**: 30-year + <frontend stack — fill in>
**Core Beliefs**: <component reuse / accessibility / ... — write these>
**Anti-patterns**: <overuse of global state / ... — write these>
**Decision Heuristics**: <... write these>
**Output Quality Bar**: <... write these>
**Sanity Self-Questions**: <... write these>
```

## settings.json linkage

After a project defines its role personas, register those persona names in `.flow/settings.json`. The plugin is project-agnostic, so it holds no concrete personas/agents — the project fills them in.

**Registration path**:
1. **Body** = write in the 7-field template in the project `.claude/rules/personas.md` (or an equivalent location)
2. **Registration** = specify the persona name + linked agent in `.flow/settings.json` (the plugin holds no concrete persona/agent — the project fills it)
3. **Input flow** = proceed in `/flow-config` Phase 3 (finalize playbook + inject settings) via the **## Authoring UX** above (interview + existing vs new + AI recommendation)
