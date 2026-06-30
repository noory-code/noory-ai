---
name: plot-i18n-audit
description: Static audit of viewer i18n compliance per feedback_plot_global_service (Novel is a global service). Scans viewer/src/**/*.{ts,tsx} for hardcoded user-facing strings, undefined t() keys, stale locale keys, and untranslated values. Triggers on i18n / 다국어 / 국제화 / "translation audit" / "locale check" / "i18n 검사" plus a Novel context.
metadata:
  version: "1.0.0"
  category: review
  type: unit
  style: procedure
  triggers: [i18n, 다국어, 국제화, "translation audit", "locale check", "i18n 검사", "번역 검사", "locale parity", "translation drift", "translations 점검", "hardcoded string", "i18n audit"]
  uses: []
---

# plot-i18n-audit — i18n compliance static audit

> **Why this skill exists.** Novel is a global service (user direction
> 2026-05-10: *"이건 글로벌 서비스가 될거거든요"*, D-2026-05-11-D,
> ``memory/feedback_plot_global_service.md``). Hardcoded English /
> Korean strings in `.tsx` files bypass the i18n resource bundle and
> create per-component sprawl that resists later migration. The
> existing ``i18n-keys-parity.test.ts`` enforces *parity between
> locales* (en.json ↔ ko.json), but cannot see:
>
> 1. **Hardcoded** user-facing strings the bundle never receives.
> 2. **Undefined** ``t("foo.bar")`` calls whose key is missing from
>    en.json.
> 3. **Stale** keys in en.json that no source file references.
> 4. **Untranslated** values where ko[k] === en[k] for non-trivial text.
>
> This skill closes those four gaps with a single static sweep — no
> TS compiler dependency, no test infra changes, no auto-fix.
> Output is a structured report the user / assistant acts on.

---

## Trigger

Activate when the user says:

- "i18n 검사 / 번역 검사 / translation audit / locale check"
- "PR 올리기 전에 i18n 확인" / "before push i18n"
- "hardcoded string 있나" / "is anything hardcoded"
- Or pastes a `.tsx` file path and asks "i18n OK?"

**Do not** activate this skill for non-Novel codebases — the rules
below cite Novel's i18n infrastructure and decision log directly.

If the user runs the skill with no scope hint, default to **all of
``viewer/src/**/*.{ts,tsx}``** (minus the exclusions below). If they
name a single file, scope to that file only.

---

## Scope

