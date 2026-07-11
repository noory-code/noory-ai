---
name: pmf-init
description: >
  Initialize a new app design guide .lib.pen file.
  Triggers when the user asks to initialize, create a new design guide,
  or set up a new app's design system in Pencil.
user-invocable: true
metadata:
  version: "1.1.0"
  category: design
  type: composite
  style: procedural
  triggers: [initialize design guide, create design guide, set up design system, pencil init, new app design]
  uses: [pmf-change-seed-color, pmf-change-logo]
---

# Init — App Design Guide

> Before executing this workflow, read and apply `../HOST_CONTRACT.md`.

Creates a per-app design guide `.lib.pen` file.
The `.lib.pen` extension is required so Pencil can import it as a library in other `.pen` files.
`material-design-guide.lib.pen` is kept as a shared library, and a separate file is created for each app.

## Step 0 — Environment Verification

Verification is split into two groups. **Group A** is required for file operations, and **Group B** is required for Pencil/Dart operations.
If Group A fails, stop immediately. Group B is verified after Step 2 completes (just before opening the Pencil file).

### Group A — File Operation Prerequisites (verified in Step 0)

#### A-1. Verify Python 3.9+ Installation

```bash
python3 --version
```

- Python 3.9 or higher → proceed to next verification
- Missing or version too low → **stop**:
  > "Python 3.9 or higher is required. Please install it and try again."

#### A-2. Verify materialyoucolor Package

```bash
python3 -c "import materialyoucolor; print('ok')"
```

- `ok` output → proceed to next verification
- ImportError → **stop**:
  > "Please run pip install materialyoucolor and try again."

#### A-3. Verify Python Script Files Exist

Resolve `<plugin-root>` from the shared host contract, then run:

```bash
python3 -c "import pathlib; root=pathlib.Path('<plugin-root>'); [exit(1) for p in ['pencil/md3calc/hct_palette.py','pencil/md3calc/gen_dart.py'] if not (root/p).exists()]"
```

- Both files exist → **Group A passed**
- Missing → **stop**:
  > "Plugin files not found. Please verify that the pencil-m3-flutter plugin is installed.
  > Claude Code: `/plugin install pencil-m3-flutter@noory-ai`
  > Codex: `codex plugin add pencil-m3-flutter@noory-ai`"

When Group A passes: output `✓ Environment check complete. Starting setup.` and proceed to Step 1.

### Group B — Pencil MCP Connection (verified in Step 2-2)

> Pencil is only needed after file copying. Verified in Step 2-2.

---

## Step 1 — Gather Information

Ask the user to confirm three items with selectable options. Provide a recommended default for each item and include a manual input option.

1. **Save path** — directory to save the `.lib.pen` file:
   - `pencil/` (recommended — under project root)
   - `apps/<appname>/pencil/`
   - Manual input

2. **App name** — used in the filename (default extracted from project directory name):
   - `<project directory name>` (recommended)
   - Manual input

3. **Flutter lib path** — location to generate Dart code:
   - `lib/src/design/` (recommended)
   - `lib/core/theme/`
   - Manual input

> Seed color and logo are collected in later steps.
> Show results after each step completes and proceed to the next step. Do not skip steps.

## Step 2 — Create App Design Guide File

Copy `material-design-guide.lib.pen` to create an app-specific library file.
Creating an empty file would lack M3 components/variables, so the copy method must be used.

### 2-1. Copy File (Pencil not required)

```bash
cp <plugin-root>/pencil/material-design-guide.lib.pen "<save_path>/<appname>-design-guide.lib.pen"
```

> Using the copy method ensures all 166 M3 components and Color Scheme variables from material-design-guide.lib.pen are included.

After completion, report: `✓ <appname>-design-guide.lib.pen file copy complete.`

### 2-2. Verify Pencil MCP Connection (Group B verification)

Verify Pencil is running before opening the file:

```
mcp__pencil__get_editor_state()
```

- Response success → proceed to 2-3
- Failure → **stop**:
  > "Cannot connect to Pencil MCP. Please check the following:
  > 1. Verify that the Pencil app is running
  > 2. Check server status in Pencil → Settings → MCP Server
  > 3. Reconnect the Pencil MCP server with the active host's MCP management surface
  > Please run this skill again after connecting."

### 2-3. Open File in Pencil

```
mcp__pencil__open_document("<save_path>/<appname>-design-guide.lib.pen")
```

After completion, report: `✓ <appname>-design-guide.lib.pen opened in Pencil. Next: seed color setup`

## Step 3 — Seed Color Setup + Dart Code Generation

