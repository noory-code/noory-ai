# Ground-Truth Inspection First — No Asserting Before Verifying (Verify Before Assert)

A gate that prevents **asserting something about a mechanism·spec·external state without checking it, and then building on top of that**. Independent of work type·language·framework. A rule the plugin owns itself (does not depend on the user's personal guidance). Enforced by default (`gate-enforcement-default-on`) — bypass only on the user's explicit say-so.

## Essence

The most expensive failure = asserting "it won't work / it will work" without checking, stacking work on that assumption, and then having the user correct it and roll it back. Cutting in once before asserting — "did I actually verify this, or am I guessing?" — eliminates most rework. A flow enforcement signal of honesty (no guessing / answer after verifying).

## Gate: 3 steps before asserting·concluding (mandatory)

Right before outputting an assertion of the "X works / doesn't work / is already so / behaves this way" kind about a mechanism·spec·external state, or building on top of it:

1. **Distinguish the source** — ① internal asset (code·SKILL.md·hook decision logic·settings schema·plugin spec) ② external asset (CI/CD·marketplace·external system·cache freshness·other repos·external policy).
2. **Attempt ground-truth inspection** — verify per the table below. Internal = `Read`/`Grep` directly; external = interview the user or query a tool. For a **negative result** (0 hits / not found / not merged), first suspect the tool·path·scope·remote freshness — a wrong-path grep gives a false 0-hit, a stale local gives a false not-merged (`git fetch` / re-check the path first).
3. **Assert after verifying** — assert only from ground-truth results. If inspection is impossible (external·user-only context), state "unverified — presumed" or ask the user.

## Ground-truth inspection paths (per source)

| Source | Inspect via | ❌ Forbidden |
|---|---|---|
| Internal code/spec (hook logic / SKILL.md / config schema / plugin capability) | `Read`/`Grep` the file directly | "Probably works like this" guess |
| External system/asset (CI/CD / marketplace / external API·policy) | User interview, or query current state (`list`/status) | Guessing from a summary as if internal |
| User's weak phrasing ("seems", "existing", "probably") | Treat as hypothesis; if impact is large, confirm intent after impact analysis | Bulk changes off weak phrasing as if confirmed |
| External contract change (serialization enum / API code value) | Secure the contract SSOT (spec/ticket/response example) + keep/add/remove policy first | Implementing arbitrary enum/code values before the spec |
| Guard/default/invariant change (`can*`/`is*`/state transitions) | Exhaustive `Grep` of the symbol + inspect code depending on the old guard/default | Changing one guard without checking its dependents |
| External state change (marketplace add / install / env change) | Query current state first → report conflict impact, then act | Change without query → post-hoc conflict |
| Cache/reflection freshness (after upgrade/redeploy) | Inspect the source diff (same-version update can be a no-op) | "I upgraded so it's reflected" |
| Internal behavior details (hook fire conditions · regex match region · file/dir IO deps) | `Read`/`Grep` before writing: fire condition, one concrete match example (header included?), behavior when the file/dir is absent | Assuming behavior → fixture failure·runtime error |
| Negative search/query result (0 hits / not-merged / "not found") | Re-check tool·path·scope first; git: `git fetch` before judging | Asserting the negative as fact |
| Pipe/chain exit code (`cmd \| tail`, `A && B`) | Run the target command standalone and read its own result (pipefail not assumed) | Trusting pipe/chain exit 0 as "pass" (earlier failure masked) |
| Agent/subtask assertion ("all X" / "N items" / "none") | High-impact: cross-verify ≥1 item yourself (`Read`/`Grep`) before adopting | Blind adoption → work built on a falsehood |
| Disablement/removal scope (turning off a feature / removing code·requests) | `Grep` the whole call path — definition·usages·request generation — then pick branch-off vs full removal | Turning off one branch while requests still fire |
| Structural change / DIP-violation measurement | Authority = exhaustive identifier `Grep` + `find test/features` + whole-project analyze | Single-pattern grep asserting impact scale / 0 violations |
| Dead/unused judgment | Language-analyzer diagnosis required (`unused_import`, etc.) | Asserting unused from reading alone (barrel import misread as 0-ref) |
| PoC/verification design | Verify "can this be checked in this environment" before assuming so | Designing the check on an unverified environment assumption |

## Violation / application cases (condensed)

- ❌ Assumed a settings-application mechanism / summarized an external CI flow by guess / skipped `list` before a marketplace add / mistook a same-version cache no-op for "not reflected".
- ❌ Wrong-path grep → false "0 hits" (cases existed); stale local main → false "not merged"; acted before the user's explicit confirmation. Common pattern: asserting a negative·remote state before inspection.
- ✅ "I'll `Read` plugin.json first, then answer" / "This CI flow is external — tell me the current behavior and I'll organize it" / "0 hits, but let me re-check the path" → corrected directory, re-ran.

## Boundary with other rules

- `decision-criteria-first` (d) — (d) = self-collect data before asking; this rule = ground-truth inspection before asserting. Internal = self-collect (`Read`/`Grep`), external = interview. Both: never skip with a guess.
- `purpose-anchoring` — derive the purpose before asking (mutually complementary).
- `gate-enforcement-default-on` — the meta-rule enforcing this gate by default.
