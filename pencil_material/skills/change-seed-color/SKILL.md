---
name: change-seed-color
description: >
  Change the seed color of the Material Design 3 Pencil library.
  Triggers when the user asks to change the seed color, primary color, brand color,
  or update the color palette/scheme in material-design-guide.lib.pen.
user-invocable: true
allowed-tools: ["Bash", "mcp__pencil__get_variables", "mcp__pencil__set_variables"]
---

# Change Seed Color

시드 컬러를 변경하면 M3 팔레트 전체(Semantic Colors + Material Color Scheme)가 재계산된다.

## Target file

`pencil_material/pencil/material-design-guide.lib.pen`

## Workflow

### Step 1 — 시드 컬러 확인

사용자에게 새 시드 컬러 hex 값을 확인한다. 예: `#6750A4`

### Step 2 — 팔레트 계산

`pencil_material/pencil/md3calc/hct_palette.py` 를 사용해 팔레트를 계산한다.

```bash
cd pencil_material/pencil/md3calc
python3 hct_palette.py <seed_hex>
```

출력 형식:
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

> error 팔레트는 시드와 무관하게 M3 표준값을 사용한다.

### Step 3 — Semantic Colors Palette 업데이트

`mcp__pencil__set_variables` 로 아래 변수들을 업데이트한다.

**업데이트 대상 변수 목록:**

| 변수명 | 테마 | 값 |
|--------|------|-----|
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
| `error/0` ~ `error/100` | `Semantic Colors Palette/Default` | M3 표준 error 값 |

### Step 4 — Material Color Scheme 업데이트

팔레트 값을 기반으로 M3 Color Scheme 토큰을 아래 규칙에 따라 매핑한다.

**light 테마:**

| 토큰 | 팔레트 값 |
|------|-----------|
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
| `surfaceDim` | neutral/87 → neutral/90 근사 |
| `surfaceBright` | neutral/98 → neutral/99 근사 |
| `surfaceContainerLowest` | neutral/100 |
| `surfaceContainerLow` | neutral/96 → neutral/95 근사 |
| `surfaceContainer` | neutral/94 → neutral/95 근사 |
| `surfaceContainerHigh` | neutral/92 → neutral/90 근사 |
| `surfaceContainerHighest` | neutral/90 |
| `outline` | neutralVariant/50 |
| `outlineVariant` | neutralVariant/80 |
| `inverseSurface` | neutral/20 |
| `onInverseSurface` | neutral/95 |
| `inversePrimary` | primary/80 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/40 |

**dark 테마:**

| 토큰 | 팔레트 값 |
|------|-----------|
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
| `surfaceDim` | neutral/6 → neutral/10 근사 |
| `surfaceBright` | neutral/24 → neutral/20 근사 |
| `surfaceContainerLowest` | neutral/4 → neutral/0 근사 |
| `surfaceContainerLow` | neutral/10 |
| `surfaceContainer` | neutral/12 → neutral/10 근사 |
| `surfaceContainerHigh` | neutral/17 → neutral/20 근사 |
| `surfaceContainerHighest` | neutral/22 → neutral/20 근사 |
| `outline` | neutralVariant/60 |
| `outlineVariant` | neutralVariant/30 |
| `inverseSurface` | neutral/90 |
| `onInverseSurface` | neutral/20 |
| `inversePrimary` | primary/40 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/80 |

> light-mc, dark-mc, light-hc, dark-hc 테마는 medium/high contrast 변형이다.
> 이 스킬에서는 light/dark 만 업데이트한다. mc/hc가 필요하면 사용자에게 알린다.

### Step 5 — 결과 확인

변경 완료 후 사용자에게 보고:
- 새 seed color
- 주요 토큰 값 (primary, secondary, tertiary)
- Flutter `colors.dart` 업데이트가 필요함을 안내
