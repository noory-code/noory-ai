# Checkbox

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/checkbox/overview |
| Guidelines | https://m3.material.io/components/checkbox/guidelines |
| Specs | https://m3.material.io/components/checkbox/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Checkbox | `Checkbox` |
| With label | `CheckboxListTile` |

## 언제 사용하나요?

- 독립적인 복수 선택이 필요한 폼/설정 목록에 사용할 때
- On/Off 이진 상태를 나타낼 때 (Switch보다 목록 친화적)
- Tri-state (checked / unchecked / indeterminate) 표현이 필요할 때
- 여러 항목 중 하나 이상을 선택하는 체크리스트에 사용할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 CheckboxListTile, 터치 타겟 최소 48dp |
| Tablet (medium) | 동일, 2열 폼 레이아웃 적용 가능 |
| Desktop/Web (expanded) | 2~3열 폼 레이아웃, 호버 상태 지원 |

## Variants

- **Standard** — Checkbox 단독
- **With label** — CheckboxListTile (레이블 포함 복합 위젯)
- **Tri-state** — tristate: true 옵션 사용

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Checkbox Guide" 프레임을 만들어주세요.
모든 내용은 이 "Checkbox Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/checkbox/overview

---

## 프레임 설정
- 이름: "Checkbox Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Checkbox"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · checkbox"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/checkbox/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 복수 선택이 가능한 폼/설정 목록에 사용할 때
  · Tri-state (checked / unchecked / indeterminate) 표현이 필요할 때
  · 여러 항목 중 하나 이상을 선택하는 체크리스트에 사용할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 가로 나란히 배치, gap 24px

  ┌─ Unchecked ────────────────────────┐
  │  18×18dp 정사각형                   │
  │  border: 2dp, Outline (Outline)    │
  │  배경: transparent                  │
  │  corner: 2dp                       │
  └────────────────────────────────────┘

  ┌─ Checked ──────────────────────────┐
  │  18×18dp 정사각형                   │
  │  배경: Primary (Primary)            │
  │  체크 아이콘: white, 12dp           │
  │  corner: 2dp                       │
  └────────────────────────────────────┘

  ┌─ Indeterminate ────────────────────┐
  │  18×18dp 정사각형                   │
  │  배경: Primary (Primary)            │
  │  대시 아이콘: white, 12dp            │
  │  corner: 2dp                       │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- CheckboxListTile을 크게 그리고 번호 레이블 연결:
  1. Checkbox container — 18×18dp, corner 2dp
  2. State icon — check / dash / empty
  3. Touch target — 48×48dp (접근성 최소)
  4. Label — 16sp, On-Surface (ListTile에서 제공)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | 값              |
  |------------------|-----------------|
  | Size             | 18 × 18 dp      |
  | Touch target     | 48 × 48 dp      |
  | Corner radius    | 2 dp            |
  | Border width     | 2 dp            |
  | Color (checked)  | Primary         |
  | Color (unchecked)| Outline         |
  | Icon color       | On-Primary      |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비 CheckboxListTile  │
  │  → CheckboxListTile        │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  2열 폼 레이아웃 가능        │
  │  → CheckboxListTile        │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  2~3열 폼, 호버 상태 지원    │
  │  → Checkbox + label        │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Checkbox Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  Checkbox/Unchecked — 미선택:
  · 컴포넌트 이름: "Checkbox/Unchecked"
  · 박스: 18×18dp, corner: 2dp
  · 배경: 투명, 테두리: On-Surface-Variant 2dp
  · 터치 타겟: 48×48dp

  Checkbox/Checked — 선택:
  · 컴포넌트 이름: "Checkbox/Checked"
  · 박스: 18×18dp, corner: 2dp
  · 배경: Primary, 체크 아이콘: On-Primary 12dp
  · 터치 타겟: 48×48dp

  Checkbox/Indeterminate — 중간 상태:
  · 컴포넌트 이름: "Checkbox/Indeterminate"
  · 박스: 18×18dp, corner: 2dp
  · 배경: Primary, 대시 아이콘: On-Primary 12dp
  · 터치 타겟: 48×48dp


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Standard
  Checkbox(value: isChecked, onChanged: (v) => setState(() => isChecked = v!))

  // With label
  CheckboxListTile(
    title: Text('Option 1'),
    value: isChecked,
    onChanged: (v) => setState(() => isChecked = v!),
  )

  // Tri-state
  Checkbox(tristate: true, value: null, onChanged: (v) {})

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;
final tt = Theme.of(context).textTheme;

// Standard Checkbox
Checkbox(
  value: isChecked,
  activeColor: cs.primary,
  onChanged: (v) => setState(() => isChecked = v!),
)

// With label — CheckboxListTile (전체 너비 터치 타겟 포함)
CheckboxListTile(
  title: Text('알림 수신 동의', style: tt.bodyMedium),
  subtitle: Text('마케팅 정보를 받습니다', style: tt.bodySmall?.copyWith(
    color: cs.onSurfaceVariant,
  )),
  value: isChecked,
  activeColor: cs.primary,
  contentPadding: EdgeInsets.symmetric(horizontal: AppSpacing.base), // 12dp
  onChanged: (v) => setState(() => isChecked = v!),
)

// Tri-state Checkbox
Checkbox(
  tristate: true,
  value: null, // null = indeterminate
  activeColor: cs.primary,
  onChanged: (v) {},
)
```
