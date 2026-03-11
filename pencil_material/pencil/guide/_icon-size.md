# Icon Size

## M3 링크

| 페이지 | URL |
|--------|-----|
| Icons | https://m3.material.io/styles/icons/overview |
| Icon Button | https://m3.material.io/components/icon-buttons/overview |

## 토큰 정의

| 토큰 | 값 | 주요 용도 |
|------|-----|---------|
| $icon/sm | 18 dp | 버튼 내 Leading/Trailing 아이콘, 인라인 텍스트 옆 |
| $icon/base | 20 dp | 작은 IconButton, Chip 아이콘 |
| $icon/md | 24 dp | 기본 아이콘 크기 (NavigationBar, AppBar, ListTile) |
| $icon/lg | 36 dp | 강조 아이콘, 빈 상태 화면 보조 |
| $icon/xl | 48 dp | 빈 상태 화면 메인, 온보딩 일러스트 대체 |

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Icon Size Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/styles/icons/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다:

| 변수명 | 값 |
|--------|-----|
| $icon/sm | 18 |
| $icon/base | 20 |
| $icon/md | 24 |
| $icon/lg | 36 |
| $icon/xl | 48 |

---

## 프레임 설정
- 이름: "Icon Size Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Icon Size"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · 아이콘 크기 토큰"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/styles/icons/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · sm (18dp) — 버튼 내 Leading/Trailing 아이콘, 인라인 텍스트 옆 아이콘
  · base (20dp) — 작은 IconButton, Chip 내 아이콘
  · md (24dp) — 기본값. NavigationBar, AppBar, ListTile 아이콘
  · lg (36dp) — 강조 아이콘, 빈 상태 화면 보조 아이콘
  · xl (48dp) — 빈 상태 화면 메인 아이콘, 온보딩 화면

---

## 섹션 3 — Size Scale
- 소제목: "Size Scale"  (20px, 600)
- 5개 아이콘 가로 나열, 하단 정렬, gap 32px:

  각 아이콘:
  - 아이콘: favorite (Material Symbol) 또는 동등한 심볼
  - 색상: On-Surface
  - 아이콘 크기: 토큰 값에 해당 (18/20/24/36/48dp)
  - 아이콘 아래 토큰명 레이블: 12px, On-Surface-Variant
  - 토큰명 아래 값: 12px, Primary

  좌→우: $icon/sm (18dp) · $icon/base (20dp) · $icon/md (24dp) · $icon/lg (36dp) · $icon/xl (48dp)

---

## 섹션 4 — Context Examples
- 소제목: "Context Examples"  (20px, 600)
- 3개 예시 가로 배치, gap 24px:

  ┌─ AppBar 아이콘 ────────────────┐
  │  [← 아이콘 24dp] AppBar Title  │
  │  $icon/md = 24dp               │
  └────────────────────────────────┘

  ┌─ 버튼 Leading 아이콘 ─────────┐
  │  [아이콘 18dp] Label           │
  │  $icon/sm = 18dp               │
  └────────────────────────────────┘

  ┌─ 빈 상태 화면 ─────────────────┐
  │       [아이콘 48dp]             │
  │  "결과가 없습니다"              │
  │  $icon/xl = 48dp               │
  └────────────────────────────────┘

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 토큰 | 크기 | 터치 영역 | 주요 용도 |
  |------|------|---------|---------|
  | $icon/sm | 18 dp | — | 버튼 Leading, 인라인 |
  | $icon/base | 20 dp | — | 작은 IconButton, Chip |
  | $icon/md | 24 dp | 48×48 dp | 기본 (AppBar, Nav, List) |
  | $icon/lg | 36 dp | — | 강조 아이콘 |
  | $icon/xl | 48 dp | — | Empty State, 온보딩 |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppIconSize 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // Icon sizes
  Icon(Icons.favorite, size: AppIconSize.sm)    // 18dp
  Icon(Icons.favorite, size: AppIconSize.base)  // 20dp
  Icon(Icons.favorite, size: AppIconSize.md)    // 24dp (기본값)
  Icon(Icons.favorite, size: AppIconSize.lg)    // 36dp
  Icon(Icons.favorite, size: AppIconSize.xl)    // 48dp

  // Button with leading icon
  FilledButton.icon(
    onPressed: () {},
    icon: Icon(Icons.add, size: AppIconSize.sm), // 18dp
    label: Text('Label'),
  )

  // Empty state with colorScheme
  Icon(
    Icons.inbox_outlined,
    size: AppIconSize.xl,  // 48dp
    color: Theme.of(context).colorScheme.onSurfaceVariant,
  )
