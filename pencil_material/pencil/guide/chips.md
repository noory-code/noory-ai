# Chips

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/chips/overview |
| Guidelines | https://m3.material.io/components/chips/guidelines |
| Specs | https://m3.material.io/components/chips/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 | Elevated 지원 |
|-----------|-------------|--------------|
| Assist | `ActionChip` | `ActionChip.elevated()` ✅ |
| Filter | `FilterChip` | `FilterChip.elevated()` ✅ |
| Input | `InputChip` | ❌ 없음 |
| Suggestion | `ChoiceChip` | `ChoiceChip.elevated()` ✅ |

## 언제 사용하나요?

- **Filter** — 콘텐츠를 태그/카테고리로 필터링할 때
- **Input** — 이메일 수신자, 태그 입력 등 사용자 입력값을 표현할 때
- **Suggestion** — 검색어 자동완성, 빠른 응답 선택지를 제안할 때
- **Assist** — 현재 컨텍스트에서 스마트 액션을 제공할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 가로 스크롤 Chip 행 또는 Wrap 레이아웃 |
| Tablet (medium) | Wrap 레이아웃, 여러 행 허용 |
| Desktop/Web (expanded) | Wrap 레이아웃, 호버 상태 지원, 고정 필터 패널 고려 |

## Variants

- Assist (ActionChip) / Filter (FilterChip) / Input (InputChip) / Suggestion (ChoiceChip)
- 각 Variant에 Elevated 변형 존재 (InputChip 제외)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Chips Guide" 프레임을 만들어주세요.
모든 내용은 이 "Chips Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/chips/overview

---

