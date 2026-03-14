# Tabs

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/tabs/overview |
| Guidelines | https://m3.material.io/components/tabs/guidelines |
| Specs | https://m3.material.io/components/tabs/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Tab bar | `TabBar` |
| Tab content | `TabBarView` |
| Controller | `TabController` / `DefaultTabController` |

## 언제 사용하나요?

- 같은 계층의 관련된 콘텐츠를 여러 섹션으로 나눌 때
- 뉴스 카테고리, 상품 탭, 프로필 섹션처럼 수평 콘텐츠 전환
- 5개 이하의 탭으로 콘텐츠를 구분하고 스크롤 탐색을 줄일 때
- 앱바 하단 또는 화면 내에서 보조 네비게이션으로 사용할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 고정 탭 (화면 너비에 맞춤), 탭 많으면 scrollable |
| Tablet (medium) | 고정 탭, 탭 너비 여유 있게 |
| Desktop/Web (expanded) | 고정 탭, 최대 너비 제한, NavigationRail과 병용 가능 |

## Variants

- **Primary tabs** — 화면 상단, 주요 콘텐츠 구분, AppBar 하단
- **Secondary tabs** — 화면 내, 보조 콘텐츠 구분
- **Scrollable** — 탭이 많을 때 가로 스크롤
- **Icon-only** — 아이콘만 표시 (높이 46dp)
- **Icon + Label** — 아이콘 위 + 텍스트 아래 (높이 72dp)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Tabs Guide" 프레임을 만들어주세요.

모든 내용은 이 "Tabs Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/tabs/overview

---

