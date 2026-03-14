# Top App Bar

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/app-bars/overview |
| Guidelines | https://m3.material.io/components/app-bars/guidelines |
| Specs | https://m3.material.io/components/app-bars/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Small | `AppBar` |
| Center-aligned | `AppBar(centerTitle: true)` |
| Medium | `SliverAppBar.medium()` |
| Large | `SliverAppBar.large()` |
| Collapsing (custom) | `SliverAppBar(pinned/floating/snap)` |

## 언제 사용하나요?

- 화면 제목, 뒤로가기, 주요 액션(검색, 더보기)을 상단에 배치할 때
- 스크롤 시 앱바가 축소/사라지는 collapsing 효과가 필요할 때
- 네비게이션 드로어 또는 뒤로가기와 연동해 계층 이동을 표시할 때
- Medium/Large는 풍부한 타이틀 공간이 필요한 상세 화면에 사용

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Small 또는 Center-aligned AppBar, Medium/Large (콘텐츠 상세) |
| Tablet (medium) | Small AppBar, 액션 아이콘 수 늘릴 수 있음 |
| Desktop/Web (expanded) | Small AppBar 또는 커스텀 헤더, 액션을 툴바/사이드바로 분산 |

## Variants

- **Small** — 표준, 1줄 타이틀
- **Center-aligned** — 타이틀 중앙 정렬 (소셜/미디어 앱)
- **Medium** — 스크롤 시 축소되는 2줄 타이틀
- **Large** — 스크롤 시 축소되는 큰 타이틀

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Top App Bar Guide" 프레임을 만들어주세요.

모든 내용은 이 "Top App Bar Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/app-bars/overview

---

## 프레임 설정
- 이름: "Top App Bar Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Top App Bar"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · app-bars"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/app-bars/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 화면 제목, 뒤로가기, 주요 액션(검색, 더보기)을 상단에 배치할 때
  · 스크롤 시 앱바가 축소/사라지는 collapsing 효과가 필요할 때
  · Medium/Large는 풍부한 타이틀 공간이 필요한 상세 화면에 사용

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 세로 나열 (너비 360dp), gap 16px

  ┌─ Small (너비 360dp, height 56dp) ────────────────────┐
  │  배경: Surface Container                              │
  │  좌: 뒤로가기 아이콘 (24dp, On-Surface-Variant)       │
  │  제목: "Page title" (titleLarge 22sp, On-Surface, 좌)│
  │  우: 액션 아이콘 2개 (24dp)                           │
  └──────────────────────────────────────────────────────┘

  ┌─ Center-aligned (너비 360dp, height 56dp) ───────────┐
  │  좌: 뒤로가기 아이콘                                  │
  │  제목: "Page title" (titleLarge 22sp, 중앙 정렬)      │
  │  우: 액션 아이콘                                      │
  └──────────────────────────────────────────────────────┘

  ┌─ Medium (너비 360dp, expanded 112dp / collapsed 64dp)┐
  │  상단 행: 뒤로가기 + 우측 아이콘                       │
  │  하단: "Page title" (headlineSmall, 좌측 하단)        │
  └──────────────────────────────────────────────────────┘

  ┌─ Large (너비 360dp, expanded 152dp / collapsed 64dp) ┐
  │  상단 행: 뒤로가기 + 우측 아이콘                       │
  │  하단: "Page title" (headlineMedium, 좌측 하단)       │
  └──────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Small AppBar를 크게 그리고 번호 레이블 연결:
  1. Container — surfaceContainer 배경, 전체 너비
  2. Leading icon — 뒤로가기/메뉴 24dp, onSurfaceVariant
  3. Title — titleLarge (Small/Center, collapsed) / headlineSmall (Medium expanded) / headlineMedium (Large expanded), onSurface
  4. Trailing icons — 우측 액션들 24dp, onSurfaceVariant (최대 3개 권장)
  5. Scroll elevation — 스크롤 시 surfaceContainerHigh로 전환 (scrolledUnderElevation)
  6. Bottom slot (선택) — TabBar 연결 가능 (AppBar.bottom)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                       | Small / Center      | Medium              | Large               | 토큰                                 |
  |---------------------------|---------------------|---------------------|---------------------|--------------------------------------|
  | Height                    | 56 dp               | expanded 112 dp / collapsed 64 dp | expanded 152 dp / collapsed 64 dp | — |
  | Title TextStyle (collapsed)| titleLarge         | titleLarge          | titleLarge          | textTheme.titleLarge                 |
  | Title TextStyle (expanded) | —                  | headlineSmall       | headlineMedium      | textTheme.headlineSmall/Medium       |
  | Title align               | Start / Center      | Start (하단)        | Start (하단)        | centerTitle: true/false              |
  | Icon size                 | 24 dp               | 24 dp               | 24 dp               | —                                    |
  | Container bg              | surfaceContainer    | surfaceContainer    | surfaceContainer    | colorScheme.surfaceContainer         |
  | Title color               | onSurface           | onSurface           | onSurface           | colorScheme.onSurface                |
  | Icon color                | onSurfaceVariant    | onSurfaceVariant    | onSurfaceVariant    | colorScheme.onSurfaceVariant         |
  | Scrolled-under bg         | surfaceContainerHigh| surfaceContainerHigh| surfaceContainerHigh| colorScheme.surfaceContainerHigh     |
  | scrolledUnderElevation    | 3 (기본)            | 3 (기본)            | 3 (기본)            | — (0 = shadow 없음)                  |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Small 또는 Center-aligned  │
  │  → AppBar                  │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Small, 액션 아이콘 증가    │
  │  → AppBar                  │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Small 또는 커스텀 헤더     │
  │  → AppBar                  │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Top App Bar Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  TopAppBar/Small — 표준 1줄 앱바:
  · 컴포넌트 이름: "TopAppBar/Small"
  · 높이: 64dp, 너비: 360dp, 배경: Surface Container
  · Leading: 뒤로가기 아이콘 24dp, On-Surface-Variant
  · 제목: titleLarge 22sp, On-Surface, 좌측 정렬
  · Actions: 우측 아이콘 2개 24dp, On-Surface-Variant

  TopAppBar/CenterAligned — 중앙 정렬 앱바:
  · 컴포넌트 이름: "TopAppBar/CenterAligned"
  · 높이: 64dp, 동일 구조
  · 제목: titleLarge 22sp, On-Surface, 중앙 정렬

  TopAppBar/Medium — 2줄 축소형 앱바 (expanded):
  · 컴포넌트 이름: "TopAppBar/Medium"
  · 높이: 112dp (expanded) / 64dp (collapsed), 배경: Surface Container
  · 상단: 뒤로가기 + 우측 아이콘 (24dp)
  · 하단: 제목 headlineSmall, On-Surface, 좌측 하단

  TopAppBar/Large — 큰 제목 축소형 앱바 (expanded):
  · 컴포넌트 이름: "TopAppBar/Large"
  · 높이: 152dp (expanded) / 64dp (collapsed), 배경: Surface Container
  · 상단: 뒤로가기 + 우측 아이콘
  · 하단: 제목 headlineMedium, On-Surface, 좌측 하단

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Small
  AppBar(
    leading: IconButton(icon: Icon(Icons.arrow_back), onPressed: () {}),
    title: Text('Page title'),
    actions: [IconButton(icon: Icon(Icons.search), onPressed: () {})],
  )

  // Medium (collapsing)
  CustomScrollView(slivers: [
    SliverAppBar.medium(
      title: Text('Page title'),
      leading: IconButton(icon: Icon(Icons.arrow_back), onPressed: () {}),
    ),
    SliverFillRemaining(child: content),
  ])

  // Large (collapsing)
  CustomScrollView(slivers: [
    SliverAppBar.large(title: Text('Page title')),
    SliverFillRemaining(child: content),
  ])

