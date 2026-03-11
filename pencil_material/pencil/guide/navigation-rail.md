# Navigation Rail

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/navigation-rail/overview |
| Guidelines | https://m3.material.io/components/navigation-rail/guidelines |
| Specs | https://m3.material.io/components/navigation-rail/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Navigation Rail | `NavigationRail` |

## 언제 사용하나요?

- 태블릿(medium) 화면에서 세로 사이드 네비게이션이 필요할 때
- 3~7개의 목적지를 좁은 세로 레일에 아이콘으로 표시할 때
- 모바일의 NavigationBar를 large 화면에 맞게 확장할 때
- 콘텐츠 영역을 최대화하면서 네비게이션도 항상 접근 가능해야 할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | **사용 안 함** → NavigationBar 사용 |
| Tablet (medium) | **NavigationRail 사용** — 좌측 세로 레일 |
| Desktop/Web (expanded) | **NavigationDrawer로 전환** 또는 확장된 Rail 유지 |

> M3 Canonical Layout의 핵심: compact=Bar, medium=Rail, expanded=Drawer

## Variants

- **Icon only** — 아이콘만 표시
- **Icon + label** — 아이콘 아래 레이블 표시
- **With FAB** — 상단에 FAB 포함

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Navigation Rail Guide" 프레임을 만들어주세요.
모든 내용은 이 "Navigation Rail Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/navigation-rail/overview

---

## 프레임 설정
- 이름: "Navigation Rail Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Navigation Rail"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · navigation-rail"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/navigation-rail/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 태블릿 화면에서 세로 사이드 네비게이션이 필요할 때
  · 3~7개의 목적지를 좁은 세로 레일에 표시할 때
  · 모바일 NavigationBar를 large 화면에 맞게 확장할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 가로 나란히 배치, gap 24px (각 variant는 rail 형태 세로 배치)

  ┌─ Icon only ──────────────────────┐
  │  width: 80dp, height: 400dp      │
  │  배경: Surface (Surface)          │
  │  목적지 4개 세로 배치, vgap 4dp   │
  │  active indicator: 56×32dp       │
  │    bg: Secondary Container, corner 16dp      │
  │    icon: 24dp, On-Surface          │
  │  inactive icon: 24dp, On-Surface-Variant   │
  └───────────────────────────────────┘

  ┌─ Icon + Label ───────────────────┐
  │  width: 80dp, height: 400dp      │
  │  목적지 4개 (icon + 12sp label)  │
  │  active: indicator + label 굵게  │
  │  inactive: icon + label 보통     │
  └───────────────────────────────────┘

  ┌─ With FAB ───────────────────────┐
  │  width: 80dp, height: 400dp      │
  │  상단: Extended FAB (선택)       │
  │  아래: 목적지 목록               │
  └───────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Icon + Label Rail을 크게 그리고 번호 레이블 연결:
  1. Container — width 80dp, surfaceContainerLow 배경, 전체 높이
  2. FAB area (선택) — 상단 leading 영역
  3. Active indicator — 56×32dp, secondaryContainer, corner 16dp
  4. Icon — 24dp (active: onSecondaryContainer, inactive: onSurfaceVariant)
  5. Label — labelMedium (active: onSurface, inactive: onSurfaceVariant)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                    | 값                      | 토큰                                  |
  |------------------------|-------------------------|---------------------------------------|
  | Width                  | 80 dp (min)             | —                                     |
  | Active indicator size  | 56 × 32 dp              | —                                     |
  | Active indicator corner| 16 dp                   | —                                     |
  | Icon size              | 24 dp                   | AppIconSize.md                        |
  | Label TextStyle        | labelMedium             | textTheme.labelMedium                 |
  | Destination count      | 3–7개                   | —                                     |
  | Container bg           | surfaceContainerLow     | colorScheme.surfaceContainerLow       |
  | Active indicator bg    | secondaryContainer      | colorScheme.secondaryContainer        |
  | Active icon color      | onSecondaryContainer    | colorScheme.onSecondaryContainer      |
  | Inactive icon color    | onSurfaceVariant        | colorScheme.onSurfaceVariant          |
  | Active label color     | onSurface               | colorScheme.onSurface                 |
  | Inactive label color   | onSurfaceVariant        | colorScheme.onSurfaceVariant          |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  사용 안 함                 │
  │  → NavigationBar 사용      │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  NavigationRail 사용        │
  │  → NavigationRail          │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Drawer로 전환 또는 Rail 유지│
  │  → NavigationDrawer        │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Navigation Rail Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  NavigationRail/Default — FAB 없음:
  · 컴포넌트 이름: "NavigationRail/Default"
  · 너비: 80dp, 높이: 전체 화면
  · 배경: Surface Container Low
  · Indicator: Secondary Container, 56×32dp, corner 16dp
  · 아이콘: 24dp (선택: On-Secondary-Container / 비선택: On-Surface-Variant)
  · 레이블: 12sp, 아이콘 하단

  NavigationRail/WithFAB — 상단 FAB 포함:
  · 컴포넌트 이름: "NavigationRail/WithFAB"
  · 동일 구조, 상단에 FAB 영역 추가
  · FAB: 56×56dp, Primary Container, corner 16dp


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  NavigationRail(
    selectedIndex: _selectedIndex,
    onDestinationSelected: (index) {
      setState(() => _selectedIndex = index);
    },
    labelType: NavigationRailLabelType.all,
    destinations: const [
      NavigationRailDestination(
        icon: Icon(Icons.home_outlined),
        selectedIcon: Icon(Icons.home),  // 선택 시 아이콘 전환
        label: Text('Home'),
      ),
      NavigationRailDestination(
        icon: Icon(Icons.explore_outlined),
        selectedIcon: Icon(Icons.explore),
        label: Text('Explore'),
      ),
    ],
  )

---

## Flutter Usage

> `NavigationRail`은 `AppTheme` 적용 시 `colorScheme`에서 색상을 자동으로 가져온다.
> `backgroundColor`, `indicatorColor`를 직접 지정하는 건 **커스터마이징** 시에만 사용한다.

```dart
import 'package:flutter_design/flutter_design.dart';

// 기본 사용 — 테마가 색상 자동 적용
NavigationRail(
  selectedIndex: _selectedIndex,
  labelType: NavigationRailLabelType.all,
  onDestinationSelected: (index) => setState(() => _selectedIndex = index),
  destinations: [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.home, size: AppIconSize.md),
      label: Text('Home'),
    ),
  ],
)

// 커스터마이징 — 색상을 직접 지정해야 할 때
final cs = Theme.of(context).colorScheme;

NavigationRail(
  selectedIndex: _selectedIndex,
  backgroundColor: cs.surfaceContainerLow,
  indicatorColor: cs.secondaryContainer,
  labelType: NavigationRailLabelType.all,
  onDestinationSelected: (index) {
    setState(() => _selectedIndex = index);
  },
  leading: FloatingActionButton(
    elevation: AppElevation.level2,
    backgroundColor: cs.primaryContainer,
    foregroundColor: cs.onPrimaryContainer,
    onPressed: () {},
    child: Icon(Icons.add, size: AppIconSize.md),
  ),
  destinations: [
    NavigationRailDestination(
      icon: Icon(Icons.home_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.home, size: AppIconSize.md),
      label: Text('Home'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.explore_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.explore, size: AppIconSize.md),
      label: Text('Explore'),
    ),
  ],
)
```
