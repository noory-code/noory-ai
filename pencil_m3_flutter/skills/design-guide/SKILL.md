---
name: design-guide
description: >
  M3 Expressive base rules and component reference for Flutter screen design using the Pencil library.
  Used as the base layer for project-specific design skills; not directly invocable.
user-invocable: false
metadata:
  version: "1.0.2"
  category: design
  type: unit
  style: guide
  triggers: [M3 design guide, material design rules, component reference, design base layer, pencil design]
  uses: []
---

# Design Guide — M3 Expressive (Base)

This skill serves two purposes:

1. **Direct use**: Claude Code assembles screens directly via Pencil MCP
2. **Base layer**: Project-specific `design` skills inherit these rules to generate Pencil AI prompts

---

## M3 Rules (Base)

Project `design` skills inherit this section as-is.

### Component Usage Principles

| Component | Rule |
|---------|------|
| **Buttons** | Only 1 Filled per screen. Hierarchy: Filled > FilledTonal > Elevated > Outlined > Text |
| **FAB** | Only 1 per screen. Use only for the single most important action |
| **NavigationBar** | Mobile 2–5 destinations. Always fixed at the bottom of the screen |
| **NavigationRail** | Tablet/desktop only |
| **NavigationDrawer** | When there are 5 or more destinations |
| **TextFields** | Default is Filled. Use Outlined only on complex backgrounds |
| **Cards** | Elevated: flat backgrounds, Filled: subtle grouping, Outlined: complex backgrounds |
| **Chips** | Assist: suggested actions, Filter: filtering, Input: user input values, Suggestion: dynamic options |
| **Selection** | Checkbox: multiple selection, Radio: single selection, Switch: On/Off toggle |
| **Snackbar** | Simple non-intrusive messages. Use Dialog for important decisions |
| **Colors** | Always use Color Role variables ($primary, $surface, etc.). Never hardcode |

### Component ID Reference (material-design-guide.lib.pen)

| Component | ID |
|---------|-----|
| Frame/Mobile/390 | `dnJUo` |
| Frame/Tablet/768 | `P7T42` |
| Frame/Desktop/1440 | `YzwZK` |
| TopAppBar/Small | `Mv3K9` |
| TopAppBar/CenterAligned | `Z4NCN` |
| NavigationBar/3Items | `ItYES` |
| NavigationBar/4Items | `7PeTi` |
| NavigationBar/5Items | `0StZU` |
| FAB/Default | `9XN45` |
| FAB/Extended | `7Gdu4` |
| Buttons/Filled/Rounded/lg | `SgybC` |
| Buttons/Filled/Rounded/md | `wq43H` |
| Buttons/FilledTonal/Rounded/md | `f8Ndk` |
| Buttons/Outlined/Rounded/md | `JTH1z` |
| Buttons/Text/Rounded/md | `hgI1q` |
| TextFields/Filled/Empty | `1gP7O` |
| TextFields/Outlined/Empty | `j0QDR` |
| Lists/OneLineItem | `HoJ5r` |
| Lists/TwoLineItem | `X6KcN` |
| Lists/ThreeLineItem | `AIucm` |
| Cards/Elevated | `WTD0O` |
| Cards/Filled | `r90Tz` |
| Cards/Outlined | `y9sA7` |
| Switch/On | `4cwpx` |
| Switch/Off | `wKKuZ` |
| Checkbox/Checked | `WMMjV` |
| Checkbox/Unchecked | `FgBKf` |
| RadioButton/Selected | `zAPPR` |
| Divider/Full | `YQxB2` |
| Snackbar/TextOnly | `BR6ZB` |

### Layout Patterns by Screen Type

**Login / Onboarding**
```
Frame/Mobile/390
  └ Hero area (~40% height, fill=$primaryContainer)
      └ Logo + App name
  └ Form card (cornerRadius [28,28,0,0], fill=$surface)
      └ Title + Subtitle
      └ TextFields/Filled × N
      └ Buttons/Filled (full-width, 1 primary action)
      └ Buttons/Text (secondary action)
```

**Home / List**
```
Frame/Mobile/390
  └ TopAppBar/Small (fixed at top)
  └ Scrollable content area
      └ List items
  └ FAB/Default (bottom right)
  └ NavigationBar (fixed at bottom)
```

**Settings**
```
Frame/Mobile/390
  └ TopAppBar/Small
  └ Section label (14px, $primary)
  └ Lists/TwoLineItem + Switch combination
  └ Divider/Full
  └ Repeat for next section
```

**Detail**
```
Frame/Mobile/390
  └ TopAppBar (with back navigation)
  └ Content card
  └ FAB/Extended (primary action)
```

---

## Prompt Generation Methodology

Project `design` skills generate Pencil AI prompts using this methodology.

### Information to Include in Prompts

1. **Target file**: Which `.pen` file to work on
2. **Screen name**: Name of the screen to generate
3. **Layout structure**: Matching pattern from above or custom structure
4. **Component list**: Components to use and their IDs
5. **Color rules**: Use only Color Role variables ($primary, $surface, etc.)
6. **Project-specific rules**: Additional constraints per app

### Prompt Output Format

```
Add a <screen name> screen to <filename>.pen.

## Common Rules
- Colors: Never hardcode. Use only Color Role variables such as $primary, $surface, $onSurface
- Form factor: Frame/Mobile/390 (ID: dnJUo)
- Place on empty canvas space (100px spacing)

## Layout
<Screen structure description>

## Components
<Component name (ID: xxx)> × N — <Role description>

## Project-Specific Rules
<Additional app-specific rules>
```

---

## Claude Code → Pencil MCP Direct Execution (Optional)

Used when Claude Code needs to assemble screens directly via Pencil MCP.

### Step 1 — Prepare Working File

```
mcp__pencil__get_editor_state()
```

- If a `.pen` file that imports `<appname>-design-guide.lib.pen` is open → Proceed to Step 2
- If not → Create a new `.pen` file and guide the user to import `<appname>-design-guide.lib.pen`

### Step 2 — Gather Design Requirements

Identify required components, layout, and color rules.

### Step 3 — Find Empty Space

```
mcp__pencil__find_empty_space_on_canvas(direction: "right", width: ..., height: ..., padding: 100)
```

### Step 4 — Create Placeholder Frame

```javascript
screen=I(document, {type: "ref", ref: "dnJUo", placeholder: true, x: ..., y: ...})
```

### Step 5 — Assemble Components

Place components following the Component ID Reference and M3 rules above.

No hardcoded colors:
```javascript
{fill: "$primary"}      // ✓
{fill: "#6750A4"}       // ✗
```

### Step 6 — Verify and Finalize

```
mcp__pencil__get_screenshot(nodeId)
U("frameId", {placeholder: false})
```
