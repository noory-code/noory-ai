# Search

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/search/overview |
| Guidelines | https://m3.material.io/components/search/guidelines |
| Specs | https://m3.material.io/components/search/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Search bar | `SearchBar` |
| Search with suggestions | `SearchAnchor` |

## 언제 사용하나요?

- 앱 내 콘텐츠를 키워드로 빠르게 탐색해야 할 때
- 자동완성 또는 최근 검색어 제안이 필요할 때
- 앱바 내 검색, 혹은 화면 상단 독립 검색바가 필요할 때
- 필터링과 검색을 함께 제공하는 복합 검색 UI가 필요할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 SearchBar, 탭 시 전체 화면 SearchView |
| Tablet (medium) | 고정 너비 SearchBar (최대 720dp), 드롭다운 SearchView |
| Desktop/Web (expanded) | 상단 중앙 고정 SearchBar, 드롭다운 결과 목록 |

## Variants

- **Search bar** — 항상 표시되는 검색 입력 필드
- **Search view** — 검색 시 전체화면 또는 드롭다운으로 확장

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Search Guide" 프레임을 만들어주세요.
모든 내용은 이 "Search Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/search/overview

---

## 프레임 설정
- 이름: "Search Guide"
- 배경: Surface 색상 (Color Scheme 참조)
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Search"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · search"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/search/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 앱 내 콘텐츠를 키워드로 빠르게 탐색해야 할 때
  · 자동완성 또는 최근 검색어 제안이 필요할 때
  · 필터링과 검색을 함께 제공하는 복합 검색 UI가 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 세로 나열, gap 24px

  ┌─ Search Bar (너비 360dp) ──────────┐
  │  height: 56dp                       │
  │  배경: Search Container (Surface) │
  │  corner: 28dp (full pill)           │
  │  leading: 검색 아이콘 (24dp)        │
  │  placeholder: "Search..." (16sp)   │
  │  trailing: avatar/mic 아이콘        │
  │  shadow: elevation 1               │
  └────────────────────────────────────┘

  ┌─ Search View (너비 360dp, h 500dp) ┐
  │  상단 SearchBar (고정)              │
  │  아래: 검색 결과 / 추천 목록        │
  │  배경: Surface                     │
  │  결과 아이템: ListTile 형식        │
  │  구분선: Outline Variant           │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Search Bar를 크게 그리고 번호 레이블 연결:
  1. Container — pill shape, corner 28dp, surfaceContainerHigh 배경
  2. Leading icon — 검색 아이콘 24dp, onSurfaceVariant
  3. Placeholder / Input — bodyLarge, onSurfaceVariant / onSurface
  4. Trailing element — avatar, mic, clear 아이콘 (onSurfaceVariant)
  5. Shadow — elevation Level 1

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | 값                      | 토큰                                  |
  |------------------|-------------------------|---------------------------------------|
  | Height           | 56 dp                   | —                                     |
  | Corner radius    | 28 dp (pill)            | —                                     |
  | Leading icon     | 24 dp                   | AppIconSize.md                        |
  | Input TextStyle  | bodyLarge               | textTheme.bodyLarge                   |
  | Elevation        | Level 1                 | AppElevation.level1                   |
  | Container bg     | surfaceContainerHigh    | colorScheme.surfaceContainerHigh      |
  | Icon color       | onSurfaceVariant        | colorScheme.onSurfaceVariant          |
  | Text color       | onSurface               | colorScheme.onSurface                 |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비, 탭 시 전체화면  │
  │  → SearchBar + SearchAnchor│
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  고정 너비 (최대 720dp)     │
  │  → SearchBar + SearchAnchor│
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  상단 중앙 고정, 드롭다운   │
  │  → SearchBar + SearchAnchor│
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Search Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Search/Bar — 상단 고정형:
  · 컴포넌트 이름: "Search/Bar"
  · 높이: 56dp, 너비: 360dp, corner: 28dp (pill)
  · 배경: Surface Container High
  · Leading: 검색 아이콘 24dp, On-Surface-Variant
  · Placeholder: 16sp, On-Surface-Variant
  · Elevation: Level 1

  Search/View — 전체 화면 확장형:
  · 컴포넌트 이름: "Search/View"
  · 상단 Bar 영역: 56dp (Bar와 동일)
  · 결과 목록: Surface 배경, ListTile 형식
  · 구분선: Outline Variant


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  SearchAnchor(
    builder: (context, controller) => SearchBar(
      controller: controller,
      hintText: 'Search...',
      leading: Icon(Icons.search),
      onTap: () => controller.openView(),
    ),
    suggestionsBuilder: (context, controller) => [
      ListTile(title: Text('Recent search 1')),
      ListTile(title: Text('Recent search 2')),
    ],
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// SearchBar + SearchAnchor — 기본 (M3, Flutter 3.10+)
SearchAnchor(
  builder: (context, controller) => SearchBar(
    controller: controller,
    hintText: '검색',
    leading: const Icon(Icons.search, size: AppIconSize.md),
    padding: const WidgetStatePropertyAll(
      EdgeInsets.symmetric(horizontal: AppSpacing.base),
    ),
    elevation: const WidgetStatePropertyAll(AppElevation.level1),
    onTap: () => controller.openView(),
    onChanged: (_) => controller.openView(),
  ),
  suggestionsBuilder: (context, controller) => [
    ListTile(
      leading: const Icon(Icons.history),
      title: const Text('최근 검색어 1'),
      onTap: () => controller.closeView('최근 검색어 1'),
    ),
    ListTile(
      leading: const Icon(Icons.history),
      title: const Text('최근 검색어 2'),
      onTap: () => controller.closeView('최근 검색어 2'),
    ),
  ],
)

// trailing — 마이크 + 지우기 버튼
SearchBar(
  hintText: '검색',
  leading: const Icon(Icons.search, size: AppIconSize.md),
  trailing: [
    IconButton(
      icon: const Icon(Icons.mic, size: AppIconSize.md),
      onPressed: () {},
    ),
    if (_query.isNotEmpty)
      IconButton(
        icon: const Icon(Icons.close, size: AppIconSize.md),
        onPressed: () => _controller.clear(),
      ),
  ],
  onChanged: (q) => setState(() => _query = q),
)

// SearchBar 단독 사용 (제안 없음)
SearchBar(
  hintText: '검색',
  leading: const Icon(Icons.search, size: AppIconSize.md),
  onSubmitted: (query) {
    // 검색 실행
  },
)
```
