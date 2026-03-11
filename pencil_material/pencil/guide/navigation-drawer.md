# Navigation Drawer

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/navigation-drawer/overview |
| Guidelines | https://m3.material.io/components/navigation-drawer/guidelines |
| Specs | https://m3.material.io/components/navigation-drawer/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Modal drawer | `Drawer` + `NavigationDrawer` |
| Permanent drawer | `NavigationDrawer` (항상 표시) |

## 언제 사용하나요?

- 목적지가 5개 이상이거나 계층 구조가 복잡할 때
- 앱의 모든 최상위 목적지에 대한 접근을 한 곳에서 제공할 때
- 자주 쓰지 않는 목적지를 숨겨두고 필요할 때 열 수 있게 할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Modal Drawer (햄버거 메뉴로 열기) |
| Tablet (medium) | NavigationRail 선호, 필요 시 Modal Drawer 유지 |
| Desktop/Web (expanded) | **Permanent Drawer** — 항상 표시, 콘텐츠 옆 고정 |

## Variants

- **Modal** — 슬라이드로 열리고 스크림으로 닫힘
- **Permanent** — 항상 사이드에 고정 표시 (large 화면)
- **Dismissible** — 스크롤 시 숨겨지는 형태

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Navigation Drawer Guide" 프레임을 만들어주세요.
모든 내용은 이 "Navigation Drawer Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/navigation-drawer/overview

---

## 프레임 설정
- 이름: "Navigation Drawer Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Navigation Drawer"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · navigation-drawer"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/navigation-drawer/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 목적지가 5개 이상이거나 계층 구조가 복잡할 때
  · 앱의 모든 최상위 목적지에 대한 접근을 한 곳에서 제공할 때
  · 자주 쓰지 않는 목적지를 숨겨두고 필요할 때 열 수 있게 할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Modal Drawer ─────────────────────┐
  │  전체 화면 (360×800dp)              │
  │  왼쪽: Drawer panel (280×800dp)    │
  │    배경: Surface (Surface)          │
  │    상단 여백: 12dp                  │
  │    제목 영역: "App Name" (24sp)     │
  │    목적지 아이템 5개:               │
  │      active: bg Secondary Container, h 56dp    │
  │      label + icon 좌측 정렬         │
  │  오른쪽: scrim (#000 32%)          │
  └────────────────────────────────────┘

  ┌─ Permanent Drawer ─────────────────┐
  │  전체 화면 (1024×800dp)            │
  │  좌측: Drawer (280dp, h 전체)      │
  │    항상 고정 표시                   │
  │    배경: Surface                   │
  │  우측: 메인 콘텐츠 영역 (744dp)     │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Modal Drawer를 크게 그리고 번호 레이블 연결:
  1. Container — width 280dp, surfaceContainerLow
  2. Header (선택) — titleSmall, onSurfaceVariant
  3. Destination item — height 56dp, hpad 28dp
  4. Active indicator — secondaryContainer, corner 28dp
  5. Destination icon — 24dp (active: onSecondaryContainer, inactive: onSurfaceVariant)
  6. Destination label — labelLarge (active: onSecondaryContainer, inactive: onSurfaceVariant)
  7. Divider — 그룹 구분 (선택)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                | 값                      | 토큰                                  |
  |--------------------|-------------------------|---------------------------------------|
  | Width              | 280–360 dp              | —                                     |
  | Item height        | 56 dp                   | —                                     |
  | Horizontal padding | 12 dp                   | —                                     |
  | Icon size          | 24 dp                   | AppIconSize.md                        |
  | Label TextStyle    | labelLarge              | textTheme.labelLarge                  |
  | Header TextStyle   | titleSmall              | textTheme.titleSmall                  |
  | Header height (opt)| 48–88 dp                | —                                     |
  | Container bg       | surfaceContainerLow     | colorScheme.surfaceContainerLow       |
  | Active indicator   | secondaryContainer      | colorScheme.secondaryContainer        |
  | Active icon color  | onSecondaryContainer    | colorScheme.onSecondaryContainer      |
  | Active label color | onSecondaryContainer    | colorScheme.onSecondaryContainer      |
  | Inactive icon/label| onSurfaceVariant        | colorScheme.onSurfaceVariant          |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Modal Drawer 슬라이드     │
  │  → Scaffold.drawer         │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  NavigationRail 선호        │
  │  → NavigationRail          │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Permanent Drawer 고정     │
  │  → NavigationDrawer (perm) │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Navigation Drawer Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  NavigationDrawer/Modal — 스크림 포함 모달 드로어:
  · 컴포넌트 이름: "NavigationDrawer/Modal"
  · 너비: 360dp, 높이: 전체 화면
  · 배경: Surface Container Low
  · 우상단 corner: 16dp
  · Headline: 14sp, On-Surface-Variant
  · Item 높이: 56dp, 수평 패딩: 28dp
  · 선택 indicator: Secondary Container, corner 28dp
  · 아이콘: 24dp, 레이블: 14sp

  NavigationDrawer/Persistent — 항상 고정 드로어:
  · 컴포넌트 이름: "NavigationDrawer/Persistent"
  · 동일 구조, 스크림 없음
  · 콘텐츠 영역 옆에 항상 표시


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  Scaffold(
    drawer: NavigationDrawer(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (index) {
        setState(() => _selectedIndex = index);
        Navigator.pop(context);
      },
      children: const [
        NavigationDrawerDestination(
          icon: Icon(Icons.home),
          label: Text('Home'),
        ),
        NavigationDrawerDestination(
          icon: Icon(Icons.explore),
          label: Text('Explore'),
        ),
      ],
    ),
  )

---

## Flutter Usage

> `NavigationDrawer`는 `AppTheme` 적용 시 `colorScheme`에서 색상을 자동으로 가져온다.
> `backgroundColor`, `indicatorColor`를 직접 지정하는 건 **커스터마이징** 시에만 사용한다.

```dart
import 'package:flutter_design/flutter_design.dart';

// 기본 사용 — 테마가 색상 자동 적용
Scaffold(
  drawer: NavigationDrawer(
    selectedIndex: _selectedIndex,
    onDestinationSelected: (index) {
      setState(() => _selectedIndex = index);
      Navigator.pop(context);
    },
    children: [
      NavigationDrawerDestination(
        icon: Icon(Icons.home_outlined, size: AppIconSize.md),
        label: Text('Home'),
      ),
    ],
  ),
)

// 커스터마이징 — 색상을 직접 지정해야 할 때
final cs = Theme.of(context).colorScheme;

Scaffold(
  drawer: NavigationDrawer(
    selectedIndex: _selectedIndex,
    backgroundColor: cs.surfaceContainerLow,
    indicatorColor: cs.secondaryContainer,
    onDestinationSelected: (index) {
      setState(() => _selectedIndex = index);
      Navigator.pop(context);
    },
    children: [
      Padding(
        padding: EdgeInsets.fromLTRB(AppSpacing.base, AppSpacing.md, AppSpacing.base, AppSpacing.sm),
        child: Text('앱 이름', style: Theme.of(context).textTheme.titleSmall),
      ),
      NavigationDrawerDestination(
        icon: Icon(Icons.home_outlined, size: AppIconSize.md),
        label: Text('Home'),
      ),
      NavigationDrawerDestination(
        icon: Icon(Icons.explore_outlined, size: AppIconSize.md),
        label: Text('Explore'),
      ),
    ],
  ),
)
```