## 프레임 설정
- 이름: "Chips Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Chips"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · chips"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/chips/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · Filter — 콘텐츠를 태그/카테고리로 필터링할 때
  · Input — 이메일 수신자, 태그처럼 사용자 입력값을 표현할 때
  · Suggestion — 검색어 자동완성, 빠른 응답 선택지를 제안할 때
  · Assist — 현재 컨텍스트에서 스마트 액션을 제공할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 가로 나란히 배치, gap 16px

  ┌─ Assist ─────────────────┐
  │  height: 32dp             │
  │  bg: Surface (투명)        │
  │  border: 1dp, Outline Variant   │
  │  corner: 8dp              │
  │  leading icon: 18dp       │
  │  label: "Assist" (14sp)  │
  │  hpad: 8dp                │
  └───────────────────────────┘

  ┌─ Filter ─────────────────┐
  │  height: 32dp             │
  │  selected bg: Secondary Container │
  │  unselected bg: Surface (투명) │
  │  border: 1dp, Outline Variant   │
  │  corner: 8dp              │
  │  showCheckmark: true (선택시) │
  │  check icon: 18dp         │
  │  label: "Filter" (14sp)  │
  └───────────────────────────┘

  ┌─ Input ──────────────────┐
  │  height: 32dp             │
  │  bg: Surface (투명)        │
  │  border: 1dp, Outline Variant │
  │  corner: 8dp              │
  │  leading avatar: 24dp     │
  │  label: "Input" (14sp)   │
  │  trailing X: 18dp         │
  └───────────────────────────┘

  ┌─ Suggestion ─────────────┐
  │  height: 32dp             │
  │  unselected bg: Surface (투명) │
  │  selected bg: Primary Container │
  │  border: 1dp, Outline Variant   │
  │  corner: 8dp              │
  │  label: "Choice" (14sp)  │
  └───────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Filter Chip (selected)을 크게 그리고 번호 레이블 연결:
  1. Container — height 32dp, corner 8dp, secondaryContainer 배경
  2. Leading icon / check — 18dp 아이콘 (onSecondaryContainer)
  3. Label — labelLarge (onSecondaryContainer selected / onSurface unselected)
  4. Trailing icon (선택) — X 아이콘 18dp (InputChip, onSurface)
  5. State layer — hover/focus/pressed 오버레이

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                        | 값                      | 토큰                                |
  |----------------------------|-------------------------|-------------------------------------|
  | Height                     | 32 dp                   | —                                   |
  | Corner radius              | 8 dp                    | —                                   |
  | Horizontal pad             | 8–16 dp                 | —                                   |
  | Icon size                  | 18 dp                   | AppIconSize.sm                      |
  | Label TextStyle            | labelLarge              | textTheme.labelLarge                |
  | Border color (unselected)  | outlineVariant          | colorScheme.outlineVariant          |
  | Filter selected bg         | secondaryContainer      | colorScheme.secondaryContainer      |
  | Filter selected text       | onSecondaryContainer    | colorScheme.onSecondaryContainer    |
  | Suggestion selected bg     | primaryContainer        | colorScheme.primaryContainer        |
  | Suggestion selected text   | onPrimaryContainer      | colorScheme.onPrimaryContainer      |
  | materialTapTargetSize      | shrinkWrap              | —                                   |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  가로 스크롤 Chip 행 또는 Wrap│
  │  → Wrap + FilterChip       │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Wrap 레이아웃, 여러 행 허용  │
  │  → Wrap + FilterChip       │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  호버 지원, 고정 필터 패널 고려│
  │  → Wrap + FilterChip       │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Chips Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트를 행별로 배치, 각 행 gap 16px, 행 간격 24px:

  [행 1 — Assist 계열]

  Chips/Assist — 스마트 액션:
  · 컴포넌트 이름: "Chips/Assist"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: 투명, 테두리: Outline 1dp
  · leading icon: 18dp (On-Surface), 레이블 색상: On-Surface (14sp)

  Chips/Assist/Elevated — Elevated 스타일:
  · 컴포넌트 이름: "Chips/Assist/Elevated"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Surface Container Low, 그림자: elevation 1dp
  · leading icon: 18dp, 레이블 색상: On-Surface

  Chips/Assist/Disabled — 비활성:
  · 컴포넌트 이름: "Chips/Assist/Disabled"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: On-Surface opacity 12%, 테두리: Outline opacity 12%
  · 레이블 색상: On-Surface opacity 38%

  [행 2 — Filter 계열]

  Chips/Filter — 필터 (비선택):
  · 컴포넌트 이름: "Chips/Filter"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: 투명, 테두리: Outline 1dp, 레이블 색상: On-Surface

  Chips/Filter/Selected — 필터 (선택):
  · 컴포넌트 이름: "Chips/Filter/Selected"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Secondary Container, 체크 아이콘: 18dp, On-Secondary-Container
  · 레이블 색상: On-Secondary-Container

  Chips/Filter/Elevated — Elevated 필터 (비선택):
  · 컴포넌트 이름: "Chips/Filter/Elevated"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Surface Container Low, 그림자: elevation 1dp, 레이블 색상: On-Surface

  Chips/Filter/Elevated/Selected — Elevated 필터 (선택):
  · 컴포넌트 이름: "Chips/Filter/Elevated/Selected"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Secondary Container, 그림자: elevation 1dp
  · 체크 아이콘: 18dp, 레이블 색상: On-Secondary-Container

  Chips/Filter/Disabled — 비활성:
  · 컴포넌트 이름: "Chips/Filter/Disabled"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: On-Surface opacity 12%, 테두리: Outline opacity 12%
  · 레이블 색상: On-Surface opacity 38%

  [행 3 — Input 계열]

  Chips/Input — 입력 태그:
  · 컴포넌트 이름: "Chips/Input"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: 투명, 테두리: Outline 1dp
  · leading avatar: 24dp, trailing X: 18dp, 레이블 색상: On-Surface

  Chips/Input/Disabled — 비활성:
  · 컴포넌트 이름: "Chips/Input/Disabled"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: On-Surface opacity 12%, 테두리: Outline opacity 12%
  · 레이블 색상: On-Surface opacity 38%

  [행 4 — Suggestion 계열]

  Chips/Suggestion — 제안 (비선택):
  · 컴포넌트 이름: "Chips/Suggestion"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: 투명, 테두리: Outline 1dp, 레이블 색상: On-Surface

  Chips/Suggestion/Selected — 제안 (선택):
  · 컴포넌트 이름: "Chips/Suggestion/Selected"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Primary Container, 테두리 없음
  · 레이블 색상: On-Primary-Container

  Chips/Suggestion/Elevated — Elevated 제안:
  · 컴포넌트 이름: "Chips/Suggestion/Elevated"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: Surface Container Low, 그림자: elevation 1dp, 레이블 색상: On-Surface

  Chips/Suggestion/Disabled — 비활성:
  · 컴포넌트 이름: "Chips/Suggestion/Disabled"
  · 높이: 32dp, corner: 8dp, 수평 패딩: 8dp
  · 배경: On-Surface opacity 12%, 테두리: Outline opacity 12%
  · 레이블 색상: On-Surface opacity 38%

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Assist
  ActionChip(label: Text('Assist'), onPressed: () {})
  ActionChip.elevated(label: Text('Assist'), onPressed: () {})

  // Filter (showCheckmark: true가 기본)
  FilterChip(label: Text('Filter'), selected: false, onSelected: (v) {})
  FilterChip(label: Text('Filter'), selected: true, showCheckmark: true, onSelected: (v) {})
  FilterChip.elevated(label: Text('Filter'), selected: isSelected, onSelected: (v) {})

  // Input (elevated 없음)
  InputChip(label: Text('Input'), onDeleted: () {})

  // Suggestion
  ChoiceChip(label: Text('Choice'), selected: false, onSelected: (v) {})
  ChoiceChip(label: Text('Choice'), selected: true, onSelected: (v) {})
  ChoiceChip.elevated(label: Text('Choice'), selected: isSelected, onSelected: (v) {})

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// FilterChip — M3 Filter
// selectedColor: SecondaryContainer (Filter 전용)
FilterChip(
  label: const Text('전체'),
  selected: isSelected,
  showCheckmark: true,
  selectedColor: cs.secondaryContainer,
  checkmarkColor: cs.onSecondaryContainer,
  labelStyle: TextStyle(
    color: isSelected ? cs.onSecondaryContainer : cs.onSurface,
  ),
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8.0), // AppRadius.xs
    side: BorderSide(
      color: isSelected ? Colors.transparent : cs.outline,
    ),
  ),
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onSelected: (v) => setState(() => isSelected = v),
)

