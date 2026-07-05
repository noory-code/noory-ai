---
name: security
description: Security-hardening work type — threat modeling → mitigation design (as AC) → implementation → security check·verification → merge. No implementation without a threat model, no merge without passing the security check
---

# security

A work type that protects assets from threats or responds to vulnerabilities. **Model threats first**, specify a mitigation as an AC for each identified threat before implementing, and enforce the security check as a Hard Gate before merge.

## Applies to

- Security design of new features / hardening authentication·authorization·data protection
- Vulnerability report response / attack-surface reduction / permission-boundary re-review
- Not a fit: general feature development unrelated to security (→ `feature`) / behavior-preserving structural improvement (→ `refactor`) / fixing a general defect that is not a security flaw (→ `bug`)

## Procedure

1. **Identify assets·trust boundaries** — organize the protection targets (data·credentials·permissions) and trust boundaries / deliverable: asset·boundary list
2. **Threat modeling** — systematically derive threats per boundary and prioritize by impact·likelihood / deliverable: threat model (threat items + priorities)
3. **Mitigation design (as AC)** — for each prioritized threat, decide a mitigation and specify it as a verifiable AC / deliverable: threat↔mitigation AC list
4. **Mitigation implementation** — implement mitigations in the direction where the AC passes / deliverable: implementation code (per-threat mitigation mapping)
5. **Security check·verification** — verify mitigation ACs + run the security checks the project supplies (static analysis·dependency check·penetration check, etc.) / deliverable: security check report (pass/fail + residual risk)
6. **Merge** — a change set that passes the check + records residual risk / deliverable: merged change (check report attached)

> The concrete check tools·language-specific secure-coding rules·threat-classification taxonomy are delegated to the procedures the project supplies (project `.claude/agents/`). This playbook defines only the general security-hardening flow.
>
> **Branch (emergency vulnerability response)**: when urgently responding to a known vulnerability, lighten ①② to a "threat analysis of that single vulnerability" and perform ③~⑥ the same way. Even in an emergency, the mitigation AC·security check are not skipped.

## AC format

Write each mitigation with 5 fields.

- **Given** — precondition (threat scenario / attacker input / system state)
- **When** — action (attack attempt / boundary-crossing attempt / normal request)
- **Then** — expected result (block / reject / safe handling)
- **Verification method** — automated security test or check procedure (static analysis / boundary test / observation)
- **Success·failure criteria** — PASS if the threat is blocked / FAIL if bypass is possible (state residual risk)

> No unmeasurable AC of the "seems safe / looks fine" kind.

Example (domain-independent — permission-boundary threat→mitigation):

- **Given** — a state where an unauthorized subject attempts to access a protected resource
- **When** — the request to that resource is executed
- **Then** — the request is rejected (no resource exposure·modification)
- **Verification method** — automated security test (assert rejection for an unauthorized request)
- **Success·failure criteria** — PASS if rejected / FAIL if the resource is exposed·modified

## Hard Gate

> **HARD GATE**: no starting implementation without threat modeling
> If unmet: procedure ④ (mitigation implementation) is blocked — procedure ② (threat modeling) + ③ (mitigation AC) are required first
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip it)

> **HARD GATE**: no merge if the security check does not pass
> If unmet: procedure ⑥ (merge) is blocked — both the mitigation AC + the project security check must pass. Residual risk proceeds only after being recorded·accepted
> Bypass: only on the user's explicit expression (skip / move on / bypass / skip it)

## Feedback loop location

The "verify → feedback → fix → re-verify" loop of this playbook:

1. **Procedure ⑤ (security check·verification)** — the core loop. Run the mitigation AC·security check (verify) → analyze failures·residual risk (feedback) → fix the mitigation → re-check. Repeat until fully passing
2. **Procedure ② (threat modeling)** — an early feedback loop checking for missed threats relative to assets·boundaries
3. **Procedure ⑥ (merge)** — reviewer security feedback → fix → re-review

> The loops above are verification loops **within the work flow**. Improving the playbook itself ("is this flow correct") is the responsibility of retrospective-based evolution (`retro-processing` work type) — outside the scope of this playbook.

## Review·evaluation points

- **Review**: procedure ② (threat-model review — missed threats·priorities) + procedure ⑥ (pre-merge security review). Prioritize trust-boundary consistency / mitigation adequacy / whether residual risk is accepted. Delegate when the project supplies a security-review teammate. **RT is default-on** (intensity·independence = README §7 + RT intensity matrix). RT essence attacks: missed threats·trust-boundary consistency·residual risk.
- **Evaluation**: procedure ③ mitigation AC (Given/When/Then) satisfaction = the deliverable evaluation criterion. All mitigation ACs + the security check passing = satisfied.
- The `flow-procedure-story` §7-2 review·evaluation Hard Gate enforces execution of the above points.

## Violation handling

- Implementation without a threat model / merge without passing the security check / unrecorded residual risk = block or request remediation
- Bypass is allowed only on the user's explicit expression (skip / move on / bypass / skip it)
- The fact of the bypass + the accepted residual risk = mandatory recording in the retrospective Problem section
