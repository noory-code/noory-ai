# Floating Action Button

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/floating-action-button/overview |
| Guidelines | https://m3.material.io/components/floating-action-button/guidelines |
| Specs | https://m3.material.io/components/floating-action-button/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| FAB (standard) | `FloatingActionButton` |
| Small FAB | `FloatingActionButton.small()` |
| Large FAB | `FloatingActionButton.large()` |
| Extended FAB | `FloatingActionButton.extended()` |

## 언제 사용하나요?

- 화면에서 가장 중요하고 자주 사용하는 단일 액션을 강조할 때
- 글쓰기, 추가, 촬영처럼 콘텐츠 생성 액션에 사용할 때
- 스크롤해도 항상 접근 가능해야 하는 핵심 액션일 때
- 한 화면에 하나만 배치 (여러 개 지양)

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 우하단 FAB 또는 Extended FAB |
| Tablet (medium) | Extended FAB (레이블 포함), NavigationRail 위에 배치 가능 |
| Desktop/Web (expanded) | Extended FAB, 사이드 고정 또는 콘텐츠 영역 내 배치 |

> 태블릿/데스크탑에서는 Extended FAB(텍스트 레이블 포함)를 사용해 액션 의미를 명확히.

## Variants

- **FAB** — 표준 크기 (56dp)
- **Small FAB** — 작은 크기 (40dp)
- **Large FAB** — 큰 크기 (96dp)
- **Extended FAB** — 아이콘 + 텍스트 레이블

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Floating Action Button Guide" 프레임을 만들어주세요.
모든 내용은 이 "Floating Action Button Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/floating-action-button/overview

---

## 프레임 설정
- 이름: "Floating Action Button Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Floating Action Button"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · floating-action-button"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/floating-action-button/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 화면에서 가장 중요하고 자주 사용하는 단일 액션을 강조할 때
  · 글쓰기, 추가, 촬영처럼 콘텐츠 생성 액션에 사용할 때
  · 스크롤해도 항상 접근 가능해야 하는 핵심 액션일 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 가로 나란히 배치, gap 20px

  ┌─ FAB (Standard) ──┐
  │  56×56dp          │
  │  bg: Primary Container      │
  │  (Primary Cont.)  │
  │  corner: 16dp     │
  │  shadow: level 3  │
  │  + 아이콘 24dp    │
  │  (On-Primary-Container)        │
  └────────────────────┘

  ┌─ Small FAB ───────┐
  │  40×40dp          │
  │  bg: Primary Container      │
  │  corner: 12dp     │
  │  shadow: level 3  │
  │  + 아이콘 24dp    │
  └────────────────────┘

  ┌─ Large FAB ───────┐
  │  96×96dp          │
  │  bg: Primary Container      │
  │  corner: 28dp     │
  │  shadow: level 3  │
  │  + 아이콘 36dp    │
  └────────────────────┘

  ┌─ Extended FAB ────────────┐
  │  height: 56dp             │
  │  bg: Primary Container              │
  │  corner: 16dp             │
  │  shadow: level 3          │
  │  leading: + 아이콘 24dp   │
  │  label: "New message"    │
  │  (14sp, On-Primary-Container)         │
  │  hpad: 16dp               │
  └───────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Extended FAB를 크게 그리고 번호 레이블 연결:
  1. Container — Primary Container 배경, corner 16dp, elevation 3
  2. Icon — 24dp, On-Primary-Container
  3. Label — 14sp, On-Primary-Container (Extended만 해당)
  4. Shadow — elevation 3 (dp3)
  5. State layer — hover/pressed 오버레이

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | Small | FAB  | Large | Extended |
  |------------------|-------|------|-------|----------|
  | Size             | 40dp  | 56dp | 96dp  | 56dp H   |
  | Corner radius    | 12dp  | 16dp | 28dp  | 16dp     |
  | Icon size        | 24dp  | 24dp | 36dp  | 24dp     |
  | Elevation        | dp3   | dp3  | dp3   | dp3      |
  | Color            | Primary Container 모두 동일 |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  우하단 FAB 또는 Extended FAB│
  │  → FloatingActionButton    │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Extended FAB, NavRail 위  │
  │  → FloatingActionButton.extended │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Extended FAB, 사이드 고정  │
  │  → FloatingActionButton.extended │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Floating Action Button Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  FAB/Small — 소형:
  · 컴포넌트 이름: "FAB/Small"
  · 크기: 40×40dp, corner: 12dp
  · 배경: Primary Container, 아이콘: 24dp, On-Primary-Container
  · Elevation: Level 3

  FAB/Default — 표준:
  · 컴포넌트 이름: "FAB/Default"
  · 크기: 56×56dp, corner: 16dp
  · 배경: Primary Container, 아이콘: 24dp, On-Primary-Container
  · Elevation: Level 3

  FAB/Large — 대형:
  · 컴포넌트 이름: "FAB/Large"
  · 크기: 96×96dp, corner: 28dp
  · 배경: Primary Container, 아이콘: 36dp, On-Primary-Container
  · Elevation: Level 3

  FAB/Extended — 텍스트 포함:
  · 컴포넌트 이름: "FAB/Extended"
  · 높이: 56dp, 가변 너비, corner: 16dp
  · 배경: Primary Container, leading 아이콘 24dp + 레이블 14sp, On-Primary-Container
  · 수평 패딩: 16dp, Elevation: Level 3


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  FloatingActionButton(onPressed: () {}, child: Icon(Icons.add))
  FloatingActionButton.small(onPressed: () {}, child: Icon(Icons.add))
  FloatingActionButton.large(onPressed: () {}, child: Icon(Icons.add))
  FloatingActionButton.extended(
    onPressed: () {},
    icon: Icon(Icons.edit),
    label: Text('New message'),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Standard FAB — Primary (기본)
FloatingActionButton(
  elevation: AppElevation.level2,          // 3dp resting
  highlightElevation: AppElevation.level3, // 6dp pressed
  backgroundColor: cs.primaryContainer,
  foregroundColor: cs.onPrimaryContainer,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.md), // 16dp
  ),
  onPressed: () {},
  child: Icon(Icons.add, size: AppIconSize.md), // 24dp
)

