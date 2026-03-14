# Navigation Bar

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/navigation-bar/overview |
| Guidelines | https://m3.material.io/components/navigation-bar/guidelines |
| Specs | https://m3.material.io/components/navigation-bar/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Navigation Bar (M3) | `NavigationBar` |
| (M2 레거시) | `BottomNavigationBar` |

## 언제 사용하나요?

- 앱의 최상위 목적지 3~5개를 동등한 중요도로 전환할 때
- 탭 간 이동이 빈번하고 콘텐츠가 서로 독립적일 때
- 화면 하단에 항상 표시되는 기본 네비게이션이 필요할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | **NavigationBar 사용** — 하단 고정 |
| Tablet (medium) | **NavigationRail로 대체** — 세로 사이드 레일 |
| Desktop/Web (expanded) | **NavigationDrawer로 대체** — 고정 사이드 드로어 |

> M3 Canonical Layout: compact → NavigationBar, medium → NavigationRail, expanded → NavigationDrawer

## Variants

- **Baseline** — 표준 네비게이션 바
- **Flexible** (M3 Expressive) — 더 짧고 유연한 형태

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Navigation Bar Guide" 프레임을 만들어주세요.
모든 내용은 이 "Navigation Bar Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/navigation-bar/overview

---

## 프레임 설정
- 이름: "Navigation Bar Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Navigation Bar"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · navigation-bar"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/navigation-bar/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 앱의 최상위 목적지 3~5개를 동등한 중요도로 전환할 때
  · 탭 간 이동이 빈번하고 콘텐츠가 서로 독립적일 때
  · 화면 하단에 항상 표시되는 기본 네비게이션이 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- 하나의 Navigation Bar를 전체 너비(360dp)로 그리기

  ┌─ Navigation Bar (Baseline) ─────────────────────────────┐
  │  너비: 360dp, 높이: 80dp                                  │
  │  배경: Surface (Surface Container)                       │
  │  아이템 4개 균등 배치:                                    │
  │                                                          │
  │  [Home]       [Explore]      [Library]     [Profile]     │
  │  Active:                                                  │
  │    indicator: 64×32dp, Secondary Container, corner 16dp              │
  │    icon: 24dp, On-Surface                                    │
  │    label: "Home" (12sp, On-Surface, bold)                   │
  │  Inactive:                                                │
  │    icon: 24dp, On-Surface-Variant                                    │
  │    label: "Explore" (12sp, On-Surface-Variant)                      │
  └──────────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Navigation Bar 전체를 크게 그리고 번호 레이블 연결:
  1. Container — 전체 너비, height 80dp, Surface Container 배경
  2. Active indicator — 64×32dp, Secondary Container, corner 16dp
  3. Icon — 24dp (active: On-Secondary-Container, inactive: On-Surface-Variant)
  4. Label — 12sp (active: On-Surface, inactive: On-Surface-Variant)
  5. Badge (선택) — 아이콘 우상단 배지

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                        | 값                      | 토큰                               |
  |----------------------------|-------------------------|------------------------------------|
  | Height                     | 80 dp                   | —                                  |
  | Active indicator size      | 64 × 32 dp              | —                                  |
  | Active indicator corner    | 16 dp                   | —                                  |
  | Icon size                  | 24 dp                   | AppIconSize.md                     |
  | Label TextStyle            | labelMedium             | textTheme.labelMedium              |
  | Item count                 | 3–5개                   | —                                  |
  | Container bg               | surfaceContainer        | colorScheme.surfaceContainer       |
  | Active indicator bg        | secondaryContainer      | colorScheme.secondaryContainer     |
  | Active icon color          | onSecondaryContainer    | colorScheme.onSecondaryContainer   |
  | Inactive icon color        | onSurfaceVariant        | colorScheme.onSurfaceVariant       |
  | Active label color         | onSurface               | colorScheme.onSurface              |
  | Inactive label color       | onSurfaceVariant        | colorScheme.onSurfaceVariant       |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  하단 NavigationBar 사용     │
  │  → NavigationBar           │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  NavigationRail로 대체      │
  │  → NavigationRail          │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  NavigationDrawer로 대체    │
  │  → NavigationDrawer        │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Navigation Bar Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  NavigationBar/3Items — 아이템 3개:
  · 컴포넌트 이름: "NavigationBar/3Items"
  · 높이: 80dp, 너비: 360dp
  · 배경: Surface Container
  · Active indicator: Secondary Container, 64×32dp, corner 16dp
  · 아이콘: 24dp (선택: On-Secondary-Container / 비선택: On-Surface-Variant)
  · 레이블: 12sp (선택: On-Secondary-Container / 비선택: On-Surface-Variant)

  NavigationBar/4Items — 아이템 4개:
  · 컴포넌트 이름: "NavigationBar/4Items"
  · 동일 구조, 아이템 4개 균등 배치

  NavigationBar/5Items — 아이템 5개:
  · 컴포넌트 이름: "NavigationBar/5Items"
  · 동일 구조, 아이템 5개 균등 배치


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  NavigationBar(
    selectedIndex: _selectedIndex,
    onDestinationSelected: (index) => setState(() => _selectedIndex = index),
    destinations: const [
      NavigationDestination(
        icon: Icon(Icons.home_outlined),
        selectedIcon: Icon(Icons.home),  // 선택 시 아이콘 전환
        label: 'Home',
      ),
      NavigationDestination(
        icon: Icon(Icons.explore_outlined),
        selectedIcon: Icon(Icons.explore),
        label: 'Explore',
      ),
      NavigationDestination(
        icon: Icon(Icons.library_music_outlined),
        selectedIcon: Icon(Icons.library_music),
        label: 'Library',
      ),
    ],
  )

---

## Flutter Usage

> `NavigationBar`는 `AppTheme` 적용 시 `colorScheme`에서 색상을 자동으로 가져온다.
> `backgroundColor`, `indicatorColor`를 직접 지정하는 건 **커스터마이징** 시에만 사용한다.

```dart
import 'package:flutter_design/flutter_design.dart';

// 기본 사용 — 테마가 색상 자동 적용
NavigationBar(
  selectedIndex: _selectedIndex,
  onDestinationSelected: (index) => setState(() => _selectedIndex = index),
  destinations: [
    NavigationDestination(
      icon: Icon(Icons.home_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.home, size: AppIconSize.md),
      label: 'Home',
    ),
  ],
)

// 커스터마이징 — 색상을 직접 지정해야 할 때
final cs = Theme.of(context).colorScheme;

NavigationBar(
  selectedIndex: _selectedIndex,
  backgroundColor: cs.surfaceContainer,
  indicatorColor: cs.secondaryContainer,
  onDestinationSelected: (index) {
    setState(() => _selectedIndex = index);
  },
  destinations: [
    NavigationDestination(
      icon: Icon(Icons.home_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.home, size: AppIconSize.md),
      label: 'Home',
    ),
    NavigationDestination(
      icon: Icon(Icons.explore_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.explore, size: AppIconSize.md),
      label: 'Explore',
    ),
    NavigationDestination(
      icon: Icon(Icons.library_music_outlined, size: AppIconSize.md),
      selectedIcon: Icon(Icons.library_music, size: AppIconSize.md),
      label: 'Library',
    ),
  ],
)
```