Execute the full procedure of the `pmf-change-seed-color` skill.
The target file is `<appname>-design-guide.lib.pen` created in Step 2 (currently open in the editor).
Pass the `flutter_lib_path` collected in Step 1 as context.

`pmf-change-seed-color` completes both Pencil variable updates and Dart file generation.
Dart generation uses the `.pen` file as SSOT — `get_variables()` → `--from-json` to generate based on actual variable values.
Include the `--barrel <appname>_ui` option to also generate a barrel file:
- `semantic_color_palette.dart` — palette raw values
- `theme_colors.dart` — ColorScheme 6 variants
- `theme.dart` — AppTheme (ThemeData)
- `tokens.dart` — Spacing / Radius / Elevation etc.
- `<appname>_ui.dart` — barrel file (imports all 4 above at once)

> `theme.dart` uses the `google_fonts` package. It must be added to the project `pubspec.yaml`:
> ```yaml
> dependencies:
>   google_fonts: ^6.2.1
> ```

After completion, report: `✓ Seed color + Dart code generation complete. Next: logo setup`

## Step 4 — Logo Setup

Execute the full procedure of the `pmf-change-logo` skill.

> See `pmf-change-logo` skill reference.

After completion, report: `✓ Logo setup complete. Next: project design skill creation`

## Step 5 — Flutter Workspace Registration (if applicable)

Check whether the root `pubspec.yaml` contains a `workspace:` section:

```bash
python3 -c "import pathlib; print('workspace project' if 'workspace:' in pathlib.Path('pubspec.yaml').read_text() else 'standalone')"
```

- If workspace project → instruct user to add app path to the `workspace:` list in root `pubspec.yaml`:
  > "Please add the app path to the workspace: list in the root pubspec.yaml."
- If standalone project → skip this step

## Step 6 — Create Project Design Skill

Create a project-specific `design` skill file based on `pencil-m3-flutter:design-guide`.
This skill's role: **user request → output prompt text to paste into the Pencil AI chat**.

Generate the file content once, then write the same content to both host discovery paths:

- Claude Code: `<project root>/.claude/skills/design/SKILL.md`
- Codex: `<project root>/.agents/skills/design/SKILL.md`

File contents:
```markdown
---
name: design
description: >
  Generate a Pencil AI prompt for designing screens of <appname>.
  Triggers when the user asks to design a screen, create a UI, or build a layout.
user-invocable: true
---

# Design — <appname>

Based on the M3 rules and prompt generation methodology from `pencil-m3-flutter:design-guide`.

## Role

When the user requests a screen design:
1. Apply M3 rules from `pencil-m3-flutter:design-guide` + project-specific rules below
2. **Output prompt text to paste into the Pencil AI chat**

> This project skill produces a prompt rather than manipulating Pencil directly.
> Copy the output prompt and paste it into the Pencil AI chat.

## Project Information

- Pencil library: `<pen_file_path>/<appname>-design-guide.lib.pen`
- Screen working file: `<pen_file_path>/<appname>-screens.pen` (or user-specified)
- Flutter theme code: `<flutter_lib_path>/`

## Project-Specific Rules

> Fill this section to match your project:
> - App-specific components and IDs (defined in <appname>-design-guide.lib.pen)
> - Frequently used screen patterns
> - Brand color / typography specifics

## Prompt Output Format

Follow the prompt generation methodology from `pencil-m3-flutter:design-guide`.
Fill in the screen content using the template below and output:

\`\`\`
Add a <screen name> screen to <appname>-screens.pen.

## Common Rules
- Colors: never hardcode. Use only Color Role variables such as $primary, $surface, $onSurface
- Form factor: Frame/Mobile/390 (ID: dnJUo)
- Place on empty canvas space (100px gap)

## Layout
<screen structure>

## Components
<component list and IDs>

## Project-Specific Rules
<apply rules from section above>
\`\`\`
```

> After creation, instruct the user to "fill in the Project-Specific Rules section."

## Step 7 — Final Report

After completion, report to the user:

```
✓ <appname>-design-guide.lib.pen creation complete

- Seed color: <hex>
- Primary (light): <primary/40>
- Primary (dark):  <primary/80>
- Flutter theme code: <flutter_lib_path>/
- Logo: applied
- Claude Code project skill: .claude/skills/design/SKILL.md
- Codex project skill: .agents/skills/design/SKILL.md

Next steps:
  1. Fill in the "Project-Specific Rules" section in SKILL.md for your app
  2. Create a new .pen file in Pencil (e.g., <appname>-screens.pen)
  3. Add an import for <appname>-design-guide.lib.pen to that file
  4. Invoke the design skill with the active host's skill picker or natural-language trigger
```