// Small FAB
FloatingActionButton.small(
  elevation: AppElevation.level2,
  highlightElevation: AppElevation.level3,
  backgroundColor: cs.primaryContainer,
  foregroundColor: cs.onPrimaryContainer,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.sm), // 12dp
  ),
  onPressed: () {},
  child: Icon(Icons.add, size: AppIconSize.md),
)

// Large FAB
FloatingActionButton.large(
  elevation: AppElevation.level2,
  highlightElevation: AppElevation.level3,
  backgroundColor: cs.primaryContainer,
  foregroundColor: cs.onPrimaryContainer,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.xl), // 28dp
  ),
  onPressed: () {},
  child: Icon(Icons.add, size: AppIconSize.lg), // 36dp
)

// Extended FAB
FloatingActionButton.extended(
  elevation: AppElevation.level2,
  highlightElevation: AppElevation.level3,
  backgroundColor: cs.primaryContainer,
  foregroundColor: cs.onPrimaryContainer,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(AppRadius.md), // 16dp
  ),
  onPressed: () {},
  icon: Icon(Icons.add, size: AppIconSize.md),
  label: const Text('추가하기'),
)

// FAB 색상 변형 — Secondary / Tertiary / Surface
FloatingActionButton(
  backgroundColor: cs.secondaryContainer, // Secondary 변형
  foregroundColor: cs.onSecondaryContainer,
  onPressed: () {},
  child: const Icon(Icons.edit),
)
FloatingActionButton(
  backgroundColor: cs.tertiaryContainer,  // Tertiary 변형
  foregroundColor: cs.onTertiaryContainer,
  onPressed: () {},
  child: const Icon(Icons.star),
)
FloatingActionButton(
  backgroundColor: cs.surface,            // Surface 변형
  foregroundColor: cs.primary,
  onPressed: () {},
  child: const Icon(Icons.add),
)
```
