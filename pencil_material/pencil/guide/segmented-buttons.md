# Segmented Buttons

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/segmented-buttons/overview |
| Guidelines | https://m3.material.io/components/segmented-buttons/guidelines |
| Specs | https://m3.material.io/components/segmented-buttons/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Single select | `SegmentedButton<T>` |
| Multi-select | `SegmentedButton<T>` (multiSelectionEnabled: true) |

## 언제 사용하나요?

- 2~5개의 상호 연관된 옵션 중 하나(또는 여러 개)를 선택할 때
- 지도 뷰 타입, 차트 기간 선택 등 뷰 전환에 사용
- RadioButton 그룹보다 더 컴팩트하게 선택지를 표시하고 싶을 때
- 선택 상태가 즉각적으로 화면에 반영되는 토글 형태 UI

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비로 배치, 최대 5개 세그먼트 |
| Tablet (medium) | 고정 너비, 툴바 내 배치 가능 |
| Desktop/Web (expanded) | 동일, 호버 상태 지원 |

## Variants

- **Single-select** — 동시에 하나만 선택
- **Multi-select** — 동시에 여러 개 선택 가능

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Segmented Buttons Guide" 프레임을 만들어주세요.

모든 내용은 이 "Segmented Buttons Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/segmented-buttons/overview

---

## 프레임 설정
- 이름: "Segmented Buttons Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Segmented Buttons"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · segmented-buttons"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/segmented-buttons/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 2~5개의 상호 연관된 옵션 중 하나를 선택할 때
  · 지도 뷰 타입, 차트 기간 선택 등 뷰 전환에 사용
  · RadioButton 그룹보다 컴팩트하게 선택지를 표시하고 싶을 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 세로 나열, gap 24px

  ┌─ Single-select (너비 320dp) ──────────────────────────┐
  │  height: 40dp, border: 1dp Outline, corner: 20dp      │
  │  세그먼트 3개 균등 배치:                               │
  │  [Day (selected)]  [Week]  [Month]                    │
  │  selected: bg Secondary Container, check icon + label │
  │  unselected: bg transparent, label만                  │
  └────────────────────────────────────────────────────────┘

  ┌─ Multi-select (너비 320dp) ───────────────────────────┐
  │  height: 40dp, border: 1dp Outline, corner: 20dp      │
  │  세그먼트 4개:                                        │
  │  [Walk ✓]  [Ride ✓]  [Drive]  [Fly]                  │
  │  selected 2개: bg Secondary Container + check icon   │
  │  unselected: 투명 배경                                │
  └────────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Single-select (Day 선택)를 크게 그리고 번호 레이블 연결:
  1. Container — corner 20dp, outline border 1dp
  2. Selected segment — secondaryContainer 배경
  3. Check icon — 18dp, onSecondaryContainer
  4. Label — labelLarge (selected: onSecondaryContainer / unselected: onSurface)
  5. Segment dividers — 1dp, outline

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성               | 값                      | 토큰                                |
  |-------------------|-------------------------|-------------------------------------|
  | Height            | 40 dp                   | —                                   |
  | Corner radius     | 20 dp (pill)            | —                                   |
  | Border            | 1 dp                    | —                                   |
  | Border color      | outline                 | colorScheme.outline                 |
  | Check icon size   | 18 dp                   | AppIconSize.sm                      |
  | Label TextStyle   | labelLarge              | textTheme.labelLarge                |
  | Selected bg       | secondaryContainer      | colorScheme.secondaryContainer      |
  | Selected text     | onSecondaryContainer    | colorScheme.onSecondaryContainer    |
  | Unselected text   | onSurface               | colorScheme.onSurface               |
  | Segment count     | 2–5개                   | —                                   |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비, 최대 5개 세그먼트│
  │  → SegmentedButton         │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  고정 너비, 툴바 내 배치    │
  │  → SegmentedButton         │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  동일, 호버 상태 지원        │
  │  → SegmentedButton         │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Segmented Buttons Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  SegmentedButtons/2Segments — 2분할:
  · 컴포넌트 이름: "SegmentedButtons/2Segments"
  · 높이: 40dp, 너비: 360dp, corner: 20dp
  · 테두리: Outline 1dp, 세그먼트 구분선: Outline 1dp
  · 선택 배경: Secondary Container, 텍스트: On-Secondary-Container
  · 비선택 텍스트: On-Surface, 체크 아이콘: 18dp

  SegmentedButtons/3Segments — 3분할:
  · 컴포넌트 이름: "SegmentedButtons/3Segments"
  · 동일 구조, 세그먼트 3개 균등 배치

  SegmentedButtons/4Segments — 4분할:
  · 컴포넌트 이름: "SegmentedButtons/4Segments"
  · 동일 구조, 세그먼트 4개 균등 배치


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  SegmentedButton<String>(
    segments: const [
      ButtonSegment(value: 'day', label: Text('Day')),
      ButtonSegment(value: 'week', label: Text('Week')),
      ButtonSegment(value: 'month', label: Text('Month')),
    ],
    selected: {_selected},
    onSelectionChanged: (Set<String> val) {
      setState(() => _selected = val.first);
    },
  )

  // Multi-select
  SegmentedButton<String>(
    multiSelectionEnabled: true,
    segments: [...],
    selected: _selectedSet,
    onSelectionChanged: (val) => setState(() => _selectedSet = val),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

// Single-select — 기본 (테마 자동 적용)
SegmentedButton<String>(
  segments: const [
    ButtonSegment(value: 'day', label: Text('Day')),
    ButtonSegment(value: 'week', label: Text('Week')),
    ButtonSegment(value: 'month', label: Text('Month')),
  ],
  selected: {_selected},
  onSelectionChanged: (Set<String> val) {
    setState(() => _selected = val.first);
  },
)

// 아이콘 + 레이블 세그먼트
SegmentedButton<String>(
  segments: const [
    ButtonSegment(
      value: 'list',
      icon: Icon(Icons.list),
      label: Text('List'),
    ),
    ButtonSegment(
      value: 'grid',
      icon: Icon(Icons.grid_view),
      label: Text('Grid'),
    ),
  ],
  selected: {_viewMode},
  onSelectionChanged: (val) => setState(() => _viewMode = val.first),
)

// Multi-select — 여러 개 동시 선택
SegmentedButton<String>(
  multiSelectionEnabled: true,
  segments: const [
    ButtonSegment(value: 'walk', label: Text('Walk')),
    ButtonSegment(value: 'ride', label: Text('Ride')),
    ButtonSegment(value: 'drive', label: Text('Drive')),
  ],
  selected: _selectedModes,
  onSelectionChanged: (val) => setState(() => _selectedModes = val),
)

// emptySelectionAllowed — 모두 해제 가능
SegmentedButton<String>(
  emptySelectionAllowed: true,
  segments: const [
    ButtonSegment(value: 'a', label: Text('A')),
    ButtonSegment(value: 'b', label: Text('B')),
  ],
  selected: _selected,
  onSelectionChanged: (val) => setState(() => _selected = val),
)

// Disabled segment
SegmentedButton<String>(
  segments: const [
    ButtonSegment(value: 'day', label: Text('Day')),
    ButtonSegment(value: 'week', label: Text('Week'), enabled: false),
  ],
  selected: {_selected},
  onSelectionChanged: (val) => setState(() => _selected = val.first),
)
```