## 프레임 설정
- 이름: "Tabs Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Tabs"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · tabs"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/tabs/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 같은 계층의 관련된 콘텐츠를 여러 섹션으로 나눌 때
  · 뉴스 카테고리, 상품 탭처럼 수평 콘텐츠 전환
  · 5개 이하의 탭으로 콘텐츠를 구분하고 스크롤 탐색을 줄일 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 5개를 세로 나열 (너비 360dp), gap 24px

  ┌─ Primary / Text-only (너비 360dp) ────────────────┐
  │  height: 48dp                                       │
  │  배경: Surface, 하단 outlineVariant 1dp             │
  │  탭 3개 균등 배치                                   │
  │  active: indicator bar 3dp 하단, Primary            │
  │  active label: Primary, titleSmall                  │
  │  inactive label: On-Surface-Variant, titleSmall     │
  └────────────────────────────────────────────────────┘

  ┌─ Secondary / Text-only (너비 360dp) ──────────────┐
  │  height: 48dp                                       │
  │  active indicator: 하단 2dp bar, On-Surface        │
  │  active label: On-Surface / inactive: On-Surface-Variant │
  └────────────────────────────────────────────────────┘

  ┌─ Scrollable (너비 360dp, 탭 초과) ────────────────┐
  │  탭 6개, 화면 너비 초과 → 가로 스크롤              │
  │  첫 탭 선택 상태, 우측 페이드 아웃                  │
  └────────────────────────────────────────────────────┘

  ┌─ Icon-only (너비 360dp) ───────────────────────────┐
  │  height: 46dp                                       │
  │  아이콘 24dp, 탭 레이블 없음                        │
  │  active icon: Primary / inactive: On-Surface-Variant│
  └────────────────────────────────────────────────────┘

  ┌─ Icon + Label (너비 360dp) ────────────────────────┐
  │  height: 72dp                                       │
  │  아이콘(24dp) 위 + 텍스트 아래 배치                 │
  │  active: Primary / inactive: On-Surface-Variant     │
  └────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Primary TabBar (Icon + Label)를 크게 그리고 번호 레이블 연결:
  1. Container — surface 배경, 하단 outlineVariant 1dp
  2. Active indicator — 3dp bar (Primary) / 2dp (Secondary), 하단
  3. Icon (선택) — 24dp, 탭 상단. text 없으면 중앙 세로 정렬
  4. Label — titleSmall, 아이콘 아래 배치 (iconMargin 기본 2dp)
  5. State layer — hover/focus/pressed 상태 오버레이

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                             | Primary           | Secondary         | 토큰                                 |
  |---------------------------------|-------------------|-------------------|--------------------------------------|
  | Height (text-only)              | 48 dp             | 48 dp             | —                                    |
  | Height (icon + text)            | 72 dp             | 72 dp             | —                                    |
  | Height (icon-only)              | 46 dp             | 46 dp             | —                                    |
  | Indicator height                | 3 dp              | 2 dp              | —                                    |
  | Min item width                  | 90 dp             | 90 dp             | —                                    |
  | Icon size                       | 24 dp             | 24 dp             | —                                    |
  | Label TextStyle                 | titleSmall        | titleSmall        | textTheme.titleSmall                 |
  | Active label / icon color       | primary           | onSurface         | colorScheme.primary / .onSurface     |
  | Inactive label / icon color     | onSurfaceVariant  | onSurfaceVariant  | colorScheme.onSurfaceVariant         |
  | Indicator color                 | primary           | onSurface         | colorScheme.primary / .onSurface     |
  | Container bg                    | surface           | surface           | colorScheme.surface                  |
  | Divider color                   | outlineVariant    | outlineVariant    | colorScheme.outlineVariant           |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  고정 탭, 많으면 scrollable │
  │  → TabBar                  │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  고정 탭, 너비 여유         │
  │  → TabBar                  │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  고정 탭, NavigationRail 병용│
  │  → TabBar                  │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Tabs Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 세로 나열, gap 24px:

  Tabs/Primary/TextOnly — Primary TabBar 텍스트 탭:
  · 컴포넌트 이름: "Tabs/Primary/TextOnly"
  · 높이: 48dp, 너비: 360dp, 배경: Surface
  · Indicator: Primary, 3dp 높이, 하단
  · 선택 레이블: Primary, titleSmall
  · 비선택 레이블: On-Surface-Variant, titleSmall
  · 탭 3개 (홈 / 탐색 / 보관함)

  Tabs/Secondary/TextOnly — Secondary TabBar 텍스트 탭:
  · 컴포넌트 이름: "Tabs/Secondary/TextOnly"
  · 높이: 48dp, 너비: 360dp, 배경: Surface
  · Indicator: On-Surface, 2dp 높이, 하단
  · 선택 레이블: On-Surface / 비선택: On-Surface-Variant
  · 탭 3개 (전체 / 최신 / 인기)

  Tabs/Primary/IconLabel — Primary TabBar 아이콘+텍스트 탭:
  · 컴포넌트 이름: "Tabs/Primary/IconLabel"
  · 높이: 72dp, 너비: 360dp, 배경: Surface
  · 아이콘 24dp (위) + 텍스트 (아래), gap 2dp
  · Indicator: Primary, 3dp 높이, 하단
  · 탭 3개 (home / explore / library 아이콘 + 텍스트)

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Primary — text-only (48dp)
  DefaultTabController(
    length: 3,
    child: Scaffold(
      appBar: AppBar(
        bottom: TabBar(tabs: [
          Tab(text: '홈'),
          Tab(text: '탐색'),
          Tab(text: '보관함'),
        ]),
      ),
      body: TabBarView(children: [...]),
    ),
  )

  // Secondary — 화면 내 보조 탭
  TabBar.secondary(tabs: [Tab(text: '전체'), Tab(text: '최신')])

  // Icon-only (46dp)
  TabBar(tabs: [
    Tab(icon: Icon(Icons.home_outlined)),
    Tab(icon: Icon(Icons.explore_outlined)),
  ])

  // Icon + Label (72dp)
  TabBar(tabs: [
    Tab(icon: Icon(Icons.home_outlined), text: '홈'),
    Tab(icon: Icon(Icons.explore_outlined), text: '탐색'),
  ])

  // Scrollable
  TabBar(
    isScrollable: true,
    tabAlignment: TabAlignment.start,
    tabs: [...],
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// [Tab 파라미터]
// text       — 텍스트 레이블 (height: 48dp)
// icon       — 아이콘 위젯 (icon-only: 46dp, icon+text: 72dp)
// iconMargin — 아이콘↔텍스트 간격 (기본: bottom 2dp)
// height     — 탭 높이 직접 지정 (icon/text 자동 높이 override)
// child      — 커스텀 위젯 (text/icon 대신)

// Primary Tabs — AppBar 하단 (기본, 테마 자동 적용)
DefaultTabController(
  length: 3,
  child: Scaffold(
    appBar: AppBar(
      bottom: TabBar(
        tabs: const [
          Tab(text: '홈'),
          Tab(text: '탐색'),
          Tab(text: '보관함'),
        ],
      ),
    ),
    body: const TabBarView(
      children: [HomeView(), ExploreView(), LibraryView()],
    ),
  ),
)

// Secondary Tabs — 화면 내 보조 탭
TabBar.secondary(
  controller: _tabController,
  tabs: const [
    Tab(text: '전체'),
    Tab(text: '최신'),
    Tab(text: '인기'),
  ],
)

// Scrollable Tabs — 탭이 많을 때 가로 스크롤
TabBar(
  isScrollable: true,
  tabAlignment: TabAlignment.start, // 왼쪽 정렬
  tabs: const [
    Tab(text: '전체'),
    Tab(text: '음악'),
    Tab(text: '영상'),
    Tab(text: '팟캐스트'),
    Tab(text: '라디오'),
  ],
)

// Icon-only Tabs — 46dp (icon 있고 text 없으면 자동)
TabBar(
  tabs: const [
    Tab(icon: Icon(Icons.home_outlined)),     // 24dp
    Tab(icon: Icon(Icons.explore_outlined)),
    Tab(icon: Icon(Icons.library_music_outlined)),
  ],
)

// Icon + Label Tabs — 아이콘 위 텍스트 아래, 72dp
TabBar(
  tabs: const [
    Tab(icon: Icon(Icons.home_outlined), text: '홈'),
    Tab(icon: Icon(Icons.explore_outlined), text: '탐색'),
    Tab(icon: Icon(Icons.library_music_outlined), text: '보관함'),
  ],
)

// Icon + Label — iconMargin으로 간격 조정
TabBar(
  tabs: [
    Tab(
      icon: const Icon(Icons.home_outlined),
      iconMargin: const EdgeInsets.only(bottom: 2.0), // 기본 2dp
      text: '홈',
    ),
  ],
)

// 명시적 토큰 적용 (테마 오버라이드 필요 시)
TabBar(
  labelColor: cs.primary,
  unselectedLabelColor: cs.onSurfaceVariant,
  indicatorColor: cs.primary,
  dividerColor: cs.outlineVariant,
  labelStyle: Theme.of(context).textTheme.titleSmall,
  tabs: const [Tab(text: '홈'), Tab(text: '탐색')],
)
```
