# Sliders

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/sliders/overview |
| Guidelines | https://m3.material.io/components/sliders/guidelines |
| Specs | https://m3.material.io/components/sliders/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Continuous slider | `Slider` |
| Discrete slider | `Slider` (divisions 파라미터) |
| Range slider | `RangeSlider` |
| Centered slider | `Slider` (커스텀 구현) |

## 언제 사용하나요?

- 볼륨, 밝기처럼 연속적인 범위에서 하나의 값을 선택할 때
- 가격 범위, 날짜 범위처럼 최솟값~최댓값을 함께 설정할 때
- 단계가 있는 이산(discrete) 값 선택이 필요할 때
- 정확한 숫자 입력 대신 직관적인 드래그 인터랙션이 필요할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 Slider, 충분한 터치 타겟(48dp 높이) |
| Tablet (medium) | 고정 너비, 최대 600dp |
| Desktop/Web (expanded) | 마우스 드래그 지원, 키보드 방향키 조작 지원 필수 |

## Variants

- **Continuous** — 부드럽게 연속 값 선택
- **Discrete** — 고정 단계로 이동
- **Range** — 시작/끝 두 값 선택
- **Centered** — 중간값에서 양방향으로 조절

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Sliders Guide" 프레임을 만들어주세요.

모든 내용은 이 "Sliders Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/sliders/overview

---

## 프레임 설정
- 이름: "Sliders Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Sliders"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · sliders"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/sliders/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 볼륨, 밝기처럼 연속적인 범위에서 하나의 값을 선택할 때
  · 가격 범위처럼 최솟값~최댓값을 함께 설정할 때
  · 정확한 숫자 입력 대신 직관적인 드래그 인터랙션이 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 세로 나열 (각 너비 320dp), gap 24px

  ┌─ Continuous (너비 320dp) ──────────────────────────┐
  │  track height: 4dp                                   │
  │  active track: Primary (왼쪽 60%)                   │
  │  inactive track: Secondary Container (오른쪽)       │
  │  thumb: 20dp 원, Primary, shadow dp1                │
  └─────────────────────────────────────────────────────┘

  ┌─ Discrete (너비 320dp) ────────────────────────────┐
  │  동일 구조 + tick marks                             │
  │  tick marks: 5개 점 (4×4dp, On-Surface)            │
  │  thumb: 20dp, Primary                               │
  └─────────────────────────────────────────────────────┘

  ┌─ Range (너비 320dp) ───────────────────────────────┐
  │  thumb 2개 (20dp, Primary)                         │
  │  두 thumb 사이: active track (Primary)              │
  │  바깥: inactive track (Secondary Container)        │
  └─────────────────────────────────────────────────────┘

  ┌─ Centered (너비 320dp) ────────────────────────────┐
  │  중앙에서 양쪽으로 active track 확장                │
  │  중앙 기준점: 1dp 세로선                            │
  └─────────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Continuous Slider를 크게 그리고 번호 레이블 연결:
  1. Track (active) — primary, 4dp 높이
  2. Track (inactive) — secondaryContainer, 4dp 높이
  3. Thumb — 20dp 원, primary
  4. Value label (선택) — thumb 위 말풍선 텍스트 (labelMedium)
  5. Tick marks (discrete) — 4dp 점, onSurface

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                   | 값                      | 토큰                              |
  |-----------------------|-------------------------|-----------------------------------|
  | Track height          | 4 dp                    | —                                 |
  | Thumb size            | 20 dp                   | —                                 |
  | Touch target          | 48 dp 높이              | —                                 |
  | Tick mark size        | 4 dp                    | —                                 |
  | Active track color    | primary                 | colorScheme.primary               |
  | Inactive track color  | secondaryContainer      | colorScheme.secondaryContainer    |
  | Thumb color           | primary                 | colorScheme.primary               |
  | Tick mark color       | onSurface               | colorScheme.onSurface             |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비, 48dp 터치 타겟   │
  │  → Slider                  │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  고정 너비, 최대 600dp      │
  │  → Slider                  │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  마우스/키보드 조작 지원     │
  │  → Slider                  │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Sliders Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  Sliders/Continuous — 연속 값 선택:
  · 컴포넌트 이름: "Sliders/Continuous"
  · 너비: 320dp, 터치 타겟 높이: 48dp
  · Active track: 4dp, Primary (왼쪽 60%)
  · Inactive track: 4dp, Secondary Container
  · Thumb: 20dp 원, Primary, Shadow Level 1

  Sliders/Discrete — 이산 단계 선택:
  · 컴포넌트 이름: "Sliders/Discrete"
  · 동일 구조, tick marks 포함
  · Tick marks: 4dp 점, On-Surface

  Sliders/Range — 범위 선택:
  · 컴포넌트 이름: "Sliders/Range"
  · Thumb 2개 (20dp, Primary)
  · 두 Thumb 사이: Active track (Primary)
  · 바깥: Inactive track (Secondary Container)


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Continuous
  Slider(value: _value, onChanged: (v) => setState(() => _value = v))

  // Discrete
  Slider(value: _value, divisions: 5, label: '${_value.round()}',
         onChanged: (v) => setState(() => _value = v))

  // Range
  RangeSlider(
    values: _rangeValues,
    onChanged: (v) => setState(() => _rangeValues = v),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

// Continuous Slider — 기본 (테마 자동 적용)
Slider(
  value: _value,
  min: 0,
  max: 100,
  onChanged: (v) => setState(() => _value = v),
)

// Discrete Slider — 고정 단계 (label 표시)
Slider(
  value: _value,
  min: 0,
  max: 100,
  divisions: 5,
  label: '${_value.round()}',
  onChanged: (v) => setState(() => _value = v),
)

// Range Slider — 최솟값/최댓값 동시 선택
RangeSlider(
  values: _rangeValues,
  min: 0,
  max: 100,
  divisions: 10,
  labels: RangeLabels(
    '${_rangeValues.start.round()}',
    '${_rangeValues.end.round()}',
  ),
  onChanged: (v) => setState(() => _rangeValues = v),
)

// onChangeStart / onChangeEnd — 드래그 시작/종료 콜백
Slider(
  value: _value,
  onChangeStart: (v) => print('드래그 시작: $v'),
  onChangeEnd: (v) => print('드래그 완료: $v'),
  onChanged: (v) => setState(() => _value = v),
)

// Disabled — onChanged: null
Slider(value: 0.5, onChanged: null)
```
