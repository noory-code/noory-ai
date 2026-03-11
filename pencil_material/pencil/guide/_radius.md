# Border Radius

## M3 링크

| 페이지 | URL |
|--------|-----|
| Shape | https://m3.material.io/styles/shape/overview |
| Shape Scale | https://m3.material.io/styles/shape/shape-scale-tokens |

## 토큰 정의 (M3 Shape Scale)

| 토큰 | 값 | M3 Shape 역할 |
|------|-----|--------------|
| $radius/none | 0 dp | shape/none — 직각 (DataTable 등) |
| $radius/xs | 8 dp | shape/extra-small — 작은 칩, 입력 필드 |
| $radius/sm | 12 dp | shape/small — 카드 소형, 메뉴 |
| $radius/md | 16 dp | shape/medium — 카드, Dialog |
| $radius/lg | 20 dp | shape/large — BottomSheet, Drawer |
| $radius/xl | 28 dp | shape/extra-large — FAB, 대형 카드 |
| $radius/full | 9999 dp | shape/full — pill 형태 (버튼, Chip, FAB extended) |

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Border Radius Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/styles/shape/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다. 이미 등록되어 있다면 값을 확인하고 아래와 다르면 수정한다:

| 변수명 | 값 |
|--------|-----|
| $radius/none | 0 |
| $radius/xs | 8 |
| $radius/sm | 12 |
| $radius/md | 16 |
| $radius/lg | 20 |
| $radius/xl | 28 |
| $radius/full | 9999 |

---

## 프레임 설정
- 이름: "Border Radius Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Border Radius"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · Shape Scale"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/styles/shape/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · none (0dp) — DataTable, 이미지 썸네일 직각
  · xs (8dp) — 작은 칩, 툴팁, 입력 필드
  · sm (12dp) — 소형 카드, 메뉴, 스낵바
  · md (16dp) — 카드, Dialog, 알림
  · lg (20dp) — BottomSheet, 사이드 Drawer
  · xl (28dp) — FAB, 대형 카드
  · full (pill) — 버튼, Chip, Extended FAB

---

## 섹션 3 — Shape Scale
- 소제목: "Shape Scale"  (20px, 600)
- 7개 사각형 가로 나열, gap 16px:
  각 사각형 크기 80×80dp

  ┌─ none ──┐   ┌─ xs ────┐   ┌─ sm ────┐   ┌─ md ────┐
  │ 0dp     │   │ r=8dp   │   │ r=12dp  │   │ r=16dp  │
  │ bg:     │   │ bg:     │   │ bg:     │   │ bg:     │
  │ Primary │   │ Primary │   │ Primary │   │ Primary │
  │ Container│  │ Container│  │ Container│  │ Container│
  └─────────┘   └─────────┘   └─────────┘   └─────────┘

  ┌─ lg ────┐   ┌─ xl ────┐   ┌─── full ────────────────┐
  │ r=20dp  │   │ r=28dp  │   │      pill shape          │
  │ bg:     │   │ bg:     │   │   bg: Primary Container  │
  │ Primary │   │ Primary │   └─────────────────────────┘
  │ Container│  │ Container│
  └─────────┘   └─────────┘

  full은 80×32dp 가로 pill 형태로 표현 (radius=9999)
  각 사각형 아래: 토큰명 (12px, On-Surface-Variant) + 값 (12px, Primary)

---

## 섹션 4 — Component Mapping
- 소제목: "Component Mapping"  (20px, 600)
- 테이블:
  | Shape | 값 | 컴포넌트 |
  |-------|-----|---------|
  | none | 0 dp | DataTable, ImageTile |
  | extra-small | 8 dp | Chip (소형), Tooltip |
  | small | 12 dp | Card (소형), Menu, Snackbar |
  | medium | 16 dp | Card, Dialog, Alert |
  | large | 20 dp | BottomSheet, NavigationDrawer |
  | extra-large | 28 dp | FAB, LargeCard |
  | full | pill | Button, Chip, ExtendedFAB |

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 토큰 | 값 | M3 Shape Token |
  |------|-----|----------------|
  | $radius/none | 0 dp | shape.none |
  | $radius/xs | 8 dp | shape.extra-small |
  | $radius/sm | 12 dp | shape.small |
  | $radius/md | 16 dp | shape.medium |
  | $radius/lg | 20 dp | shape.large |
  | $radius/xl | 28 dp | shape.extra-large |
  | $radius/full | 9999 dp | shape.full (pill) |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppRadius 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // BorderRadius
  BorderRadius.circular(AppRadius.none)  // 0dp
  BorderRadius.circular(AppRadius.xs)    // 8dp
  BorderRadius.circular(AppRadius.sm)    // 12dp
  BorderRadius.circular(AppRadius.md)    // 16dp
  BorderRadius.circular(AppRadius.lg)    // 20dp
  BorderRadius.circular(AppRadius.xl)    // 28dp
  BorderRadius.circular(AppRadius.full)  // pill (9999dp)

  // BoxDecoration with colorScheme
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(AppRadius.md), // Card
    color: Theme.of(context).colorScheme.primaryContainer,
  )

  // RoundedRectangleBorder (버튼, FAB)
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.full), // Button — pill
  )

