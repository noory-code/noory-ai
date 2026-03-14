# Elevation

## M3 링크

| 페이지 | URL |
|--------|-----|
| Elevation | https://m3.material.io/styles/elevation/overview |
| Tonal Color | https://m3.material.io/styles/elevation/applying-elevation |

## 토큰 정의 (M3 Elevation 5단계)

| 토큰 | 값 | M3 레벨 | 주요 컴포넌트 |
|------|-----|---------|--------------|
| $elevation/0 | 0 dp | Level 0 | 기본 Surface (배경) |
| $elevation/1 | 1 dp | Level 1 | Card, NavigationDrawer |
| $elevation/2 | 3 dp | Level 2 | FAB, Chip (선택), DropdownMenu |
| $elevation/3 | 6 dp | Level 3 | FAB (pressed), NavigationBar |
| $elevation/4 | 8 dp | Level 4 | Dialog 뒤 Scrim |
| $elevation/5 | 12 dp | Level 5 | Dialog, BottomSheet, ModalSheet |

> M3 Elevation은 Shadow + Tonal Surface Overlay (Primary 색상을 불투명도로 표현)를 동시에 사용.

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Elevation Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/styles/elevation/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다:

| 변수명 | 값 |
|--------|-----|
| $elevation/level0 | 0 |
| $elevation/level1 | 1 |
| $elevation/level2 | 3 |
| $elevation/level3 | 6 |
| $elevation/level4 | 8 |
| $elevation/level5 | 12 |

---

## 프레임 설정
- 이름: "Elevation Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Elevation"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · Shadow + Tonal Overlay"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/styles/elevation/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · Level 0 — 배경 Surface (Scaffold 배경)
  · Level 1 — 카드, NavigationDrawer (살짝 떠오른 느낌)
  · Level 2 — FAB, 드롭다운 메뉴, 선택된 칩
  · Level 3 — NavigationBar, 누른 FAB
  · Level 4 — Dialog 뒤 스크림 처리 영역
  · Level 5 — Dialog, BottomSheet, Modal

---

## 섹션 3 — Level Scale
- 소제목: "Level Scale"  (20px, 600)
- 설명: "M3 Elevation = Shadow dp + Primary Tonal Overlay"  (14px, On-Surface-Variant)
- 6개 카드 가로 나열 (2열×3행), 카드 크기 120×120dp:

  각 카드:
  - 배경: Surface Container (점점 밝아지는 Tonal Overlay 표현)
  - 그림자: 레벨에 해당하는 dp shadow (Pencil shadow 기능 사용)
  - 중앙 텍스트: "Level N"  (14px, bold, On-Surface)
  - 하단 텍스트: "Ndp"  (12px, On-Surface-Variant)

  · Level 0 — 0dp, 그림자 없음
  · Level 1 — 1dp
  · Level 2 — 3dp
  · Level 3 — 6dp
  · Level 4 — 8dp
  · Level 5 — 12dp

---

## 섹션 4 — Tonal Overlay 설명
- 소제목: "Tonal Surface Overlay"  (20px, 600)
- 설명 박스 (background: Surface Container, radius 12dp, padding 16dp):
  "M3는 그림자만으로 Elevation을 표현하지 않습니다.
  Primary 색상의 Overlay(투명도)를 Surface에 적용하여
  더 높은 Elevation일수록 Primary가 더 많이 섞입니다.
  → Surface + Primary Tonal Overlay = Elevated Surface"

---

## 섹션 5 — Component Mapping
- 소제목: "Component Mapping"  (20px, 600)
- 테이블:
  | 레벨 | Shadow | 컴포넌트 |
  |------|--------|---------|
  | Level 0 | 0 dp | Scaffold, Surface |
  | Level 1 | 1 dp | Card (default), NavigationDrawer |
  | Level 2 | 3 dp | FAB (resting), DropdownMenu, Chip (선택) |
  | Level 3 | 6 dp | FAB (hover), NavigationBar |
  | Level 4 | 8 dp | — (Scrim 영역) |
  | Level 5 | 12 dp | Dialog, BottomSheet, Modal |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppElevation 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // Card
  Card(
    elevation: AppElevation.level1,  // 1dp
    color: Theme.of(context).colorScheme.surface,
    child: ...,
  )

  // FAB
  FloatingActionButton(
    elevation: AppElevation.level2,  // 3dp resting (pressed는 M3가 자동 처리)
    child: Icon(Icons.add),
  )

  // Dialog
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      elevation: AppElevation.level5, // 12dp
      backgroundColor: Theme.of(context).colorScheme.surface,
    ),
  )

  // Material widget
  Material(
    elevation: AppElevation.level3, // 6dp
    color: Theme.of(context).colorScheme.surface,
    child: ...,
  )