- **Scan:** ``viewer/src/**/*.{ts,tsx}``.
- **Exclude:**
  - ``viewer/src/i18n/**`` — locale source files (``en.json`` /
    ``ko.json`` / ``index.ts`` / ``LanguageToggle.tsx``); these
    OWN the bundle, they are not consumers of it.
  - ``viewer/src/**/*.test.{ts,tsx}`` — test files are
    development artefacts, not user-facing.
  - ``viewer/tests/**`` — same.
  - ``viewer/src/main.tsx`` — bootstrap, no UI text.
- **Locale source:**
  - ``viewer/src/i18n/locales/en.json`` (primary).
  - ``viewer/src/i18n/locales/ko.json`` (Korean).
  - The ``i18n-keys-parity.test.ts`` already pins these in lock-step;
    this audit *reads* them but does not enforce parity.

---

## What counts as "user-facing string"

A literal string in source code is **user-facing** when it appears
in any of these positions:

1. **JSX text node** — the text between an opening and closing tag:
   `<button>Save</button>` → `"Save"` is user-facing.
2. **JSX attribute value** for any of these attributes:
   - ``aria-label`` / ``aria-description`` / ``aria-placeholder``
   - ``title``
   - ``alt``
   - ``placeholder``
   - ``label`` (e.g. ``<input label="Name">``)
   These reach screen readers / tooltips / form chrome — the user
   sees them.
3. **Direct argument to ``alert()`` / ``confirm()`` / ``prompt()``**
   — runtime UI text.

### Exemptions (allowlist)

A literal that matches any of these **does not** count as
user-facing and is silently skipped:

- **Length ≤ 3 characters** — icon glyphs, abbreviations, punctuation
  (``"↔"`` / ``"OK"`` / ``"·"``).
- **NodeKind discriminator** — exact match against the 15 kind
  literals: ``project`` / ``mission`` / ``core_value`` /
  ``identity`` / ``actor`` / ``actor_ref`` / ``service`` /
  ``category`` / ``mission_ref`` / ``value_ref`` /
  ``identity_ref`` / ``metric`` / ``step`` / ``rule`` /
  ``content``. These are technical discriminators, not display
  text; if they ever surface to the user it's via ``t(\`kind.${k}\`)``.
- **Brand mark — regex ``^[A-Z]{2,8}$``** — short all-caps tokens
  like ``PLOT``, ``URL``, ``MCP``. Brands stay untranslated by
  convention.
- **MIME type / format identifier — regex ``^[a-z]+/[a-z0-9.+-]+$``**
  — ``application/json`` etc.
- **Adjacent ``// i18n-skip`` comment** — the line immediately above
  the literal contains this exact substring. Use for WIP / dev-only
  text. Permanent skip is not supported (no ``// i18n-skip-forever``
  variant); permanent → i18n it.

---

## The 4 audits

Run all four in order. Each produces zero or more findings.

### Audit 1 — Hardcoded user-facing strings

For every file in scope, scan the AST-equivalent (regex over the
syntactic positions listed in "What counts as user-facing"):

- For each user-facing string literal, check if it's inside a
  ``t(...)`` call. If **not**, and the literal does not match the
  exemption allowlist, emit a finding.

**Finding shape:**

```
H1 — Hardcoded user-facing string
file: viewer/src/shell/Header.tsx:18
context: <span className="...">PLOT</span>
string:  "PLOT"
fix:     Either i18n it via t("header.brand"), OR confirm it
         matches the brand-mark exemption (^[A-Z]{2,8}$) and
         add a comment // i18n-skip: brand mark.
```

### Audit 2 — Undefined ``t()`` keys

For every ``t("foo.bar")`` or ``t(\`foo.${var}\`)`` call in scope:

- **Static key** (`t("foo.bar")`): look up ``foo.bar`` in en.json.
  If absent, emit a finding.
- **Dynamic key** (template literal with `${...}`): extract the
  static prefix (text before the first `${`). Verify that en.json
  has **at least one** key under that prefix path. If the prefix
  branch is entirely empty / missing, emit a finding (the dynamic
  call will resolve to no key for any input).

**Finding shape:**

```
U1 — Undefined t() key
file: viewer/src/shell/CanvasTabs.tsx:46
call: t(`canvas.tabs.${id}`)
en.json prefix `canvas.tabs.*`: not found
fix:  Add the missing key(s) to en.json + ko.json, OR remove the
      orphan t() call.
```

### Audit 3 — Stale en.json keys

Build the full set of en.json key paths. For each key:

- **Static reference search** — grep all in-scope source files for
  ``"<key>"`` (with both single and double quotes).
- **Dynamic reference search** — for each ``t(\`<prefix>.${expr}\`)``
  call found in scope, mark every key under ``<prefix>.*`` as
  referenced.

Any en.json key with **zero** references (static + dynamic) is stale.

**Finding shape:**

```
S1 — Stale en.json key
key: header.markSessionLegacy
ko.json sibling: "이전 세션 표시" (kept in sync by parity test)
fix:  Remove from en.json + ko.json, OR find the missing source
      reference that should use it.
```

### Audit 4 — Untranslated ko.json values

For every key path in en.json + ko.json, compare values. Emit a
finding when **all** of these are true:

- ``ko[key] === en[key]`` (byte-equal strings).
- ``en[key].length > 3``.
- The value is **not** the key tail (e.g. ``kind.actor`` → ``"actor"``
  is fine; ``button.save`` → ``"Save"`` is NOT fine because the
  English value differs from the path tail and Korean should too).
- The value does **not** match the brand-mark / MIME-type allowlist.

**Finding shape:**

```
T1 — Untranslated ko.json value
key:    serviceDetail.label
en.json: "Service detail"
ko.json: "Service detail"  ← same string, length > 3, not a brand
fix:     Translate ko.json value to "서비스 상세" or similar, OR
         confirm intentional cross-locale match and add the key
         to the audit's exemption list (last resort — prefer
         translation).
```

---

## Report format

Output **one section per audit** that fired ≥ 1 finding (omit
audits with zero findings). After all sections, a **verdict line**:

- ✅ **CLEAN** — zero findings across all four audits.
- 🟡 **FIX** — at least one finding in Audit 1 (hardcoded) or
  Audit 2 (undefined keys). User-visible string is wrong RIGHT NOW
  in the running viewer.
- 🔴 **BLOCK** — same as FIX but with ≥ 3 findings; signals
  systematic i18n bypass rather than a single oversight. Push for
  i18n migration sprint before next user-facing release.

Audits 3 (stale) and 4 (untranslated) alone never trigger 🟡 / 🔴;
they're cleanup-grade findings, not user-visible bugs. They appear
in the report at Minor severity.

---

## What this audit does NOT do

By design:

- **No auto-fix.** The skill reports; the user / assistant edits.
  Auto-fix would have to guess at translation, key naming, and
  exemption — each guess multiplies the audit's risk surface.
- **No parity enforcement.** That's
  ``viewer/tests/i18n-keys-parity.test.ts`` (D-2026-05-11-D); it
  runs in vitest and is the canonical guard for en ↔ ko key sets.
- **No TS compiler dependency.** Static regex matches the existing
  per-kind / per-canvas guard pattern (D-2026-05-12-D /
  D-2026-05-12-F). If the parser's heuristics drift, the failure
  lands here loudly; fix the heuristic.
- **No file write outside the report.** Read-only; reversible.

---

## How to run this skill

The skill is procedural: invoke its trigger phrase, then execute
the four audits manually (each is a defined regex / grep over the
in-scope file set). Until a future commit wires the audits to a
test or hook (Phase 2+ per the evolution path below), the skill
runs in the assistant's reading frame.

Phase 1 (now): manual invocation, manual scan, manual report.

Phase 2 (after several uses confirm the rules don't over- or
under-fit): wire Audit 1 + 2 into a vitest static guard
(``viewer/tests/i18n-static-audit.test.tsx``) so missing keys /
hardcoded strings fail the build. Audits 3 + 4 stay manual
(cleanup-grade — running them on every commit would be noise).

Phase 3 (mature): PreCommit hook gating commits with FIX / BLOCK
verdicts. Per ``project_red_team_review_skill.md`` evolution
philosophy: don't pre-build Phase 2/3; let usage shape them.

---

## Calibration

After the skill fires, watch the user's response:

- User accepts the findings → the rules calibrate.
- User says "PLOT is brand, skip" → the exemption was right;
  the skill correctly forced the user to *confirm* the
  classification.
- User pushes back on a finding (false positive) → update the
  exemption list with a concrete rule, not a one-off skip. The
  skill stays useful only if findings convert to either fixes
  or codified exemptions.
- Audit 3 (stale) repeatedly flags the same dynamic-key prefix →
  the parser is missing a template-literal shape. Fix the parser,
  not the source code.

The skill stays valuable as long as the conversion rate (findings →
real changes) stays above ~50%. If five consecutive runs produce
zero acted-upon findings, the codebase has internalised the rules —
move the audit to a hook and retire the manual invocation.
