# Tooltips

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/tooltips/overview |
| Guidelines | https://m3.material.io/components/tooltips/guidelines |
| Specs | https://m3.material.io/components/tooltips/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Plain tooltip | `Tooltip` |
| Rich tooltip | `Tooltip` (richMessage 파라미터) |

## 언제 사용하나요?

- 아이콘 버튼처럼 레이블이 없는 UI 요소의 기능을 설명할 때
- 사용자가 길게 누르거나 마우스를 올렸을 때 보조 힌트를 제공할 때
- 한 문장 이내로 간결하게 맥락 정보를 전달할 때
- 필수가 아닌 선택적 보조 설명에만 사용할 것 (필수 정보는 레이블 사용)

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 길게 누르기(500ms)로 Tooltip 표시 |
| Tablet (medium) | 길게 누르기 또는 호버 |
| Desktop/Web (expanded) | **호버 시 항상 Tooltip 표시** — 필수 (마우스 환경) |

> 데스크탑/웹에서 아이콘 버튼에는 반드시 Tooltip 제공.

## Variants

- **Plain** — 짧은 텍스트 툴팁
- **Rich** — 제목 + 본문 + 버튼 포함 가능한 확장형 툴팁

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Tooltips Guide" 프레임을 만들어주세요.

모든 내용은 이 "Tooltips Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/tooltips/overview

---

## 프레임 설정
- 이름: "Tooltips Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Tooltips"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · tooltips"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/tooltips/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 아이콘 버튼처럼 레이블이 없는 UI 요소의 기능을 설명할 때
  · 사용자가 길게 누르거나 마우스를 올렸을 때 보조 힌트를 제공할 때
  · 한 문장 이내로 간결하게 맥락 정보를 전달할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 32px

  ┌─ Plain Tooltip ────────────────────┐
  │  아이콘 버튼 위에 tooltip 표시      │
  │  tooltip 박스: corner 4dp          │
  │  배경: Inverse Surface             │
  │  텍스트: "Add to favorites"        │
  │  (12sp, Inverse On-Surface)        │
  │  hpad: 8dp, vpad: 4dp             │
  │  화살표: 아래쪽 삼각형 (선택)       │
  └────────────────────────────────────┘

  ┌─ Rich Tooltip ─────────────────────┐
  │  넓은 tooltip 박스 (max 240dp)      │
  │  배경: Surface Container High       │
  │  corner: 4dp, shadow: dp2          │
  │  제목: "Title" (14sp bold)          │
  │  본문: 설명 텍스트 (12sp)           │
  │  하단 버튼: "Learn more" (TextBtn) │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Plain Tooltip을 크게 그리고 번호 레이블 연결:
  1. Container — corner 4dp, inverseSurface 배경
  2. Label text — bodySmall (onInverseSurface)
  3. Caret (선택) — 삼각형 화살표

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                | Plain               | Rich                  | 토큰 (Plain)                    |
  |--------------------|---------------------|-----------------------|---------------------------------|
  | Max width          | 200 dp              | 320 dp                | —                               |
  | Corner radius      | 4 dp                | 4 dp                  | —                               |
  | Vertical padding   | 4 dp                | 12 dp                 | —                               |
  | Horizontal padding | 8 dp                | 16 dp                 | —                               |
  | Label TextStyle    | bodySmall           | bodySmall / titleSmall| textTheme.bodySmall             |
  | Container bg       | inverseSurface      | surfaceContainerHigh  | colorScheme.inverseSurface      |
  | Label color        | onInverseSurface    | onSurface             | colorScheme.onInverseSurface    |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  길게 누르기(500ms)로 표시  │
  │  → Tooltip                 │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  길게 누르기 또는 호버      │
  │  → Tooltip                 │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  호버 시 항상 표시 (필수)   │
  │  → Tooltip                 │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Tooltips Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Tooltips/Plain — 텍스트만:
  · 컴포넌트 이름: "Tooltips/Plain"
  · 최대 너비: 200dp, 최소 높이: 24dp
  · 배경: Inverse Surface, corner 4dp
  · 텍스트: 12sp, Inverse On-Surface
  · 수평 패딩: 8dp, 수직 패딩: 4dp
  · Elevation Level 1

  Tooltips/Rich — 제목 + 본문 + 버튼:
  · 컴포넌트 이름: "Tooltips/Rich"
  · 최대 너비: 320dp
  · 배경: Surface Container, corner 12dp
  · 제목: 14sp bold, On-Surface
  · 본문: 12sp, On-Surface-Variant
  · Action 버튼: TextButton, 하단
  · Elevation Level 2


  State 없음 — 단일 상태로만 표시

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Plain tooltip
  Tooltip(
    message: 'Add to favorites',
    child: IconButton(icon: Icon(Icons.favorite), onPressed: () {}),
  )

  // Rich tooltip
  Tooltip(
    richMessage: WidgetSpan(child: Column(children: [
      Text('Title', style: TextStyle(fontWeight: FontWeight.bold)),
      Text('Description text here'),
    ])),
    child: IconButton(icon: Icon(Icons.info), onPressed: () {}),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Plain Tooltip
Tooltip(
  message: '즐겨찾기에 추가',
  preferBelow: false,
  decoration: BoxDecoration(
    color: cs.inverseSurface,
    borderRadius: BorderRadius.circular(AppRadius.xs), // 8dp
  ),
  padding: EdgeInsets.symmetric(
    horizontal: AppSpacing.sm, // 4dp
    vertical: AppSpacing.xs,  // 2dp
  ),
  textStyle: Theme.of(context).textTheme.labelSmall?.copyWith(
    color: cs.onInverseSurface,
  ),
  child: IconButton(
    icon: Icon(Icons.favorite_border),
    onPressed: () {},
  ),
),

// Rich Tooltip
Tooltip(
  richMessage: TextSpan(children: [
    TextSpan(
      text: '더 알아보기\n',
      style: Theme.of(context).textTheme.labelMedium?.copyWith(
        color: cs.onSurface,
        fontWeight: FontWeight.bold,
      ),
    ),
    TextSpan(text: '자세한 설명이 여기 표시됩니다.'),
  ]),
  child: IconButton(icon: Icon(Icons.info_outline), onPressed: () {}),
)
```
