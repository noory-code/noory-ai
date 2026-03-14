# Icon Buttons

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/icon-buttons/overview |
| Guidelines | https://m3.material.io/components/icon-buttons/guidelines |
| Specs | https://m3.material.io/components/icon-buttons/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Standard | `IconButton` |
| Filled | `IconButton.filled()` |
| Filled Tonal | `IconButton.filledTonal()` |
| Outlined | `IconButton.outlined()` |

## 언제 사용하나요?

- 레이블 없이 아이콘만으로 의미가 명확한 보조 액션에 사용할 때
- 북마크, 좋아요, 공유처럼 토글 가능한 선택 상태를 표현할 때
- 툴바, 앱바, 카드 내 컴팩트한 액션이 필요할 때
- 아이콘 의미가 불명확한 경우 Tooltip을 함께 사용할 것

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 최소 48dp 터치 타겟 확보 |
| Tablet (medium) | 동일, 툴바 밀도를 높여도 됨 |
| Desktop/Web (expanded) | 호버 상태 필수 지원, Tooltip 항상 표시 |

## Variants

- **Standard** — 배경 없음, 낮은 강조
- **Filled** — 채워진 배경, 높은 강조
- **Filled Tonal** — 보조 색상 배경, 중간 강조
- **Outlined** — 테두리, 중간 강조

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Icon Buttons Guide" 프레임을 만들어주세요.
모든 내용은 이 "Icon Buttons Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/icon-buttons/overview

---

## 프레임 설정
- 이름: "Icon Buttons Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Icon Buttons"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · icon-buttons"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/icon-buttons/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 레이블 없이 아이콘만으로 의미가 명확한 보조 액션에 사용할 때
  · 북마크, 좋아요처럼 토글 가능한 선택 상태를 표현할 때
  · 툴바, 앱바, 카드 내 컴팩트한 액션이 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 가로 나란히 배치, gap 20px

  ┌─ Standard ─────┐
  │  48×48dp touch │
  │  bg: none      │
  │  icon: 24dp    │
  │  (On-Surface-Variant)     │
  └─────────────────┘

  ┌─ Filled ───────┐
  │  40×40dp       │
  │  bg: Primary   │
  │  corner: full  │
  │  icon: 24dp    │
  │  (On-Primary)  │
  └─────────────────┘

  ┌─ Filled Tonal ─┐
  │  40×40dp       │
  │  bg: Secondary Container   │
  │  corner: full  │
  │  icon: 24dp    │
  │  (On-Secondary-Container) │
  └─────────────────┘

  ┌─ Outlined ─────┐
  │  40×40dp       │
  │  bg: none      │
  │  border: 1dp   │
  │  (Outline)     │
  │  corner: full  │
  │  icon: 24dp    │
  │  (On-Surface-Variant)     │
  └─────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Filled Icon Button을 크게 그리고 번호 레이블 연결:
  1. Container — 40×40dp, corner full (원형), Primary 배경
  2. Icon — 24dp, On-Primary 색상
  3. State layer — hover/focus/pressed 오버레이 (48×48dp 터치 영역)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | Standard | Filled/Tonal/Outlined |
  |------------------|----------|-----------------------|
  | Touch target     | 48 dp    | 48 dp                 |
  | Container size   | —        | 40 × 40 dp            |
  | Corner radius    | —        | full (원형, CircleBorder) |
  | Icon size        | 24 dp    | 24 dp                 |
  | Border (outlined)| —        | 1 dp                  |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  최소 48dp 터치 타겟 확보    │
  │  → IconButton              │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  동일, 툴바 밀도 높여도 됨   │
  │  → IconButton              │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  호버 필수, Tooltip 항상 표시│
  │  → IconButton + Tooltip    │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Icon Buttons Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  IconButtons/Standard — 배경 없음:
  · 컴포넌트 이름: "IconButtons/Standard"
  · 터치 타겟: 48×48dp (컨테이너 없음)
  · 아이콘: 24dp, On-Surface-Variant

  IconButtons/Filled — 채워진 배경:
  · 컴포넌트 이름: "IconButtons/Filled"
  · 컨테이너: 40×40dp, corner: full (원형)
  · 배경: Primary, 아이콘: 24dp, On-Primary

  IconButtons/FilledTonal — 보조 배경:
  · 컴포넌트 이름: "IconButtons/FilledTonal"
  · 컨테이너: 40×40dp, corner: full (원형)
  · 배경: Secondary Container, 아이콘: 24dp, On-Secondary-Container

  IconButtons/Outlined — 테두리:
  · 컴포넌트 이름: "IconButtons/Outlined"
  · 컨테이너: 40×40dp, corner: full (원형)
  · 배경: 투명, 테두리: Outline 1dp, 아이콘: 24dp, On-Surface-Variant


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  IconButton(icon: Icon(Icons.favorite), onPressed: () {})
  IconButton.filled(icon: Icon(Icons.favorite), onPressed: () {})
  IconButton.filledTonal(icon: Icon(Icons.favorite), onPressed: () {})
  IconButton.outlined(icon: Icon(Icons.favorite), onPressed: () {})

  // Toggle
  IconButton(
    isSelected: isSelected,
    icon: Icon(Icons.favorite_border),
    selectedIcon: Icon(Icons.favorite),
    onPressed: () => setState(() => isSelected = !isSelected),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Standard — 배경 없음
IconButton(
  iconSize: AppIconSize.md, // 24dp
  icon: const Icon(Icons.favorite),
  color: cs.onSurfaceVariant,
  onPressed: () {},
)

// Filled — Primary 배경 (원형)
IconButton.filled(
  iconSize: AppIconSize.md,
  icon: const Icon(Icons.favorite),
  onPressed: () {},
)

// Filled Tonal — Secondary Container 배경 (원형)
IconButton.filledTonal(
  iconSize: AppIconSize.md,
  icon: const Icon(Icons.favorite),
  onPressed: () {},
)

// Outlined — 테두리 (원형)
IconButton.outlined(
  iconSize: AppIconSize.md,
  icon: const Icon(Icons.favorite),
  onPressed: () {},
)

// Toggle — isSelected + selectedIcon
IconButton.filled(
  isSelected: isSelected,
  icon: const Icon(Icons.favorite_border),
  selectedIcon: const Icon(Icons.favorite),
  onPressed: () => setState(() => isSelected = !isSelected),
)

// Disabled — onPressed: null
IconButton.filled(
  icon: const Icon(Icons.favorite),
  onPressed: null,
)
```
