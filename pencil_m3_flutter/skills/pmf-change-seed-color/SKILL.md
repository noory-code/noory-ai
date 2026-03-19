---
name: pmf-change-seed-color
description: >
  Change the seed color of the Material Design 3 Pencil library.
  Triggers when the user asks to change the seed color, primary color, brand color,
  or update the color palette/scheme in material-design-guide.lib.pen.
user-invocable: true
metadata:
  version: "1.0.2"
  category: design
  type: unit
  style: procedural
  triggers: [change seed color, change primary color, update color palette, brand color, color scheme]
  uses: []
---

# Change Seed Color

Changing the seed color causes the entire M3 palette (Semantic Colors + Material Color Scheme) to be recalculated.

## Target file

- Standalone execution: `${CLAUDE_PLUGIN_ROOT}/pencil/material-design-guide.lib.pen`
- Delegated execution from `init`: The newly created `<appname>-design-guide.lib.pen`
  (The file opened by init is already active in the editor, so use it as-is)

## Workflow

### Step 1 -- Confirm Seed Color

Ask the user for the new seed color hex value. Example: `#6750A4`

### Step 2 -- Calculate Palette

Use `${CLAUDE_PLUGIN_ROOT}/pencil/md3calc/hct_palette.py` to calculate the palette.

```bash
cd ${CLAUDE_PLUGIN_ROOT}/pencil/md3calc
python3 hct_palette.py <seed_hex>
```

Output format:
```json
{
  "seed": "#6750A4",
  "primary": { "0": "#000000", "10": "...", "20": "...", "30": "...", "40": "...", "50": "...", "60": "...", "70": "...", "80": "...", "90": "...", "95": "...", "99": "...", "100": "#FFFFFF" },
  "secondary": { ... },
  "tertiary": { ... },
  "neutral": { ... },
  "neutralVariant": { ... },
  "error": { "0": "#000000", "10": "#410002", "20": "#690005", "30": "#93000A", "40": "#BA1A1A", "50": "#DE3730", "60": "#FF5449", "70": "#FF897D", "80": "#FFB4AB", "90": "#FFDAD6", "95": "#FFEDEA", "99": "#FFFBFF", "100": "#FFFFFF" }
}
```

> The error palette uses M3 standard values regardless of the seed.

### Step 3 -- Update Semantic Colors Palette

Update the following variables using `mcp__pencil__set_variables`.

**Variables to update:**

| Variable | Theme | Value |
|----------|-------|-------|
| `seed` | `Semantic Colors Palette/Default` | seed hex |
| `primary/0` | `Semantic Colors Palette/Default` | primary[0] |
| `primary/10` | `Semantic Colors Palette/Default` | primary[10] |
| `primary/20` | `Semantic Colors Palette/Default` | primary[20] |
| `primary/30` | `Semantic Colors Palette/Default` | primary[30] |
| `primary/40` | `Semantic Colors Palette/Default` | primary[40] |
| `primary/50` | `Semantic Colors Palette/Default` | primary[50] |
| `primary/60` | `Semantic Colors Palette/Default` | primary[60] |
| `primary/70` | `Semantic Colors Palette/Default` | primary[70] |
| `primary/80` | `Semantic Colors Palette/Default` | primary[80] |
| `primary/90` | `Semantic Colors Palette/Default` | primary[90] |
| `primary/95` | `Semantic Colors Palette/Default` | primary[95] |
| `primary/99` | `Semantic Colors Palette/Default` | primary[99] |
| `primary/100` | `Semantic Colors Palette/Default` | #FFFFFF |
| `secondary/0` ~ `secondary/100` | `Semantic Colors Palette/Default` | secondary[*] |
| `tertiary/0` ~ `tertiary/100` | `Semantic Colors Palette/Default` | tertiary[*] |
| `neutral/0` ~ `neutral/100` | `Semantic Colors Palette/Default` | neutral[*] |
| `neutralVariant/0` ~ `neutralVariant/100` | `Semantic Colors Palette/Default` | neutralVariant[*] |
| `error/0` ~ `error/100` | `Semantic Colors Palette/Default` | M3 standard error values |

### Step 4 -- Update Material Color Scheme

Map M3 Color Scheme tokens based on palette values according to the rules below.

**Light theme:**

