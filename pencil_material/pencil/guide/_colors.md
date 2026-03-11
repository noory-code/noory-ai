# Colors

## M3 링크

| 페이지 | URL |
|--------|-----|
| Color System | https://m3.material.io/styles/color/overview |
| Color Roles | https://m3.material.io/styles/color/roles |

---

## 3-레이어 컬러 아키텍처

```
Layer 1 — Material Color Palette     (AppColors)
  primary/0~100, secondary/0~100, ...
  → 원시 hex 값. UI에 직접 쓰지 않는다.

       ↓ 역할 부여

Layer 2 — Semantic Colors Palette    (AppSemanticColors)
  brandPrimary = AppColors.primary40
  brandError   = AppColors.error40
  → "어떤 용도"인지 이름을 붙인다. ThemeData에 연결한다.

       ↓ 테마 적용

Layer 3 — Material Color Scheme      (AppTheme → colorScheme)
  MaterialApp(theme: AppTheme.light, darkTheme: AppTheme.dark)
  → 위젯에서는 Theme.of(context).colorScheme.primary 로 접근.
```

---

## Layer 1 — Material Color Palette

**파일**: `lib/src/colors.dart` → `AppColors`

팔레트 원시값. 6개 색조 × 13단계 = 78개 상수.

```dart
// 절대 UI 코드에서 직접 쓰지 않는다
AppColors.primary40   // #B3006A
AppColors.neutral99   // #FFFBFF
AppColors.error80     // #FFB4AB
```

| 팔레트 | 범위 | 예시 |
|--------|------|------|
| primary | 0~100 | #000000 → #FFFFFF |
| secondary | 0~100 | #000000 → #FFFFFF |
| tertiary | 0~100 | #000000 → #FFFFFF |
| neutral | 0~100 | #000000 → #FFFFFF |
| neutralVariant | 0~100 | #000000 → #FFFFFF |
| error | 0~100 | #000000 → #FFFFFF |

---

## Layer 2 — Semantic Color Palette

**파일**: `lib/src/semantic_color_palette.dart` → `SemanticColorPalette`

Layer 1 팔레트의 원시값. `ThemeColors`/`_ThemeColorSet` 내부에서만 참조하며, UI 코드에서 직접 사용하지 않는다.

```dart
// Layer 2 (ThemeColors 내부에서 참조)
SemanticColorPalette.primary40    // #B3006A
SemanticColorPalette.neutral99    // #FFFBFF
SemanticColorPalette.error80      // #FFB4AB

// UI 코드에서 직접 사용 금지 — colorScheme 으로 접근한다
```

---

## Layer 3 — Color Scheme (실제 사용)

**파일**: `lib/src/theme.dart` → `AppTheme`

### MaterialApp 세팅

```dart
MaterialApp(
  theme: AppTheme.light,
  darkTheme: AppTheme.dark,
  themeMode: ThemeMode.system,
  ...
)
```

### 위젯에서 색상 접근

