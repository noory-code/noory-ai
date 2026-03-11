# Radio Button

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/radio-button/overview |
| Guidelines | https://m3.material.io/components/radio-button/guidelines |
| Specs | https://m3.material.io/components/radio-button/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Radio | `Radio<T>` |
| With label | `RadioListTile<T>` |

## 언제 사용하나요?

- 여러 옵션 중 반드시 하나만 선택해야 하는 배타적 선택에 사용할 때
- 옵션이 2~5개로 적고 모든 선택지를 한눈에 보여줄 때
- 결제 방법, 배송 방식처럼 명확히 하나를 골라야 하는 설정
- 선택지가 6개 이상이면 DropdownMenu로 대체할 것

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 세로 목록, 전체 너비 RadioListTile |
| Tablet (medium) | 2열 배치 가능 |
| Desktop/Web (expanded) | 인라인 가로 배치 또는 2~3열 폼 레이아웃, 호버 지원 |

## Variants

- **Standard** — Radio 단독
- **With label** — RadioListTile (레이블 포함)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Radio Button Guide" 프레임을 만들어주세요.
모든 내용은 이 "Radio Button Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/radio-button/overview

---

## 프레임 설정
- 이름: "Radio Button Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Radio Button"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · radio-button"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/radio-button/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 여러 옵션 중 반드시 하나만 선택해야 하는 배타적 선택에 사용할 때
  · 옵션이 2~5개로 적고 모든 선택지를 한눈에 보여줄 때
  · 선택지가 6개 이상이면 DropdownMenu로 대체할 것

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- 2개 상태를 세로로 나열, gap 16px

  ┌─ Unselected ─────────────────────┐
  │  20×20dp 원형                     │
  │  border: 2dp, Outline (Outline)  │
  │  내부: 비어 있음                  │
  │  touch target: 48×48dp           │
  └───────────────────────────────────┘

  ┌─ Selected ───────────────────────┐
  │  20×20dp 원형                     │
  │  border: 2dp, Primary (Primary)  │
  │  내부: 10dp 채워진 원             │
  │  내부 색상: Primary (Primary)    │
  └───────────────────────────────────┘

  RadioListTile 예시 (너비 320dp):
  ┌─────────────────────────────────────┐
  │  ○  Option 1  (16sp, On-Surface)      │
  │  ●  Option 2  (16sp, On-Surface)      │
  │  ○  Option 3  (16sp, On-Surface)      │
  └─────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Selected Radio를 크게 그리고 번호 레이블 연결:
  1. Outer ring — 20dp 원, 2dp border (selected: primary / unselected: onSurfaceVariant)
  2. Inner fill — 10dp 원, primary
  3. Touch target — 48×48dp (접근성 최소)
  4. State layer — hover/focus ripple (primary 기반)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                   | 값                   | 토큰                          |
  |-----------------------|----------------------|-------------------------------|
  | Outer circle          | 20 dp                | —                             |
  | Inner circle          | 10 dp                | —                             |
  | Border width          | 2 dp                 | —                             |
  | Touch target          | 48 × 48 dp           | —                             |
  | Selected color        | primary              | colorScheme.primary           |
  | Unselected color      | onSurfaceVariant     | colorScheme.onSurfaceVariant  |
  | Label TextStyle       | bodyLarge            | textTheme.bodyLarge           |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  세로 목록, 전체 너비       │
  │  → RadioListTile           │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  2열 배치 가능              │
  │  → RadioListTile           │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  인라인 가로 배치, 호버 지원 │
  │  → Radio + label           │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Radio Button Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  RadioButton/Unselected — 미선택 상태:
  · 컴포넌트 이름: "RadioButton/Unselected"
  · 외부 원: 20dp, 테두리 2dp, On-Surface-Variant
  · 내부: 비어 있음
  · 터치 타겟: 48×48dp

  RadioButton/Selected — 선택 상태:
  · 컴포넌트 이름: "RadioButton/Selected"
  · 외부 원: 20dp, 테두리 2dp, Primary
  · 내부 원: 10dp, Primary 채움
  · 터치 타겟: 48×48dp


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Standard
  Radio<String>(
    value: 'option1',
    groupValue: _selected,
    onChanged: (v) => setState(() => _selected = v!),
  )

  // With label
  RadioListTile<String>(
    title: Text('Option 1'),
    value: 'option1',
    groupValue: _selected,
    onChanged: (v) => setState(() => _selected = v!),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// RadioListTile group — 기본 (테마 자동 적용)
Column(
  children: [
    RadioListTile<String>(
      title: const Text('Option 1'),
      value: 'option1',
      groupValue: _selected,
      onChanged: (v) => setState(() => _selected = v!),
    ),
    RadioListTile<String>(
      title: const Text('Option 2'),
      subtitle: const Text('설명 텍스트'), // 보조 설명
      value: 'option2',
      groupValue: _selected,
      onChanged: (v) => setState(() => _selected = v!),
    ),
  ],
)

// Radio 단독 사용 (레이블 직접 배치)
Row(
  children: [
    Radio<String>(
      value: 'option1',
      groupValue: _selected,
      onChanged: (v) => setState(() => _selected = v!),
    ),
    const Text('Option 1'),
  ],
)

// Disabled — onChanged: null
RadioListTile<String>(
  title: const Text('Disabled Option'),
  value: 'disabled',
  groupValue: _selected,
  onChanged: null,  // 비활성
)
```
