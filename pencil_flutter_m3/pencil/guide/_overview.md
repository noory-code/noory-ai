# Overview — flutter_design Guide

## 이 폴더의 파일 구성

### 토큰 / 시스템 가이드 (`_` 접두사)

| 파일 | 내용 |
|------|------|
| `_colors.md` | Color System — 3-레이어 아키텍처, ColorScheme 사용법 |
| `_typography.md` | Typography — M3 Type Scale 15개 스타일 |
| `_spacing.md` | Spacing — 8dp 그리드 토큰 |
| `_radius.md` | Border Radius — M3 Shape Scale |
| `_elevation.md` | Elevation — 5단계 + Tonal Overlay |
| `_icon-size.md` | Icon Size — 5단계 크기 토큰 |
| `_opacity.md` | Opacity — State Layer Opacity |
| `_thickness.md` | Thickness — Border / Divider 두께 토큰 |

### 컴포넌트 가이드 (31개)

| 파일 | 컴포넌트 |
|------|---------|
| `badge.md` | Badge |
| `bottom-app-bar.md` | Bottom App Bar |
| `bottom-sheets.md` | Bottom Sheet |
| `buttons.md` | Filled / Outlined / Text / Elevated Button |
| `cards.md` | Card |
| `carousel.md` | Carousel |
| `checkbox.md` | Checkbox |
| `chips.md` | Chip |
| `date-pickers.md` | Date Picker |
| `dialogs.md` | Dialog |
| `divider.md` | Divider |
| `fab.md` | Floating Action Button |
| `icon-buttons.md` | Icon Button |
| `lists.md` | List / ListTile |
| `menus.md` | Menu |
| `navigation-bar.md` | Navigation Bar |
| `navigation-drawer.md` | Navigation Drawer |
| `navigation-rail.md` | Navigation Rail |
| `progress-indicators.md` | Progress Indicator |
| `radio-button.md` | Radio Button |
| `search.md` | Search Bar |
| `segmented-buttons.md` | Segmented Button |
| `side-sheets.md` | Side Sheet |
| `sliders.md` | Slider |
| `snackbar.md` | Snackbar |
| `switch.md` | Switch |
| `tabs.md` | Tab Bar |
| `text-fields.md` | Text Field |
| `time-pickers.md` | Time Picker |
| `tooltips.md` | Tooltip |
| `top-app-bar.md` | Top App Bar |

---

## Pencil 가이드 사용법

### Step 1 — 라이브러리 로드

Pencil 앱에서 `material-design-guide.lib.pen` 을 라이브러리로 추가.
이 라이브러리에는 M3 Color Scheme 토큰 (`$primary`, `$surface` 등)과 Typography 토큰이 정의되어 있다.

### Step 2 — 프롬프트 복사

가이드 파일에서 **"Pencil 프롬프트"** 섹션의 내용을 복사한다.

### Step 3 — Pencil AI 실행

Pencil AI 패널에 복사한 프롬프트를 붙여넣기 → 가이드 프레임 자동 생성.

---

## Flutter 코드 연동

각 가이드 파일의 **"Flutter Usage"** 섹션 참조.

```dart
import 'package:flutter_design/flutter_design.dart';

// 색상
final cs = Theme.of(context).colorScheme;

// 타이포
final tt = Theme.of(context).textTheme;

// 토큰
AppSpacing.base      // 16dp
AppRadius.md         // 12dp
AppElevation.level1  // 1dp
AppIconSize.md       // 24dp
AppOpacity.hover     // 0.08
```

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 Overview 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Design Guide — Overview" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

---

## 프레임 설정
- 이름: "Design Guide — Overview"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "flutter_design Guide"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · 디자인 시스템 + Pencil 가이드"  (14px, On-Surface-Variant)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — 사용 흐름
- 소제목: "How to use"  (20px, 600)
- 3개 스텝 수평 나열, gap 24px, 각 스텝 카드 (bg: Surface Container, radius 12dp, padding 20dp):

  ┌─ Step 1 ──────────────┐
  │  라이브러리 로드       │
  │  material-design-      │
  │  guide.lib.pen         │
  │  Pencil에 추가         │
  └────────────────────────┘

  ┌─ Step 2 ──────────────┐
  │  프롬프트 복사         │
  │  guide/*.md 파일의     │
  │  "Pencil 프롬프트"     │
  │  섹션 복사             │
  └────────────────────────┘

  ┌─ Step 3 ──────────────┐
  │  Pencil AI 실행        │
  │  AI 패널에 붙여넣기    │
  │  → 프레임 자동 생성    │
  └────────────────────────┘

---

## 섹션 3 — 토큰 시스템 가이드
- 소제목: "Token & System Guides"  (20px, 600)
- 8개 항목 2열 그리드, 각 카드 (bg: Surface Container, radius 8dp, padding 16dp):

  · Colors — Color System 3-레이어
  · Typography — M3 Type Scale
  · Spacing — 8dp 그리드
  · Border Radius — Shape Scale
  · Elevation — 5단계
  · Icon Size — 5단계 크기
  · Opacity — State Layer
  · Thickness — Border / Divider 두께

---

## 섹션 4 — Flutter 연동
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  import 'package:flutter_design/flutter_design.dart';

  // MaterialApp 세팅
  MaterialApp(
    theme:     AppTheme.light,
    darkTheme: AppTheme.dark,
  )

  // 색상 / 타이포
  final cs = Theme.of(context).colorScheme;
  final tt = Theme.of(context).textTheme;

  // 토큰
  AppSpacing.base      // 16dp
  AppRadius.md         // 12dp
  AppElevation.level1  // 1dp
  AppIconSize.md       // 24dp
  AppOpacity.hover     // 0.08
