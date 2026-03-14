# Bottom App Bar

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/bottom-app-bar/overview |
| Guidelines | https://m3.material.io/components/bottom-app-bar/guidelines |
| Specs | https://m3.material.io/components/bottom-app-bar/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Standard | `BottomAppBar` |
| With FAB | `BottomAppBar` + `FloatingActionButton` |

## 언제 사용하나요?

- 화면 하단에 주요 액션과 보조 아이콘을 배치할 때
- `FloatingActionButton`과 함께 핵심 액션을 강조할 때
- 모바일(compact) 화면에서 최대 4개의 아이콘 액션을 제공할 때
- `Scaffold.bottomNavigationBar`에 배치해 하단 고정 영역으로 사용할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Bottom App Bar 사용 |
| Tablet (medium) | 필요 시 유지, 또는 Top App Bar로 액션 이동 고려 |
| Desktop/Web (expanded) | 사용 지양 — 액션을 Top App Bar 또는 사이드 패널로 이동 |

## Variants

- **Standard** — 아이콘 버튼만 나열
- **With FAB** — FAB 포함, end-anchored 배치

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Bottom App Bar Guide" 프레임을 만들어주세요.
모든 내용은 이 "Bottom App Bar Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/bottom-app-bar/overview

---

## 프레임 설정
- 이름: "Bottom App Bar Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Bottom App Bar"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · bottom-app-bar"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/bottom-app-bar/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 화면 하단에 주요 액션과 보조 아이콘을 배치할 때
  · FloatingActionButton과 함께 핵심 액션을 강조할 때
  · 모바일에서 최대 4개의 아이콘 액션을 제공할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Standard ─────────────────────────┐
  │  너비: 360dp, 높이: 80dp            │
  │  배경: Surface (Surface)            │
  │  좌측에 아이콘 4개 가로 나열         │
  │  각 아이콘: 24×24dp, On-Surface-Variant        │
  │  아이콘 간격: 8dp, 좌패딩: 16dp      │
  │  레이블: "Standard"                │
  └────────────────────────────────────┘

  ┌─ With FAB ─────────────────────────┐
  │  너비: 360dp, 높이: 80dp            │
  │  배경: Surface (Surface)            │
  │  좌측에 아이콘 3개 나열             │
  │  우측에 FAB: 56×56dp, Primary      │
  │  FAB 아이콘: + (white, 24dp)        │
  │  FAB corner radius: 16dp           │
  │  레이블: "With FAB"               │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Standard Bottom App Bar를 크게 그리고 번호 레이블 연결:
  1. Container — 전체 너비, height 80dp, surfaceContainer 배경
  2. Action icon — 24×24dp, onSurfaceVariant 색상
  3. FAB (선택) — 56×56dp, primaryContainer 배경, corner 16dp
  4. Top edge — 1dp divider, outlineVariant

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성             | 값                      | 토큰                              |
  |-----------------|-------------------------|-----------------------------------|
  | Height          | 80 dp                   | —                                 |
  | Icon size       | 24 dp                   | AppIconSize.md                    |
  | FAB size        | 56 × 56 dp              | —                                 |
  | FAB corner      | 16 dp                   | —                                 |
  | Horizontal pad  | 16 dp                   | AppSpacing.base                   |
  | Icon spacing    | 8 dp                    | —                                 |
  | Container bg    | surfaceContainer        | colorScheme.surfaceContainer      |
  | Icon color      | onSurfaceVariant        | colorScheme.onSurfaceVariant      |
  | FAB bg          | primaryContainer        | colorScheme.primaryContainer      |
  | FAB icon color  | onPrimaryContainer      | colorScheme.onPrimaryContainer    |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Bottom App Bar 사용        │
  │  → BottomAppBar            │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  유지 또는 Top App Bar 이동  │
  │  → BottomAppBar (선택)      │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  사용 지양, 사이드 패널로 이동│
  │  → NavigationDrawer 사용   │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Bottom App Bar Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  BottomAppBar/Default — FAB 없음:
  · 컴포넌트 이름: "BottomAppBar/Default"
  · 크기: 360×80dp
  · 배경: Surface Container
  · 아이콘 4개 (24dp, On-Surface-Variant) 좌측 나열, 수평 패딩 16dp, 간격 8dp

  BottomAppBar/WithFAB — FAB 포함:
  · 컴포넌트 이름: "BottomAppBar/WithFAB"
  · 크기: 360×80dp
  · 배경: Surface Container
  · 아이콘 3개 좌측, FAB (56×56dp, Primary Container, corner 16dp) 우측 끝


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  Scaffold(
    bottomNavigationBar: BottomAppBar(
      child: Row(children: [
        IconButton(icon: Icon(Icons.menu), onPressed: () {}),
        IconButton(icon: Icon(Icons.search), onPressed: () {}),
      ]),
    ),
    floatingActionButton: FloatingActionButton(
      onPressed: () {},
      child: Icon(Icons.add),
    ),
    floatingActionButtonLocation:
      FloatingActionButtonLocation.endContained,
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

Scaffold(
  bottomNavigationBar: BottomAppBar(
    color: cs.surfaceContainer,
    elevation: AppElevation.level0,
    padding: EdgeInsets.symmetric(horizontal: AppSpacing.base), // 16dp
    child: Row(
      children: [
        IconButton(
          icon: Icon(Icons.menu, size: AppIconSize.md), // 24dp
          color: cs.onSurfaceVariant,
          onPressed: () {},
        ),
        IconButton(
          icon: Icon(Icons.search, size: AppIconSize.md), // 24dp
          color: cs.onSurfaceVariant,
          onPressed: () {},
        ),
        const Spacer(),
      ],
    ),
  ),
  floatingActionButton: FloatingActionButton(
    onPressed: () {},
    child: Icon(Icons.add, size: AppIconSize.md), // 24dp
  ),
  floatingActionButtonLocation: FloatingActionButtonLocation.endContained,
)
```
