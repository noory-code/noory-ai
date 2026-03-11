# pencil_material

## Introduction

Material Design 3 디자인 시스템 패키지입니다.
이 프로젝트는 pencil.dev를 사용하여 고유의 디자인 시스템을 구축하기 위한 시작점으로 활용될 수 있습니다.

`SemanticColorPalette` → `ThemeColors` → `AppTheme` 3-레이어 컬러 아키텍처 +
Design Tokens(Spacing/Radius/Elevation/Icon/Opacity) + Pencil 가이드.

---

## 패키지 구조

```
lib/src/
├── semantic_color_palette.dart  # Layer 1 — M3 팔레트 원시값 (78개 상수 + seed)
├── theme_colors.dart            # Layer 2 — 6개 variant 색상 역할 (ThemeColors)
├── theme.dart                   # Layer 3 — ThemeData 6개 variant (AppTheme)
└── tokens.dart                  # Design Tokens (AppSpacing/AppRadius/AppElevation/AppIconSize/AppOpacity)

pencil/
├── material-design-guide.lib.pen  # Pencil 디자인 라이브러리
└── guide/                         # 컴포넌트·토큰별 Pencil 프롬프트 + Flutter 사용법
    ├── _overview.md               # 전체 가이드 사용법 (여기서 시작)
    ├── _colors.md                 # Color System
    ├── _typography.md             # Typography
    ├── _spacing.md / _radius.md / _elevation.md / _icon-size.md / _opacity.md
    └── buttons.md · cards.md · ... (31개 컴포넌트)
```

---

## 시작하기 (Getting Started)

### 1. 패키지 복사

이 패키지는 오픈소스로 제공되므로, 직접 수정하고 확장해서 사용하는 것을 권장합니다. Melos와 같은 Flutter 모노레포 환경에 `flutter_design` 패키지 디렉토리 전체를 복사하여 사용하세요.

### 2. 의존성 추가

이 패키지를 사용하려는 앱의 `pubspec.yaml` 파일에 아래와 같이 path dependency를 추가합니다.

```yaml
# pubspec.yaml
dependencies:
  flutter_design:
    path: ../flutter_design # Monorepo 내의 상대 경로에 맞춰 수정
```

---

## 기본 사용법 (Basic Usage)

### 1. MaterialApp 세팅

```dart
import 'package:flutter_design/flutter_design.dart';

MaterialApp(
  theme:                  AppTheme.light,
  darkTheme:              AppTheme.dark,
  highContrastTheme:      AppTheme.lightHc,
  highContrastDarkTheme:  AppTheme.darkHc,
  themeMode: ThemeMode.system,
)
```

### 2. 위젯에서 색상 접근

```dart
final cs = Theme.of(context).colorScheme;

cs.primary              // 브랜드 컬러
cs.surface              // 배경 Surface
cs.onSurface            // Surface 위 텍스트
cs.surfaceContainerHighest  // Surface Variant
cs.error                // 오류 색상
cs.outline              // 테두리
```

### 3. Design Token 사용

```dart
// Spacing
padding: EdgeInsets.all(AppSpacing.base)                   // 16dp
padding: EdgeInsets.symmetric(horizontal: AppSpacing.xl)   // 24dp
SizedBox(height: AppSpacing.sm)                            // 8dp

// Radius
BorderRadius.circular(AppRadius.md)    // 12dp — Card
BorderRadius.circular(AppRadius.full)  // 28dp — Button, Chip

// Elevation
Card(elevation: AppElevation.level1)                // 1dp
FloatingActionButton(elevation: AppElevation.level2) // 3dp

// Icon Size
Icon(Icons.home, size: AppIconSize.md)  // 24dp (기본값)
Icon(Icons.inbox, size: AppIconSize.xl) // 48dp (Empty State)

// Opacity (State Layer)
color.withValues(alpha: AppOpacity.hover)    // 0.08
color.withValues(alpha: AppOpacity.pressed)  // 0.12
```

### 4. Typography

```dart
final tt = Theme.of(context).textTheme;

Text('페이지 제목', style: tt.headlineLarge)   // 32sp, w400
Text('카드 제목',   style: tt.titleMedium)     // 16sp, w500
Text('본문',        style: tt.bodyMedium)       // 14sp, w400
Text('캡션',        style: tt.labelSmall)       // 11sp, w500
```

---

## 컬러 스킴 변경하기 (프롬프트 기반 워크플로우)

`flutter_design`의 컬러 스킴은 `pencil.dev`와 IDE의 AI 에이전트(Gemini, Claude Code 등) 간의 프롬프트를 통해 완벽하게 동기화됩니다. 수동으로 값을 복사하여 붙여넣을 필요가 없습니다.

### Step 1: `pencil.dev`에서 프롬프트로 색상 팔레트 변경

먼저, `pencil.dev` 환경에서 디자인 시스템의 원본인 `material-design-guide.lib.pen` 파일의 색상을 변경합니다. 아래와 같은 프롬프트를 사용하세요.

> **Pencil.dev 프롬프트 예시:**
> "In the Material Design Guide, please change the seed color to `blue` and regenerate the entire color palette."

이 명령은 `pencil.dev`가 새로운 시드 색상을 기반으로 전체 Material Color Scheme (Primary, Secondary, Neutral 등)을 다시 계산하고 업데이트하도록 합니다.

### Step 2: IDE에서 프롬프트로 Flutter 코드 동기화

`pencil.dev`에서 색상 변경이 완료되면, 사용 중인 IDE(예: Gemini가 통합된 VSCode)로 돌아와 AI 에이전트에게 다음과 같이 프롬프트를 입력하여 Flutter 코드를 업데이트합니다.

> **IDE (Gemini/Claude) 프롬프트 예시:**
> "The color scheme in 'material-design-guide.lib.pen' has been updated. Please sync the `packages/flutter_design/lib/src/semantic_color_palette.dart` file with the new values."

이 명령을 받은 AI 에이전트는 `pencil.dev`의 변경된 색상 값들을 가져와 `semantic_color_palette.dart` 파일의 모든 관련 상수들을 자동으로 업데이트하여, 디자인과 코드를 완벽하게 일치시킵니다.

---

## 6개 Theme Variant

| Getter | 용도 |
|--------|------|
| `AppTheme.light`   | 기본 라이트 |
| `AppTheme.dark`    | 기본 다크 |
| `AppTheme.lightMc` | Medium Contrast 라이트 |
| `AppTheme.darkMc`  | Medium Contrast 다크 |
| `AppTheme.lightHc` | High Contrast 라이트 (`highContrastTheme`) |
| `AppTheme.darkHc`  | High Contrast 다크 (`highContrastDarkTheme`) |

---

## 3-레이어 컬러 아키텍처

```
Layer 1 — SemanticColorPalette   (raw hex)
  primary0~100, secondary, tertiary, neutral, neutralVariant, error
  → UI에서 직접 사용 금지

       ↓ 역할 부여

Layer 2 — ThemeColors / _ThemeColorSet   (named roles per variant)
  light.primary = primary40
  dark.primary  = primary80
  → ThemeColors.lightScheme, darkScheme, ...

       ↓ 테마 적용

Layer 3 — AppTheme   (ThemeData)
  MaterialApp(theme: AppTheme.light)
  → 위젯에서 Theme.of(context).colorScheme.primary
```

---

## Pencil 가이드 사용법

`pencil/guide/_overview.md` 참조.
