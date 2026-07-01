---
name: mashbill-frontend-bug-diagnosis
description: Diagnose Novel canvas UI bugs (cursor flicker, hover wrong, hit-test wrong, click not firing, button not visible) by running Playwright DOM probes BEFORE proposing any code change. Triggers on cursor / hover / pointer / hit-test / flicker / 깜빡 / button doesn't / 안 눌려 / click 안 됨 / 호버 / 손가락 / grab / crosshair keywords plus a Novel canvas context.
metadata:
  version: "1.0.0"
  category: dev-process
  type: unit
  style: procedure
  triggers: [cursor, hover, pointer, hit-test, flicker, "깜빡", "보자기", "검지", click, "안 눌려", "안 됨", grab, crosshair, button, hit, hover wrong]
  uses: [mcp__plugin_playwright_playwright__browser_navigate, mcp__plugin_playwright_playwright__browser_evaluate, mcp__plugin_playwright_playwright__browser_take_screenshot, mcp__plugin_playwright_playwright__browser_hover, mcp__plugin_playwright_playwright__browser_click]
---

# mashbill-frontend-bug-diagnosis — probe before fix

> **Why this skill exists.** Novel v0.13.3 → v0.13.10 burned ~6 cursor
> rounds of round-trip with the user because the assistant theorised
> from CSS files first, fixed based on the theory, shipped, the user
> reported the same bug. Each round was 5-10 minutes of human time
> wasted. v0.13.10 finally ran a Playwright DOM probe and identified
> the actual cause (`.react-flow__node[role="button"]` from RF v11
> a11y) in 30 seconds. **This skill enforces probe-first as a
> deterministic procedure.**

---

## Trigger

Activate when the user reports a Novel canvas UI behaviour that
disagrees with [`SPEC.md`](../../mashbill/docs/SPEC.md) or
[`CURSOR.md`](../../mashbill/docs/CURSOR.md):

- Cursor showing a wrong shape (`pointer` instead of `grab`,
  `default` on a node, etc.)
- Cursor flickering between two shapes on the same hover
- A click not firing on something that looks clickable
- A hover not revealing something the SPEC promises
- A button not appearing, or appearing in the wrong place

If the user description is vague ("뭔가 이상해"), ask one specific
question to localise it ("어느 노드 / 어느 버튼 / 어느 동작이요?")
THEN apply the procedure below.

---

## Procedure (no skipping)

### Step 1 — Verify Playwright + dev server are running

```bash
# Check viewer + MCP servers
curl -s -o /dev/null -w "vite=%{http_code}\n" http://localhost:5193/
curl -s -o /dev/null -w "mcp=%{http_code}\n"  http://localhost:5190/
```

If not up, start them:
```bash
cd mashbill && uv run mashbill-http &
cd novel/viewer && npm run dev &
```

Verify Playwright tools are loaded via `ToolSearch query="select:mcp__plugin_playwright_playwright__browser_navigate,mcp__plugin_playwright_playwright__browser_evaluate"`. If not loaded, ask the user to install the Playwright MCP plugin first — **do not** proceed to theorise from code.

### Step 2 — Navigate to the affected canvas

```text
browser_navigate(url:
  "http://localhost:5193/?project_path=<USER_PROJECT_PATH>&project=<NAME>&canvas=<CANVAS>")
```

Use the test project (`/Users/woogis/Workspace/plot-test-v013` is the
canonical one) unless the user specifies another. The canvas key is
`foundation` / `actors` / `services` / `service_detail:<id>`.

### Step 3 — Take a baseline screenshot

```text
browser_take_screenshot(filename: "diag-baseline.png")
```

Read the screenshot. **Identify pixel coordinates of the suspect
element(s)** before any probe. Coordinates feed Step 4.

### Step 4 — Run the cursor / hit-test probe at those coordinates

For each suspect coordinate, call `browser_evaluate` with this
template (parameterise the points list):

```javascript
() => {
  const points = [
    { name: 'descriptive label 1', x: 583, y: 240 },
    { name: 'descriptive label 2', x: 700, y: 100 },
    // ... add per-suspect-element points
  ];
  return points.map((p) => {
    const el = document.elementFromPoint(p.x, p.y);
    if (!el) return { ...p, cursor: '(no element)' };
    return {
      ...p,
      cursor: getComputedStyle(el).cursor,
      tag: el.tagName,
      cls: String(el.className || '').slice(0, 80),
      role: el.getAttribute('role') || '',
      id: el.id || '',
    };
  });
}
```

For a more thorough sweep (no specific suspects yet), grid-sample:

```javascript
() => {
  const seen = new Map();
  for (let x = 200; x <= 1400; x += 50) {
    for (let y = 80; y <= 1100; y += 50) {
      const el = document.elementFromPoint(x, y);
      if (!el) continue;
      const cur = getComputedStyle(el).cursor;
      if (!seen.has(cur)) {
        seen.set(cur, {
          tag: el.tagName,
          cls: String(el.className || '').slice(0, 80),
          role: el.getAttribute('role') || '',
        });
      }
    }
  }
  return Array.from(seen, ([cursor, m]) => ({ cursor, ...m }));
}
```