| Token | Palette Value |
|-------|---------------|
| `primary` | primary/40 |
| `onPrimary` | primary/100 |
| `primaryContainer` | primary/90 |
| `onPrimaryContainer` | primary/10 |
| `primaryFixed` | primary/90 |
| `primaryFixedDim` | primary/80 |
| `onPrimaryFixed` | primary/10 |
| `onPrimaryFixedVariant` | primary/30 |
| `secondary` | secondary/40 |
| `onSecondary` | secondary/100 |
| `secondaryContainer` | secondary/90 |
| `onSecondaryContainer` | secondary/10 |
| `secondaryFixed` | secondary/90 |
| `secondaryFixedDim` | secondary/80 |
| `onSecondaryFixed` | secondary/10 |
| `onSecondaryFixedVariant` | secondary/30 |
| `tertiary` | tertiary/40 |
| `onTertiary` | tertiary/100 |
| `tertiaryContainer` | tertiary/90 |
| `onTertiaryContainer` | tertiary/10 |
| `tertiaryFixed` | tertiary/90 |
| `tertiaryFixedDim` | tertiary/80 |
| `onTertiaryFixed` | tertiary/10 |
| `onTertiaryFixedVariant` | tertiary/30 |
| `error` | error/40 |
| `onError` | error/100 |
| `errorContainer` | error/90 |
| `onErrorContainer` | error/10 |
| `surface` | neutral/99 |
| `onSurface` | neutral/10 |
| `surfaceVariant` | neutralVariant/90 |
| `onSurfaceVariant` | neutralVariant/30 |
| `surfaceDim` | neutral/87 -- approximated to neutral/90 |
| `surfaceBright` | neutral/98 -- approximated to neutral/99 |
| `surfaceContainerLowest` | neutral/100 |
| `surfaceContainerLow` | neutral/96 -- approximated to neutral/95 |
| `surfaceContainer` | neutral/94 -- approximated to neutral/95 |
| `surfaceContainerHigh` | neutral/92 -- approximated to neutral/90 |
| `surfaceContainerHighest` | neutral/90 |
| `outline` | neutralVariant/50 |
| `outlineVariant` | neutralVariant/80 |
| `inverseSurface` | neutral/20 |
| `onInverseSurface` | neutral/95 |
| `inversePrimary` | primary/80 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/40 |

**Dark theme:**

| Token | Palette Value |
|-------|---------------|
| `primary` | primary/80 |
| `onPrimary` | primary/20 |
| `primaryContainer` | primary/30 |
| `onPrimaryContainer` | primary/90 |
| `primaryFixed` | primary/90 |
| `primaryFixedDim` | primary/80 |
| `onPrimaryFixed` | primary/10 |
| `onPrimaryFixedVariant` | primary/30 |
| `secondary` | secondary/80 |
| `onSecondary` | secondary/20 |
| `secondaryContainer` | secondary/30 |
| `onSecondaryContainer` | secondary/90 |
| `secondaryFixed` | secondary/90 |
| `secondaryFixedDim` | secondary/80 |
| `onSecondaryFixed` | secondary/10 |
| `onSecondaryFixedVariant` | secondary/30 |
| `tertiary` | tertiary/80 |
| `onTertiary` | tertiary/20 |
| `tertiaryContainer` | tertiary/30 |
| `onTertiaryContainer` | tertiary/90 |
| `tertiaryFixed` | tertiary/90 |
| `tertiaryFixedDim` | tertiary/80 |
| `onTertiaryFixed` | tertiary/10 |
| `onTertiaryFixedVariant` | tertiary/30 |
| `error` | error/80 |
| `onError` | error/20 |
| `errorContainer` | error/30 |
| `onErrorContainer` | error/90 |
| `surface` | neutral/10 |
| `onSurface` | neutral/90 |
| `surfaceVariant` | neutralVariant/30 |
| `onSurfaceVariant` | neutralVariant/80 |
| `surfaceDim` | neutral/6 -- approximated to neutral/10 |
| `surfaceBright` | neutral/24 -- approximated to neutral/20 |
| `surfaceContainerLowest` | neutral/4 -- approximated to neutral/0 |
| `surfaceContainerLow` | neutral/10 |
| `surfaceContainer` | neutral/12 -- approximated to neutral/10 |
| `surfaceContainerHigh` | neutral/17 -- approximated to neutral/20 |
| `surfaceContainerHighest` | neutral/22 -- approximated to neutral/20 |
| `outline` | neutralVariant/60 |
| `outlineVariant` | neutralVariant/30 |
| `inverseSurface` | neutral/90 |
| `onInverseSurface` | neutral/20 |
| `inversePrimary` | primary/40 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/80 |

> The light-mc, dark-mc, light-hc, and dark-hc themes are medium/high contrast variants.
> This skill only updates light/dark. If mc/hc is needed, inform the user.

### Step 5 -- Regenerate Dart Code

Always execute regardless of standalone or delegated mode.
The `.pen` file is the SSOT for colors, so Dart code must be generated based on `.pen` variables.

```
1. Run mcp__pencil__get_variables() -- save results to a temp file via tempfile.gettempdir()
2. python3 ${CLAUDE_PLUGIN_ROOT}/pencil/md3calc/gen_dart.py \
     --from-json <temp_dir>/pen_vars.json \
     --out <flutter_lib_path> \
     --barrel <appname>_ui
```

> The get_variables() result can exceed 100K+ characters. Always save to a file first and pass via `--from-json`.
> `--from-json` directly parses the native format (`{name: {type, value: [{theme, value}]}}`) of get_variables().
> This ensures accurate synchronization even when the user has manually edited colors in Pencil.

Generated files:
- `semantic_color_palette.dart`, `theme_colors.dart`, `theme.dart`, `tokens.dart`
- `<appname>_ui.dart` -- barrel file generated when `--barrel` is specified

> If `flutter_lib_path` is provided via context, use it as-is. Otherwise, ask the user.
> Flutter convention default path: `lib/src/design/`

### Step 6 -- Verify Results

Report to the user after completion:
- New seed color
- Primary (light): primary/40, Primary (dark): primary/80
- Flutter theme code regeneration complete: `<flutter_lib_path>/semantic_color_palette.dart`
