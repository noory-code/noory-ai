---
name: research
description: research work type — source collection → cross-verification → structuring → indexing/handoff. Collection and verification are the core gate (unlike docs, the point is "verify" not "write")
---

# research

A work type for producing a trustworthy answer to a question or topic. **The core is not writing but collection and verification** — gather sources, cross-verify with two or more sources, structure the findings, then index and hand off so that follow-ups can use them.

## When to apply

- Investigations where the answer is undecided, so external/internal sources must be gathered to reach a grounded conclusion
- Work where fact-checking governs the reliability of the result (technology comparison / prior art / root-cause tracing / market or regulatory confirmation)
- Not a fit:
  - The conclusion/material is already settled and **writing it up** is the point → `docs` (research gates on collection/cross-verification; docs gates on writing/structure)
  - Improving structure while preserving existing behavior → `refactor` / fixing a defect → `bug` / a new feature with defined I/O → `feature`

> Boundary with docs: if the step of **gathering and verifying** sources is missing, it is docs. The research deliverable is "verified facts + source mapping"; the docs deliverable is "a readable document." Formalizing research results into a document is a follow-up that is handed to `docs`.

## Procedure

1. **Define the question** — narrow the research question into an answerable form (scope / judgment criteria / non-goals stated) / deliverable: question spec (research question + success criteria)
2. **Collect sources** — broadly gather candidate sources per question, recording source metadata (author, time, type) / deliverable: source list (each source identifier + metadata)
3. **Cross-verify** — check each core claim against **≥2 independent sources**, flag/hold discrepancies / deliverable: claim↔source mapping table (≥2 supporting sources per claim, or marked "unverified")
4. **Structure** — organize verified claims by topic/hierarchy, label confidence (verified/partial/unverified) / deliverable: structured notes (claim + confidence + source reference)
5. **Index and hand off** — build an index (question→claim→source) and organize open items so follow-ups can reuse them / deliverable: index + open/follow-up list

> How sources are accessed (search, browsing, internal-material queries) and the domain-specific reliability judgment criteria are delegated to the research procedure that the **project supplies** (project `.claude/agents/`). This playbook defines only the general research flow.
>
> **Branch (when sources are scarce)**: if a core claim has only one independent source and ≥2 cannot be secured, do not assert the conclusion — explicitly mark it "unverified/single source" at ③ and hand it off to the ⑤ open-items list (do not disguise a guess as verification).

## AC format

Each research item (a question or core claim) is written with 5 fields.

- **Given** — premise (research question / collected source set)
- **When** — action (perform cross-verification / structuring)
- **Then** — expected result (a verified claim with a confidence label + source mapping)
- **Verification method** — check against the source-mapping table (confirm the number of independent sources per claim) or reviewer observation
- **Success/fail criteria** — core claim is backed by ≥2 independent sources / asserting it while single or unverified = FAIL

> No unmeasurable AC of the "looked it up roughly / seems about right" kind.

Example (domain-agnostic — fact-checking):

- **Given** — research question "when X was introduced" + collected source list
- **When** — extract the timing claim from the candidate sources and compare
- **Then** — a timing on which ≥2 independent sources agree = confirmed as a verified claim
- **Verification method** — count the independent sources for that claim in the claim↔source mapping table
- **Success/fail criteria** — ≥2 independent sources agree → PASS / one source, or sources disagree yet it is asserted → FAIL (marking it held/unverified is allowed)

## Hard Gate

> **HARD GATE**: No single-source assertion — do not finalize a conclusion without cross-verification by ≥2 independent sources
> When unmet: block promoting the claim to "verified" at procedure ④ (structuring) — mark it "unverified/single source" and send it to the ⑤ open-items list
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip it)

> **HARD GATE**: No handing off a claim without a source
> When unmet: block procedure ⑤ (handoff) — every verified claim in the index must carry a source reference
> Bypass: only on the user's explicit expression

## Feedback loop location

The "verify → feedback → fix → re-verify" loop of this playbook:

1. **Procedure ③ (cross-verification)** — the core loop. Compare sources (verify) → find discrepancy/shortfall (feedback) → gather more sources (return to ②) → re-compare. Repeat until every core claim has ≥2 sources or is explicitly held
2. **Procedure ④ (structuring)** — an auxiliary loop that returns to ③ to re-verify when a logical gap/contradiction is found during structuring
3. **Procedure ⑤ (handoff review)** — reviewer/user feedback → complete open items → re-hand off

> The loops above are verification loops **within the work flow**. Improving the playbook itself ("is this research flow correct") is the responsibility of retrospective-based evolution (`retro-processing` work type) — outside the scope of this playbook.

## Review/evaluation points

- **Review**: procedure ③ (review cross-verification results — check source independence/reliability) + procedure ⑤ (handoff review — check the index/open-items list). Prioritize single-source bias / source reliability / unverified assertions. Delegate when the project supplies a review teammate. **RT enabled default-on** (intensity/independence = README §7 + RT intensity matrix). RT essence attacks: single-source bias, source reliability, unverified assertion.
- **Evaluation**: the procedure ③ claim↔source mapping table = the deliverable evaluation criterion. Every core claim backed by ≥2 independent sources, or explicitly labeled "unverified" = satisfied.
- `flow-procedure-story` §7-2 review/evaluation Hard Gate forces execution of the points above.

## Violation handling

- Single-source assertion / handing off a claim without a source / disguising unverified as verified = block or request completion
- Bypass allowed only on the user's explicit expression (skip / move on / bypass / skip it)
- The fact of a bypass = mandatory record in the retrospective Problem section