```dart
final cs = Theme.of(context).colorScheme;

// Primary
cs.primary                  // $primary
cs.onPrimary                // $onPrimary
cs.primaryContainer         // $primaryContainer
cs.onPrimaryContainer       // $onPrimaryContainer
cs.primaryFixed             // $primaryFixed
cs.primaryFixedDim          // $primaryFixedDim
cs.onPrimaryFixed           // $onPrimaryFixed
cs.onPrimaryFixedVariant    // $onPrimaryFixedVariant

// Secondary
cs.secondary                // $secondary
cs.onSecondary              // $onSecondary
cs.secondaryContainer       // $secondaryContainer
cs.onSecondaryContainer     // $onSecondaryContainer
cs.secondaryFixed           // $secondaryFixed
cs.secondaryFixedDim        // $secondaryFixedDim
cs.onSecondaryFixed         // $onSecondaryFixed
cs.onSecondaryFixedVariant  // $onSecondaryFixedVariant

// Tertiary
cs.tertiary                 // $tertiary
cs.onTertiary               // $onTertiary
cs.tertiaryContainer        // $tertiaryContainer
cs.onTertiaryContainer      // $onTertiaryContainer
cs.tertiaryFixed            // $tertiaryFixed
cs.tertiaryFixedDim         // $tertiaryFixedDim
cs.onTertiaryFixed          // $onTertiaryFixed
cs.onTertiaryFixedVariant   // $onTertiaryFixedVariant

// Error
cs.error                    // $error
cs.onError                  // $onError
cs.errorContainer           // $errorContainer
cs.onErrorContainer         // $onErrorContainer

// Surface — 계층별 선택
cs.surface                  // $surface (기본)
cs.surfaceDim               // $surfaceDim (어두운 surface)
cs.surfaceBright            // $surfaceBright (밝은 surface)
cs.surfaceContainerLowest   // $surfaceContainerLowest
cs.surfaceContainerLow      // $surfaceContainerLow
cs.surfaceContainer         // $surfaceContainer
cs.surfaceContainerHigh     // $surfaceContainerHigh
cs.surfaceContainerHighest  // $surfaceContainerHighest
cs.onSurface                // $onSurface
cs.onSurfaceVariant         // $onSurfaceVariant

// Outline
cs.outline                  // $outline
cs.outlineVariant           // $outlineVariant

// Inverse / Utility
cs.inverseSurface           // $inverseSurface
cs.onInverseSurface         // $onInverseSurface
cs.inversePrimary           // $inversePrimary
cs.shadow                   // $shadow
cs.scrim                    // $scrim
cs.surfaceTint              // $surfaceTint
```

---

## Pencil 토큰 → Flutter 코드 매핑

> `material-design-guide.lib.pen` 에 실제 정의된 M3 ColorScheme 토큰 기준.

### Primary

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$primary` | `colorScheme.primary` |
| `$onPrimary` | `colorScheme.onPrimary` |
| `$primaryContainer` | `colorScheme.primaryContainer` |
| `$onPrimaryContainer` | `colorScheme.onPrimaryContainer` |
| `$primaryFixed` | `colorScheme.primaryFixed` |
| `$primaryFixedDim` | `colorScheme.primaryFixedDim` |
| `$onPrimaryFixed` | `colorScheme.onPrimaryFixed` |
| `$onPrimaryFixedVariant` | `colorScheme.onPrimaryFixedVariant` |

### Secondary

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$secondary` | `colorScheme.secondary` |
| `$onSecondary` | `colorScheme.onSecondary` |
| `$secondaryContainer` | `colorScheme.secondaryContainer` |
| `$onSecondaryContainer` | `colorScheme.onSecondaryContainer` |
| `$secondaryFixed` | `colorScheme.secondaryFixed` |
| `$secondaryFixedDim` | `colorScheme.secondaryFixedDim` |
| `$onSecondaryFixed` | `colorScheme.onSecondaryFixed` |
| `$onSecondaryFixedVariant` | `colorScheme.onSecondaryFixedVariant` |

### Tertiary

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$tertiary` | `colorScheme.tertiary` |
| `$onTertiary` | `colorScheme.onTertiary` |
| `$tertiaryContainer` | `colorScheme.tertiaryContainer` |
| `$onTertiaryContainer` | `colorScheme.onTertiaryContainer` |
| `$tertiaryFixed` | `colorScheme.tertiaryFixed` |
| `$tertiaryFixedDim` | `colorScheme.tertiaryFixedDim` |
| `$onTertiaryFixed` | `colorScheme.onTertiaryFixed` |
| `$onTertiaryFixedVariant` | `colorScheme.onTertiaryFixedVariant` |

### Error

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$error` | `colorScheme.error` |
| `$onError` | `colorScheme.onError` |
| `$errorContainer` | `colorScheme.errorContainer` |
| `$onErrorContainer` | `colorScheme.onErrorContainer` |

### Surface

| Pencil 토큰 | Flutter 접근법 | 비고 |
|------------|--------------|------|
| `$surface` | `colorScheme.surface` | |
| `$onSurface` | `colorScheme.onSurface` | |
| `$surfaceDim` | `colorScheme.surfaceDim` | surface보다 어두움 |
| `$surfaceBright` | `colorScheme.surfaceBright` | surface보다 밝음 |
| `$surfaceContainerLowest` | `colorScheme.surfaceContainerLowest` | |
| `$surfaceContainerLow` | `colorScheme.surfaceContainerLow` | |
| `$surfaceContainer` | `colorScheme.surfaceContainer` | |
| `$surfaceContainerHigh` | `colorScheme.surfaceContainerHigh` | |
| `$surfaceContainerHighest` | `colorScheme.surfaceContainerHighest` | |
| `$onSurfaceVariant` | `colorScheme.onSurfaceVariant` | |

