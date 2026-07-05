---
name: meta-skill-writing
description: "Skill-writing guide. Reference for SKILL.md frontmatter / Progressive Disclosure / Step format / Verification standards."
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Skill-writing guide

Notes for writing a SKILL.md. Based on the [Agent Skills open standard](https://agentskills.io/specification).

## Persona — no standalone block at the top of a skill

Do **not** put a `## Persona` block (a copy-paste of the 7 fields Role/Expertise/Core Beliefs/Anti-patterns/Decision Heuristics/Output Quality Bar/Sanity) in the SKILL.md body. The body's procedure/AC/verification already carry the guidance, so it is redundant (with/without behavior unchanged by ground-truth inspection — Epic inert-content-cleanup). Reference the persona only as a *function*: R-mechanism input (`debate-redteam`) / Story "As a" (`_story.md`) / teammate definition (`meta-agent-procedure`). SSOT: `rules/personas.md`.

## Frontmatter (mandatory)

```yaml
---
name: my-skill
description: |
  What it does + when to use it.
  Use in the following situations: (1) condition A, (2) condition B.
metadata:
  type: reference  # or procedure (project-specific field)
  version: v1.0.0  # project-specific field
---
```

### Mandatory fields

| Field | Rule | Standard |
|------|------|------|
| `name` | lowercase + hyphen, within 64 chars, same as the folder name | agentskills.io mandatory |
| `description` | 1–1024 chars, includes trigger conditions | agentskills.io mandatory |

### Project-specific fields

| Field | Rule | Note |
|------|------|------|
| `metadata.type` | `reference` or `procedure` | skill type classification |
| `metadata.version` | `v1.0.0` format | version tracking |

### Optional fields (agentskills.io standard)

| Field | Use | Example |
|------|------|------|
| `license` | state the license | `Apache-2.0` |
| `compatibility` | environment requirements (within 500 chars) | `Requires <runtime>` |
| `allowed-tools` | pre-approved tools (experimental) | `Bash(git:*) Read` |

> Most internal skills do not need optional fields. Adding `license` is recommended only for external distribution.

## Progressive Disclosure

A skill loads progressively in 3 stages. Write it considering each stage's token budget.

| Stage | Load timing | Content | Token budget |
|------|----------|------|----------|
| 1. Metadata | at agent start (always) | `name` + `description` | ~100 tokens |
| 2. Instructions | on skill activation | the whole SKILL.md body | < 5,000 tokens (within 500 lines) |
| 3. Resources | on-demand when needed | `scripts/`, `references/`, `assets/` | as much as needed |

**Core principles**:
- Keep the SKILL.md body **within 500 lines** (5,000 tokens or fewer recommended)
- Split detailed reference material into `references/` for on-demand loading
- The `description` is used by the AI for skill matching, so **trigger keywords are mandatory**

## Resolution-procedure Step format

```markdown
### Step N: {stage name}

**Task**: {what to do}
**Result**: {artifact}
**Related material**: {resource link} (optional)
**Branch**: {conditional flow} (optional)

**Checklist**:
- [ ] {detailed confirmation item}
```

**Step components**:

| Item | Mandatory/Optional | Description |
|------|----------|------|
| **Task** | mandatory | the work to perform in this stage |
| **Result** | mandatory | a verifiable artifact |
| **Checklist** | conditional | completion verification for complex Steps |
| **Related material** | optional | resource link |
| **Branch** | optional | conditional flow |

## Checklist structure

| Location | Use | Content |
|------|------|------|
| **Top level** | final verification of skill completion | only 3–5 core items |
| **Within a Step** | completion verification of that Step | per-Step detailed confirmation |

## Folder structure

| Folder | When | Example |
|------|------|------|
| scripts/ | repeatedly run scripts | `validate.py` |
| references/ | details over 200 lines | `state-design.md` |
| assets/ | templates/images/examples | `template.md` |

**Example files**: split into assets/ when over 100 lines

## Verification section (mandatory for procedure skills / optional for reference & gate-bearing skills)

> Applies to: procedure skills require a verification-command section. A reference skill, or a skill that carries its own Hard Gate or `grep`/`ls` gate in the body, has that gate serving the Verification role, so a separate `## Verification` header is optional (substantive verification over format).

> A high-impact (High) assertion reported by a subtask/agent (skill-reviewer, etc.) is cross-verified by main directly at least once before adoption — see the "agent/subtask assertion" row of `verify-before-assert` §ground-truth-inspection path.

```markdown
## Verification

- **Build verification**: 0 errors after running the lint command
- **Test**: the test command passes
```

**Checklist vs Verification**:
| Distinction | Checklist | Verification |
|------|-----------|--------------|
| Question | "Done?" (Yes/No) | "How to confirm?" (method) |