// FilterChip.elevated — M3 Filter Elevated
FilterChip.elevated(
  label: const Text('전체'),
  selected: isSelected,
  showCheckmark: true,
  selectedColor: cs.secondaryContainer,
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onSelected: (v) => setState(() => isSelected = v),
)

// ChoiceChip — M3 Suggestion
// ⚠️ selectedColor: PrimaryContainer (SecondaryContainer 아님!)
ChoiceChip(
  label: const Text('추천어'),
  selected: isSelected,
  selectedColor: cs.primaryContainer,
  labelStyle: TextStyle(
    color: isSelected ? cs.onPrimaryContainer : cs.onSurface,
  ),
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8.0),
    side: BorderSide(
      color: isSelected ? Colors.transparent : cs.outline,
    ),
  ),
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onSelected: (v) => setState(() => isSelected = v),
)

// ActionChip — M3 Assist
ActionChip(
  label: const Text('스마트 액션'),
  avatar: Icon(Icons.auto_awesome, size: AppIconSize.sm), // 18dp
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8.0),
    side: BorderSide(color: cs.outline),
  ),
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onPressed: () {},
)

// ActionChip.elevated — M3 Assist Elevated
ActionChip.elevated(
  label: const Text('스마트 액션'),
  avatar: Icon(Icons.auto_awesome, size: AppIconSize.sm),
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onPressed: () {},
)

// InputChip — M3 Input (삭제 가능 태그)
// ⚠️ InputChip.elevated() 없음
InputChip(
  label: const Text('Flutter'),
  avatar: Icon(Icons.label, size: AppIconSize.sm), // 18dp
  deleteIcon: Icon(Icons.close, size: AppIconSize.sm), // 18dp
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8.0),
    side: BorderSide(color: cs.outline),
  ),
  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
  onDeleted: () {},
  onPressed: () {},
)

// Disabled — callback을 null로 설정
ActionChip(label: Text('Disabled'), onPressed: null)
FilterChip(label: Text('Disabled'), selected: false, onSelected: null)
InputChip(label: Text('Disabled'), onDeleted: null, onPressed: null)
ChoiceChip(label: Text('Disabled'), selected: false, onSelected: null)
```
