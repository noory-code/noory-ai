# SSOT Standard-Term Glossary + Compound-Word Block Rule

**The standard-term SSOT that every SKILL.md / Rule / Prompt / Subagent / work-item SSOT (`_epic.md`/`_story.md`/`A-NNN.md`) follows.** Enforced by default (`gate-enforcement-default-on`) — bypass only on explicit user phrasing (skip / move on / bypass / skip over).

## Gate (when authoring/verifying an SSOT · skill · rule · prompt)

1. **Cite standard terms**: persona / Phase / flow-unit notation must follow the glossary below — no arbitrary variation.
2. **Block arbitrary compounds**: no role names beyond the personas, no meaningless nominalizations, no abbreviations without the full form on first use.
3. **Single-source identifiers & counts**: one identifier = one SSOT definition, no copies (cross-ref only); "N kinds/items/axes" labels stay in sync with the actual item count.
4. **Measurable AC**: AC/verification carry a measurable command (grep/ls/find/test) — no "works fine / looks OK".
5. **On violation**: simple (role name · nominalization · abbreviation) = AI self-corrects + records `[self-correction notice] location/violation/correction/origin` in the retrospective Problem; ambiguous coined term = flag it + presumed meaning + correction candidates → user decides. No bypass on the AI's own judgment — explicit user phrasing only.

## Standard-term glossary

**Personas**: the 3 planner process personas (Manager/Attacker/Analyst) — SSOT = plugin `rules/personas.md`; role personas — SSOT = the project persona rule. Default persona for flow meta/SSOT work = **Manager (Flow Manager)**.

### Phase notation
| Standard | Banned | Meaning |
|---|---|---|
| **Planning** | Plan / "planning stage" alone | Discovery → Alignment → Draft → AI Review → Finalize |
| **Setup** | Init / initialization | branch + file creation |
| **Execute** | Implement / Run | execution |
| **Finish** | Wrap-up / Close | verify + retrospective + commit + merge |

### Flow units
| Standard | Banned | Meaning |
|---|---|---|
| **Epic** | Project | 5+ days / bundle of Stories |
| **Story** | Feature (as a Story) | 1–3 days / bundle of Actions; 2 types — US/TS |
| **User Story (US-NNN)** | — | user-value Story: user persona ("As a [persona]") + user-value AC |
| **Technical Story (TS-NNN)** | scattering into Actions / forcing into a US | technical/infra/refactor/tech-debt/build/CI Story; **user persona exempt** — process persona (Manager/Analyst) + technical AC (grep/test/build) |
| **Action** | Task / Subtask / Step | a single verifiable unit of work |

US and TS are peer Stories and may coexist in one Epic; the only difference is persona/AC.

## Compound-word block (no coining without an explicit user definition)
- Role names outside the personas ("...writer/evaluator/operator") → one standard persona (meta work: usually Manager).
- Nominalized compounds with unclear meaning → a clear, full name.
- First-use abbreviations without the full form → "DIP (Dependency Inversion Principle)".

## Identifier/count SSOT unification (drift block)
| Target | ❌ Banned | ✅ Correction |
|---|---|---|
| same identifier (role name / schema field / playbook name) | body definition copied in 2+ places | 1 SSOT definition; elsewhere "summary + SSOT reference" |
| count label ("N kinds/items/axes") | pinned, not updated when items change | on row add/remove, sync label = actual count |

Verify: counts — `grep -rEn "[0-9]+ (kinds?|items?|axes)" <target>` vs actual; identifiers — `grep -rn "<identifier>"` → non-SSOT hits must be references, not copies.

## Pruning (retro-processing step ⑥)
| Dead-letter type | Definition | Verification |
|---|---|---|
| Duplicate definition | same identifier/rule defined in body 2+ places | `grep -rn "<identifier>"` → copies outside SSOT |
| Dead-letter origin | origin citation already absorbed elsewhere but left at length | check whether the cited retrospective is absorbed |
| Synonym variant | same meaning restated in different wording | ≥2 identical-meaning expressions |
| Dead cross-ref | pointed-to SSOT gone / meaning changed | cross-ref grep + verify the target |

## grep precision (false positives / omissions)
| Pitfall | ❌ Weak | ✅ Precise |
|---|---|---|
| existing-asset false positive | `grep '<keyword>' <file>` | limit to diff: `git diff \| grep '^+.*<keyword>'` |
| missing generality | framework names only | also role tools (Postman/Figma), job titles (planner/designer), implementation tech (REST/gRPC) |
| verification self-false-positive | tool names inline in the Verification body | generalized phrasing, no proper nouns |