### Step 5 — Walk the parent chain to find the cursor source

If Step 4 shows an unexpected cursor, walk the DOM tree upward to find
the ancestor that *owns* the cursor declaration:

```javascript
() => {
  const trail = [];
  let el = document.elementFromPoint(<X>, <Y>);
  while (el && el !== document.documentElement) {
    const cs = getComputedStyle(el);
    trail.push({
      tag: el.tagName,
      cls: String(el.className || '').slice(0, 90),
      role: el.getAttribute('role') || '',
      cursor: cs.cursor,
    });
    el = el.parentElement;
  }
  return trail;
}
```

The first row whose cursor matches the unexpected value is where the
declaration takes effect. The bug is at — or above — that element.

### Step 6 — Identify the source rule

Now (and **only** now) read code. Check, in this order:

1. `viewer/src/styles.css` — our explicit overrides.
2. `node_modules/reactflow/dist/style.css` — RF defaults.
3. `node_modules/@reactflow/node-resizer/dist/style.css` — resizer
   cursors.
4. **Tailwind preflight** (`@tailwind base;`) — silently applies to
   `[type="button"]`, `[role="button"]`, `:disabled`. Cause of the
   v0.13.10 root cursor bug. Always check.
5. Inline element styles (rare, but possible).

For **each cursor declaration found**, verify it matches what the
probe in Step 4 reported. Mismatch = the rule is being shadowed by a
later rule; trace specificity.

### Step 7 — Propose the fix anchored to the probe

The fix proposal must include:

- The **exact element** found in Step 5 (tag + class + role).
- The **source rule** found in Step 6 (file + selector + line).
- The **CSS or component change** that addresses the source rule
  without breaking sibling rules.
- A **predicted post-fix probe result** (what the cursor should be
  after the change).

### Step 8 — Apply the fix, then re-probe to verify

After the fix lands (HMR auto-reloads styles.css), re-run the Step 4
probe. The reported cursor must match the prediction in Step 7.

### Step 9 — Take a confirmation screenshot

```text
browser_take_screenshot(filename: "diag-postfix.png")
```

Compare against `diag-baseline.png`. Visual difference must match the
intent.

### Step 10 — Update SPEC / CURSOR / DECISIONS per Gate 0

If the fix changed any spec'd behaviour, [Gate 0](../../mashbill/CLAUDE.md)
fires. Pin the new behaviour into [`CURSOR.md`](../../mashbill/docs/CURSOR.md)
and add a `D-YYYY-MM-DD-X` entry in
[`DECISIONS.md`](../../mashbill/docs/DECISIONS.md) before commit.

---

## Banned shortcuts (do not skip steps)

| Shortcut | Why it's banned |
|---|---|
| Reading CSS files first, then probing | The CSS doesn't tell you which rule wins at a specific pixel. The probe does. v0.13.3-v0.13.10 burned 6 rounds on this. |
| Probing only one point | Single-point probes miss flicker zones. Use a grid sweep or at least 5 named points across the suspect surface. |
| Trusting `tsc --noEmit` to catch UI bugs | Type-checks don't run cursors. JSDOM tests don't compute cursors either. Browser-only verification. |
| Shipping the fix without re-probing | The fix may interact with another rule; re-probe is mandatory. |
| Skipping the parent-chain walk | The element under the cursor is rarely the rule's source. The parent chain identifies the source. |

---

## Quick reference — common Novel cursor bug patterns

| Symptom | Likely source (probe first to confirm) |
|---|---|
| Node body shows `pointer` not `grab` | `.react-flow__node[role="button"]` Tailwind preflight (D-2026-05-10-F) |
| EditableText label shows `pointer` not inherited | `[role="button"]` Tailwind preflight on the span; cancellation rule in styles.css (D-2026-05-10-C) |
| Pane shows `default` not `grab` | Old v0.13.4 `cursor: default !important` override left in place (removed v0.13.6 / D-2026-05-10-A) |
| Crosshair on hover where SPEC says grab | Probably hovering over a connection handle (RF default `connectionindicator`) — check coordinates against handle positions |
| Cursor flickers near node edge | Not the v0.13.5 outline-paint-outside-hit-box theory anymore (that was wrong); usually crossing into a handle's hit zone |

---

## Cross-references

- [`docs/CURSOR.md`](../../mashbill/docs/CURSOR.md) — canvas cursor SSOT.
- [`docs/SPEC.md` §Cursor states](../../mashbill/docs/SPEC.md) — table form.
- [`docs/DECISIONS.md` D-2026-05-10-F](../../mashbill/docs/DECISIONS.md) — the
  diagnosis story that motivated this skill.
- [`docs/DOMAIN.md`](../../mashbill/docs/DOMAIN.md) — bounded contexts (cursor
  is a cross-cutting visual contract; it belongs nowhere specific but
  must remain consistent).