### Outline

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$outline` | `colorScheme.outline` |
| `$outlineVariant` | `colorScheme.outlineVariant` |

### Inverse / Utility

| Pencil 토큰 | Flutter 접근법 |
|------------|--------------|
| `$inverseSurface` | `colorScheme.inverseSurface` |
| `$inverseOnSurface` | `colorScheme.onInverseSurface` |
| `$inversePrimary` | `colorScheme.inversePrimary` |
| `$shadow` | `colorScheme.shadow` |
| `$scrim` | `colorScheme.scrim` |
| `$surfaceTint` | `colorScheme.surfaceTint` |

> `$primary/40` → `AppColors.primary40` (Layer 1, 직접 참조 금지)

---

## Pencil 프롬프트 — Flutter Material Colors Palette

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Flutter Material Colors Palette" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 팔레트 토큰 참조 ($grey:50~$grey:900 등)

참고: https://m3.material.io/styles/color/the-color-system/key-colors-tones

---

## 프레임 설정
- 이름: "Flutter Material Colors Palette"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 24px, 좌우 패딩 40px

---

## 색조 목록 (19개, 수직 나열)

각 색조 행 구조:
- 라벨 텍스트 (색조명, 14px, On-Surface)
- 색상 칩 가로 나열 (10단계: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900), 각 칩 48×48dp
- Accent 칩 가로 나열 (있는 경우: 100, 200, 400, 700), 각 칩 48×48dp

색조 목록:
Red / Pink / Purple / Deep Purple / Indigo / Blue / Light Blue / Cyan / Teal / Green / Light Green / Lime / Yellow / Amber / Orange / Deep Orange / Brown / Grey / Blue Grey

각 칩:
- 배경: 해당 팔레트 색상
- 텍스트: 단계 숫자 (11px, 어두운 칩은 흰색, 밝은 칩은 검정)

---

## Pencil 프롬프트 — Semantic Color Palette

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Semantic Color Palette" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 팔레트 토큰 참조 ($primary/0~$primary/100 등)

참고: https://m3.material.io/styles/color/the-color-system/key-colors-tones

---

## 프레임 설정
- 이름: "Semantic Color Palette"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 32px, 좌우 패딩 40px

---

## 섹션 1 — Seed Color
- 색상 칩 (48×48dp) + 라벨 "Seed Color" + hex값 텍스트
- 칩 배경: $seed

---

## 섹션 2 — 팔레트 그룹 (6개)

그룹: Primary / Secondary / Tertiary / Error / Neutral / Neutral Variant

각 그룹 구조:
- 그룹 라벨 (16px, 600, On-Surface)
- 색상 칩 가로 나열 (13단계: 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100), 각 칩 48×48dp
- 칩 배경: 해당 팔레트 토큰 ($primary/0, $primary/10, ...)
- 칩 텍스트: 단계 숫자 (11px, 어두운 칩은 흰색, 밝은 칩은 검정)

---

## Pencil 프롬프트 — Material Color Scheme

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Material Color Scheme" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface 등)

참고: https://m3.material.io/styles/color/roles

---

## 프레임 설정
- 이름: "Material Color Scheme"
- 배경: Surface
- 레이아웃: 수직, 좌우 패딩 40px

---

## 헤더 행
- 배경: Surface Container Highest
- 7개 열: Token / light / dark / light-mc / dark-mc / light-hc / dark-hc
- 텍스트: 12px, On-Surface

---

## 토큰 행 (46개 + 구분선 5개)

각 행: 토큰명 텍스트 + 6개 색상 칩 (테마별)

**Primary 그룹 (8행)**
primary / onPrimary / primaryContainer / onPrimaryContainer /
primaryFixed / primaryFixedDim / onPrimaryFixed / onPrimaryFixedVariant

구분선 (8dp)

**Secondary 그룹 (8행)**
secondary / onSecondary / secondaryContainer / onSecondaryContainer /
secondaryFixed / secondaryFixedDim / onSecondaryFixed / onSecondaryFixedVariant

구분선

**Tertiary 그룹 (8행)**
tertiary / onTertiary / tertiaryContainer / onTertiaryContainer /
tertiaryFixed / tertiaryFixedDim / onTertiaryFixed / onTertiaryFixedVariant

구분선

**Error 그룹 (4행)**
error / onError / errorContainer / onErrorContainer

구분선

**Surface 그룹 (11행)**
surface / onSurface / onSurfaceVariant / outline / outlineVariant /
inverseSurface / inverseOnSurface / inversePrimary / shadow / scrim / surfaceTint

구분선

**Surface Container 그룹 (7행)**
surfaceDim / surfaceBright / surfaceContainerLowest / surfaceContainerLow /
surfaceContainer / surfaceContainerHigh / surfaceContainerHighest

각 칩 (40×32dp):
- 배경: 해당 테마의 토큰 색상
- 텍스트 없음

---

## Pencil 프롬프트 — Color System Guide

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Color System Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/styles/color/overview

---

## 프레임 설정
- 이름: "Color System Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Color System"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · 3-Layer Color Architecture"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/styles/color/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — 3-Layer Architecture
- 소제목: "3-Layer Architecture"  (20px, 600)
- 3개 박스 수직 연결 (화살표로 연결):

  ┌─ Layer 1 — Material Color Palette ─────────────┐
  │  AppColors.primary40, AppColors.neutral99 ...   │
  │  원시 hex 값. UI에 직접 쓰지 않는다.             │
  │  bg: Surface Container                           │
  └──────────────────↓──────────────────────────────┘

  ┌─ Layer 2 — Semantic Colors ─────────────────────┐
  │  AppSemanticColors.brandPrimary = primary40     │
  │  역할 이름 부여. ThemeData에 연결한다.            │
  │  bg: Secondary Container                         │
  └──────────────────↓──────────────────────────────┘

  ┌─ Layer 3 — Color Scheme (실제 사용) ────────────┐
  │  Theme.of(context).colorScheme.primary          │
  │  위젯에서 항상 colorScheme으로 접근한다.          │
  │  bg: Primary Container                           │
  └─────────────────────────────────────────────────┘

---

## 섹션 3 — Color Roles
- 소제목: "Color Roles"  (20px, 600)
- 색상 칩 그리드 (4열), 각 칩 80×48dp:

  행 1:  Primary / On-Primary / Primary Container / On-Primary Container
  행 2:  Primary Fixed / Primary Fixed Dim / On-Primary Fixed / On-Primary Fixed Variant
  행 3:  Secondary / On-Secondary / Secondary Container / On-Secondary Container
  행 4:  Secondary Fixed / Secondary Fixed Dim / On-Secondary Fixed / On-Secondary Fixed Variant
  행 5:  Tertiary / On-Tertiary / Tertiary Container / On-Tertiary Container
  행 6:  Tertiary Fixed / Tertiary Fixed Dim / On-Tertiary Fixed / On-Tertiary Fixed Variant
  행 7:  Error / On-Error / Error Container / On-Error Container
  행 8:  Surface / On-Surface / Surface Dim / Surface Bright
  행 9:  Surface Container Lowest / Surface Container Low / Surface Container / Surface Container High
  행 10: Surface Container Highest / On-Surface-Variant / Outline / Outline Variant
  행 11: Inverse Surface / On-Inverse Surface / Inverse Primary / Surface Tint
  행 12: Shadow / Scrim / — / —

  각 칩:
  - 배경: 해당 색상 토큰
  - 텍스트: On 색상 토큰  (12px)
  - 텍스트 내용: 토큰명

---

## 섹션 4 — Flutter 사용법
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // MaterialApp 세팅
  MaterialApp(
    theme: AppTheme.light,
    darkTheme: AppTheme.dark,
    themeMode: ThemeMode.system,
  )

  // 위젯에서 색상 접근
  final cs = Theme.of(context).colorScheme;
  Container(color: cs.primary)
  Text('Hello', style: TextStyle(color: cs.onSurface))
  Card(color: cs.surfaceContainerHighest)