---

## Flutter Usage

> `AppBar`은 `AppTheme` 적용 시 `colorScheme`에서 색상을 자동으로 가져온다.
> `backgroundColor`, `foregroundColor`를 직접 지정하는 건 **커스터마이징** 시에만 사용한다.

```dart
import 'package:flutter_design/flutter_design.dart';

// Small AppBar — 기본 (테마 자동 적용)
AppBar(
  title: const Text('페이지 제목'),
  leading: IconButton(
    icon: const Icon(Icons.arrow_back),
    onPressed: () => context.pop(),
  ),
  actions: [
    IconButton(icon: const Icon(Icons.search), onPressed: () {}),
    IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),
  ],
)

// Center-aligned AppBar
AppBar(
  centerTitle: true,
  title: const Text('페이지 제목'),
  leading: IconButton(
    icon: const Icon(Icons.arrow_back),
    onPressed: () => context.pop(),
  ),
)

// Leading 없애기 — 루트 화면 또는 커스텀 leading
AppBar(
  automaticallyImplyLeading: false, // 뒤로가기 자동 생성 비활성
  title: const Text('홈'),
  leading: IconButton(
    icon: const Icon(Icons.menu),
    onPressed: () => _scaffoldKey.currentState?.openDrawer(),
  ),
)

// AppBar + TabBar 연동
AppBar(
  title: const Text('페이지 제목'),
  bottom: TabBar(
    controller: _tabController,
    tabs: const [Tab(text: '전체'), Tab(text: '최신')],
  ),
)

// scrolledUnderElevation — 스크롤 시 elevation 억제
AppBar(
  title: const Text('페이지 제목'),
  scrolledUnderElevation: 0, // 0 = 스크롤해도 shadow/색상 변화 없음
)

// toolbarHeight — M3 스펙 64dp / Flutter 기본값(kToolbarHeight)은 56dp
// M3 준수 시 명시적으로 64 지정 필요
AppBar(
  toolbarHeight: 64,
  title: const Text('페이지 제목'),
)

// Medium (collapsing) — 스크롤 시 타이틀 축소
CustomScrollView(
  slivers: [
    SliverAppBar.medium(
      title: const Text('페이지 제목'),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => context.pop(),
      ),
      actions: [
        IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),
      ],
    ),
    SliverList(delegate: SliverChildListDelegate([...])),
  ],
)

// Large (collapsing) — 큰 타이틀, 상세 화면
CustomScrollView(
  slivers: [
    SliverAppBar.large(
      title: const Text('상세 페이지'),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => context.pop(),
      ),
      actions: [
        IconButton(icon: const Icon(Icons.share), onPressed: () {}),
      ],
    ),
    SliverFillRemaining(child: content),
  ],
)

// SliverAppBar — pinned/floating/snap 커스텀 조합
// pinned: true  → 스크롤해도 앱바 고정 (항상 보임)
// floating: true → 아래 스크롤 시 즉시 나타남
// snap: true    → floating과 함께, 일부만 보여도 완전히 펼쳐짐 (floating 필요)
SliverAppBar(
  pinned: true,
  floating: false,
  snap: false,
  expandedHeight: 152,
  flexibleSpace: FlexibleSpaceBar(
    title: const Text('페이지 제목'),
    background: Image.network(imageUrl, fit: BoxFit.cover), // 배경 이미지
  ),
)
```
